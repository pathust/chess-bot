import time
from math import ceil, inf
from typing import Optional, Callable
import chess
from move_ordering import MoveOrdering
from repetition_table import RepetitionTable
from transposition_table import TranspositionTable
from evaluation.evaluation import Evaluation

class Searcher:
    # Constants
    transposition_table_size_mb = 64
    max_extensions = 16

    immediate_mate_score = 100000
    positive_infinity = 9999999
    negative_infinity = -positive_infinity

    def __init__(self, board: chess.Board):
        self.board = board
        self.best_move_this_iteration = chess.Move.null()
        self.best_eval_this_iteration = 0
        self.best_move = chess.Move.null()
        self.best_eval = 0
        self.has_searched_at_least_one_move = False
        self.search_cancelled = False
        self.current_depth = 0
        self.debug_info = ""

        # References
        self.transposition_table = TranspositionTable(board, self.transposition_table_size_mb)
        self.repetition_table = RepetitionTable()
        self.evaluation = Evaluation()

        # Initialization
        self.run_depth_1_search()

    def run_depth_1_search(self):
        self.search(1, 0, self.negative_infinity, self.positive_infinity)

    def start_search(self, on_search_complete: Optional[Callable] = None):
        self.best_eval_this_iteration = self.best_eval = 0
        self.best_move_this_iteration = self.best_move = chess.Move.null()

        self.is_playing_white = self.board.turn == chess.WHITE
        self.repetition_table.init(self.board)

        self.current_depth = 0
        self.debug_info = "Starting search with FEN " + self.board.fen()
        self.search_cancelled = False

        self.search_diagnostics = SearchDiagnostics()
        self.search_iteration_timer = time.time()
        self.search_total_timer = time.time()

        self.run_iterative_deepening_search()

        if self.best_move.is_null:
            self.best_move = list(self.board.legal_moves)[0]  # Pick any legal move if no best move found

        if on_search_complete:
            on_search_complete(self.best_move)

        self.search_cancelled = False

    def run_iterative_deepening_search(self):
        for search_depth in range(1, 257):
            self.has_searched_at_least_one_move = False
            self.debug_info += f"\nStarting Iteration: {search_depth}"
            self.search_iteration_timer = time.time()

            self.search(search_depth, 0, self.negative_infinity, self.positive_infinity)

            if self.search_cancelled:
                if self.has_searched_at_least_one_move:
                    self.best_move = self.best_move_this_iteration
                    self.best_eval = self.best_eval_this_iteration
                    self.search_diagnostics.move = self.format_move(self.best_move)
                    self.search_diagnostics.eval = self.best_eval
                    self.search_diagnostics.move_is_from_partial_search = True
                    self.debug_info += f"\nUsing partial search result: {self.format_move(self.best_move)} Eval: {self.best_eval}"
                self.debug_info += "\nSearch aborted"
                break
            else:
                self.current_depth = search_depth
                self.best_move = self.best_move_this_iteration
                self.best_eval = self.best_eval_this_iteration

                self.debug_info += f"\nIteration result: {self.format_move(self.best_move)} Eval: {self.best_eval}"

                self.best_eval_this_iteration = -inf
                self.best_move_this_iteration = chess.Move.null()

                # Update diagnostics
                self.search_diagnostics.num_completed_iterations = search_depth
                self.search_diagnostics.move = self.format_move(self.best_move)
                self.search_diagnostics.eval = self.best_eval

                if self.is_mate_score(self.best_eval):
                    self.debug_info += f" Mate in ply: {self.num_ply_to_mate_from_score(self.best_eval)}"

                # Exit search if found a mate within search depth.
                if self.is_mate_score(self.best_eval) and self.num_ply_to_mate_from_score(self.best_eval) <= search_depth:
                    self.debug_info += "\nExiting search due to mate found within search depth"
                    break

    def search(self, ply_remaining, ply_from_root, alpha, beta, num_extensions=0, prev_move=None, prev_was_capture=False):
        if self.search_cancelled:
            return 0

        if ply_from_root > 0:
            if self.board.is_fifty_moves() >= 100 or self.repetition_table.contains(self.board.zobrist_key):
                return 0

            alpha = max(alpha, -self.immediate_mate_score + ply_from_root)
            beta = min(beta, self.immediate_mate_score - ply_from_root)
            if alpha >= beta:
                return alpha

        tt_val = self.transposition_table.lookup_evaluation(ply_remaining, ply_from_root, alpha, beta)
        if tt_val != TranspositionTable.lookup_failed:
            if ply_from_root == 0:
                self.best_move_this_iteration = self.transposition_table.try_get_stored_move()
                self.best_eval_this_iteration = self.transposition_table.entries[self.transposition_table.index].value
            return tt_val

        if ply_remaining == 0:
            return self.quiescence_search(alpha, beta)

        moves = list(self.board.legal_moves)
        prev_best_move = self.best_move if ply_from_root == 0 else self.transposition_table.try_get_stored_move()

        # Sort moves
        moves.sort(key=lambda move: self.evaluate_move(move, alpha, beta))

        if len(moves) == 0:
            if self.board.is_check():
                mate_score = self.immediate_mate_score - ply_from_root
                return -mate_score
            else:
                return 0

        if ply_from_root > 0:
            was_pawn_move = self.board.piece_type(prev_move.target_square) == chess.PAWN
            self.repetition_table.push(self.board.zobrist_key, prev_was_capture or was_pawn_move)

        evaluation_bound = TranspositionTable.upper_bound
        best_move_in_this_position = chess.Move.null()

        for i, move in enumerate(moves):
            captured_piece_type = self.board.piece_type(move.target_square)
            is_capture = captured_piece_type != chess.Piece.NONE
            self.board.push(move)

            extension = 0
            if num_extensions < self.max_extensions:
                moved_piece_type = self.board.piece_type(move.target_square)
                target_rank = chess.square_rank(move.target_square)
                if self.board.is_check():
                    extension = 1
                elif moved_piece_type == chess.PAWN and (target_rank == 1 or target_rank == 6):
                    extension = 1

            needs_full_search = True
            eval = 0
            if extension == 0 and ply_remaining >= 3 and i >= 3 and not is_capture:
                reduce_depth = 1
                eval = -self.search(ply_remaining - 1 - reduce_depth, ply_from_root + 1, -alpha - 1, -alpha, num_extensions, move, is_capture)
                needs_full_search = eval > alpha

            if needs_full_search:
                eval = -self.search(ply_remaining - 1 + extension, ply_from_root + 1, -beta, -alpha, num_extensions + extension, move, is_capture)

            self.board.pop()

            if self.search_cancelled:
                return 0

            if eval >= beta:
                self.transposition_table.store_evaluation(ply_remaining, ply_from_root, beta, TranspositionTable.lower_bound, move)
                if not is_capture:
                    if ply_from_root < MoveOrdering.max_killer_move_ply:
                        self.move_orderer.killer_moves[ply_from_root].add(move)
                    history_score = ply_remaining * ply_remaining
                    self.move_orderer.history[self.board.move_colour_index, move.from_square, move.target_square] += history_score
                if ply_from_root > 0:
                    self.repetition_table.try_pop()

                self.search_diagnostics.num_cutoffs += 1
                return beta

            if eval > alpha:
                evaluation_bound = TranspositionTable.exact
                best_move_in_this_position = move
                alpha = eval
                if ply_from_root == 0:
                    self.best_move_this_iteration = move
                    self.best_eval_this_iteration = eval
                    self.has_searched_at_least_one_move = True

        if ply_from_root > 0:
            self.repetition_table.try_pop()

        self.transposition_table.store_evaluation(ply_remaining, ply_from_root, alpha, evaluation_bound, best_move_in_this_position)

        return alpha

    def quiescence_search(self, alpha, beta):
        if self.search_cancelled:
            return 0

        eval = self.evaluation.evaluate(self.board)
        self.search_diagnostics.num_positions_evaluated += 1
        if eval >= beta:
            self.search_diagnostics.num_cutoffs += 1
            return beta
        if eval > alpha:
            alpha = eval

        moves = list(self.board.legal_moves)
        for move in moves:
            self.board.push(move)
            eval = -self.quiescence_search(-beta, -alpha)
            self.board.pop()

            if eval >= beta:
                self.search_diagnostics.num_cutoffs += 1
                return beta
            if eval > alpha:
                alpha = eval

        return alpha

    def is_mate_score(self, score):
        return abs(score) > self.immediate_mate_score

    def num_ply_to_mate_from_score(self, score):
        return self.immediate_mate_score - abs(score)

    def announce_mate(self):
        if self.is_mate_score(self.best_eval_this_iteration):
            num_ply_to_mate = self.num_ply_to_mate_from_score(self.best_eval_this_iteration)
            num_moves_to_mate = ceil(num_ply_to_mate / 2)
            side_with_mate = "Black" if self.best_eval_this_iteration * (1 if self.board.turn == chess.WHITE else -1) < 0 else "White"
            return f"{side_with_mate} can mate in {num_moves_to_mate} move{('s' if num_moves_to_mate > 1 else '')}"
        return "No mate found"

    def clear_for_new_position(self):
        self.transposition_table.clear()
        self.move_orderer.clear_killers()

    def get_transposition_table(self):
        return self.transposition_table

class SearchDiagnostics:
    def __init__(self):
        self.num_completed_iterations = 0
        self.num_positions_evaluated = 0
        self.num_cutoffs = 0
        self.move_val = ""
        self.move = ""
        self.eval = 0
        self.move_is_from_partial_search = False
        self.num_q_checks = 0
        self.num_q_mates = 0
        self.is_book = False
        self.max_extension_reached_in_search = 0