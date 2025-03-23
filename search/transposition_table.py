import chess
import math
from typing import Optional, Tuple

class TranspositionTable:
    lookup_failed = -1
    exact = 0
    lower_bound = 1
    upper_bound = 2

    def __init__(self, board: chess.Board, size_mb: int):
        self.board = board
        self.enabled = True

        # Determine table size based on desired size in MB
        tt_entry_size_bytes = 64  # Size of each entry (Entry structure) in bytes
        desired_table_size_in_bytes = size_mb * 1024 * 1024
        num_entries = desired_table_size_in_bytes // tt_entry_size_bytes

        self.count = num_entries
        self.entries = {}

    def clear(self):
        self.entries.clear()

    @property
    def index(self) -> int:
        zobrist_key = self.board.zobrist_hash()
        return zobrist_key % self.count

    def try_get_stored_move(self) -> Optional[chess.Move]:
        entry = self.entries.get(self.index)
        if entry:
            return entry.move
        return None

    def lookup_evaluation(self, depth: int, ply_from_root: int, alpha: int, beta: int) -> int:
        if not self.enabled:
            return self.lookup_failed

        entry = self.entries.get(self.index)
        if entry:
            if entry.key == self.board.zobrist_hash():
                if entry.depth >= depth:
                    corrected_score = self.correct_retrieved_mate_score(entry.value, ply_from_root)
                    if entry.node_type == self.exact:
                        return corrected_score
                    elif entry.node_type == self.upper_bound and corrected_score <= alpha:
                        return corrected_score
                    elif entry.node_type == self.lower_bound and corrected_score >= beta:
                        return corrected_score
        return self.lookup_failed

    def store_evaluation(self, depth: int, num_ply_searched: int, eval: int, eval_type: int, move: chess.Move):
        if not self.enabled:
            return

        entry = Entry(self.board.zobrist_hash(), self.correct_mate_score_for_storage(eval, num_ply_searched), depth, eval_type, move)
        self.entries[self.index] = entry

    def correct_mate_score_for_storage(self, score: int, num_ply_searched: int) -> int:
        if self.is_mate_score(score):
            sign = math.copysign(1, score)
            return int((abs(score) + num_ply_searched) * sign)
        return score

    def correct_retrieved_mate_score(self, score: int, num_ply_searched: int) -> int:
        if self.is_mate_score(score):
            sign = math.copysign(1, score)
            return int((abs(score) - num_ply_searched) * sign)
        return score

    def is_mate_score(self, score: int) -> bool:
        return abs(score) >= 10000


class Entry:
    def __init__(self, key: int, value: int, depth: int, node_type: int, move: chess.Move):
        self.key = key
        self.value = value
        self.depth = depth
        self.node_type = node_type
        self.move = move

    @staticmethod
    def get_size() -> int:
        # Assuming that the size of the Entry is similar to the original in C#
        return 64  # Size of Entry in bytes


# Example usage:

# Initialize a chess board
board = chess.Board()

# Create a transposition table with 16MB size
tt = TranspositionTable(board, 16)

# Example of storing an evaluation
move = chess.Move.from_uci("e2e4")
tt.store_evaluation(depth=5, num_ply_searched=10, eval=500, eval_type=TranspositionTable.exact, move=move)

# Example of looking up an evaluation
eval_result = tt.lookup_evaluation(depth=5, ply_from_root=2, alpha=-1000, beta=1000)
print(f"Evaluation: {eval_result}")

# Example of retrieving the stored move
stored_move = tt.try_get_stored_move()
if stored_move:
    print(f"Stored Move: {stored_move}")
else:
    print("No stored move")
