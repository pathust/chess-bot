import chess
import math
from typing import List, Tuple
from evaluation.evaluation import Evaluation
from evaluation.piece_square_table import PieceSquareTable
class MoveOrdering:
    max_move_count = 218
    square_controlled_by_opponent_pawn_penalty = 350
    captured_piece_value_multiplier = 100

    max_killer_move_ply = 32
    million = 1000000
    hash_move_score = 100 * million
    winning_capture_bias = 8 * million
    promote_bias = 6 * million
    killer_bias = 4 * million
    losing_capture_bias = 2 * million
    regular_bias = 0

    def __init__(self, transposition_table):
        self.move_scores = [0] * self.max_move_count
        self.transposition_table = transposition_table
        self.invalid_move = chess.Move.null()
        self.killer_moves = [Killers() for _ in range(self.max_killer_move_ply)]
        self.history = [[[0] * 64 for _ in range(64)] for _ in range(2)]

    def clear_history(self):
        self.history = [[[0] * 64 for _ in range(64)] for _ in range(2)]

    def clear_killers(self):
        self.killer_moves = [Killers() for _ in range(self.max_killer_move_ply)]

    def clear(self):
        self.clear_killers()
        self.clear_history()

    def order_moves(self, hash_move: chess.Move, board: chess.Board, moves: List[chess.Move], opp_attacks: int, opp_pawn_attacks: int, in_qsearch: bool, ply: int):
        opp_pieces = (board.enemy_diagonal_sliders | board.enemy_orthogonal_sliders | board.piece_bitboards[chess.PieceType.KNIGHT])
        pawn_attacks = board.white_pawn_attacks if board.turn == chess.WHITE else board.black_pawn_attacks

        for i, move in enumerate(moves):
            if move == hash_move:
                self.move_scores[i] = self.hash_move_score
                continue

            score = 0
            start_square = move.from_square
            target_square = move.to_square

            move_piece = board.piece_at(start_square)
            move_piece_type = move_piece.piece_type if move_piece else None
            capture_piece_type = board.piece_at(target_square).piece_type if board.piece_at(target_square) else None
            is_capture = capture_piece_type is not None
            flag = move.promotion
            piece_value = self.get_piece_value(move_piece_type)

            if is_capture:
                capture_material_delta = self.get_piece_value(capture_piece_type) - piece_value
                opponent_can_recapture = (opp_pawn_attacks | opp_attacks) & (1 << target_square)

                if opponent_can_recapture:
                    score += (self.winning_capture_bias if capture_material_delta >= 0 else self.losing_capture_bias) + capture_material_delta
                else:
                    score += self.winning_capture_bias + capture_material_delta

            if move_piece_type == chess.PAWN:
                if flag == chess.QUEEN and not is_capture:
                    score += self.promote_bias
            else:
                to_score = PieceSquareTable.tables[move_piece] = target_square
                from_score = PieceSquareTable.tables[move_piece] = start_square
                score += to_score - from_score

                if (opp_pawn_attacks & (1 << target_square)):
                    score -= 50
                elif (opp_attacks & (1 << target_square)):
                    score -= 25

            if not is_capture:
                is_killer = not in_qsearch and ply < self.max_killer_move_ply and self.killer_moves[ply].match(move)
                score += self.killer_bias if is_killer else self.regular_bias
                score += self.history[board.turn][start_square][target_square]

            self.move_scores[i] = score

        self.quicksort(moves, self.move_scores, 0, len(moves) - 1)

    def get_piece_value(self, piece_type: int) -> int:
        piece_values = {
            chess.QUEEN: Evaluation.queen_value,
            chess.ROOK: Evaluation.rook_value,
            chess.KNIGHT: Evaluation.knight_value,
            chess.BISHOP: Evaluation.bishop_value,
            chess.PAWN: Evaluation.pawn_value,
        }
        return piece_values.get(piece_type, 0)

    def get_score(self, index: int) -> str:
        score = self.move_scores[index]

        score_types = [self.hash_move_score, self.winning_capture_bias, self.losing_capture_bias, self.promote_bias, self.killer_bias, self.regular_bias]
        type_names = ["Hash Move", "Good Capture", "Bad Capture", "Promote", "Killer Move", "Regular"]
        closest = float('inf')
        type_name = ""

        for i, score_type in enumerate(score_types):
            delta = abs(score - score_type)
            if delta < closest:
                closest = delta
                type_name = type_names[i]

        return f"{score} ({type_name})"

    def quicksort(self, values: List[chess.Move], scores: List[int], low: int, high: int):
        """Perform quicksort on the moves based on their scores."""
        if low < high:
            pivot_index = self.partition(values, scores, low, high)
            self.quicksort(values, scores, low, pivot_index - 1)
            self.quicksort(values, scores, pivot_index + 1, high)

    def partition(self, values: List[chess.Move], scores: List[int], low: int, high: int) -> int:
        pivot_score = scores[high]
        i = low - 1

        for j in range(low, high):
            if scores[j] > pivot_score:
                i += 1
                values[i], values[j] = values[j], values[i]
                scores[i], scores[j] = scores[j], scores[i]

        values[i + 1], values[high] = values[high], values[i + 1]
        scores[i + 1], scores[high] = scores[high], scores[i + 1]

        return i + 1


class Killers:
    def __init__(self):
        self.move_a = chess.Move.null()
        self.move_b = chess.Move.null()

    def add(self, move: chess.Move):
        if move != self.move_a:
            self.move_b = self.move_a
            self.move_a = move

    def match(self, move: chess.Move) -> bool:
        return move == self.move_a or move == self.move_b
