import time
from math import ceil
import chess
from search.move_ordering import MoveOrdering
from search.repetition_table import RepetitionTable
from search.transposition_table import TranspositionTable
from evaluation.evaluation import Evaluation
from nnue_evaluation import NNUEEvaluation
class Searcher:
    # Constants
    transposition_table_size_mb = 64
    max_extensions = 16

    immediate_mate_score = 100000
    positive_infinity = 9999999
    negative_infinity = -positive_infinity
    max_depth:int = 5
    expansion_ratio = [0,0,5.918685130964094,2.31559020535454,2.928389878801775,2.977312373936534,2.206598636221307,1.49191046769435,1.0995220641809031,1.0128484938632873,1.086859457633767,2,2,2,2,2,2]

    def __init__(self, board: chess.Board, use_nnue=False):
        self.board = board
        self.current_depth = 0
        self.best_move = chess.Move.null()
        self.best_eval = 0
        self.is_playing_white = False
        self.best_move_this_iteration = chess.Move.null()
        self.best_eval_this_iteration = 0
        self.has_searched_at_least_one_move = False
        self.search_cancelled = False
        self.debug_info = ""
        self.search_iteration_timer = time.time()
        self.search_total_timer = time.time()
        self.time_limit = Searcher.positive_infinity

        #for time management
        self.use_time_manager = False #defaul 
        self.adjust_time_ratio = 1

        self.counter_searched_nood = 0
        self.last_ply_zero = 0
        self.last_best_move = chess.Move.null()
        self.best_move_searched_node = 0

        self.history_best_scores = [0] * 20 # evel of best move per depth
        self.history_best_node = [chess.Move.null()] * 20 #best move per depth
        self.panic_eval = 150 #if eval decrease more than this in a ply, change to panic mode
        # Initialize search_diagnostics
        self.search_diagnostics = SearchDiagnostics()

        # References and initialization
        self.evaluation = NNUEEvaluation() if use_nnue else Evaluation()
        self.transposition_table = TranspositionTable(board, self.transposition_table_size_mb)
        self.move_orderer = MoveOrdering(self.transposition_table)
        self.repetition_table = RepetitionTable()

        # Run a depth 1 search for JIT warm-up
        self.search(1, 0, self.negative_infinity, self.positive_infinity)

    def start_search(self,time_limit = positive_infinity ,on_search_complete=None):
        # Initialize search
        self.best_eval_this_iteration = self.best_eval = 0
        self.best_move_this_iteration = self.best_move = chess.Move.null()

        self.is_playing_white = self.board.turn == chess.WHITE

        self.move_orderer.clear_history()
        self.repetition_table.init(self.board)

        self.time_limit=time_limit
        # Initialize debug info
        self.current_depth = 0
        self.debug_info = "Starting search with FEN " + self.board.fen()
        self.search_cancelled = False
        self.search_diagnostics = SearchDiagnostics()
        self.search_iteration_timer = time.time()
        self.search_total_timer = time.time()

        #for time management
        if self.use_time_manager:
            self.adjust_time_ratio=1
            self.history_best_scores = [0] * 20 # evel of best move per depth
            self.history_best_node = [chess.Move.null()] * 20 #best move per depth

        print('initialized')
        # Search
        self.run_iterative_deepening_search()
        print('finished search')
        # Finish up
        print(self.best_move)
        if self.best_move.null():
            # In the unlikely event no best move is found, take any legal move
            moves = list(self.board.legal_moves)
            if moves:
                self.best_move = moves[0]

        if on_search_complete:
            on_search_complete(self.best_move)

        self.search_cancelled = False

    def run_iterative_deepening_search(self):
        for search_depth in range(1, self.max_depth+1): 
            if self.use_time_manager:
                elapsed_time_ms = (time.time() - self.search_iteration_timer) * 1000

                if(elapsed_time_ms  > self.time_limit * 0.3):
                    self.adjust_time_ratio += self.adjust_time()
                    elapsed_time_ms *= self.adjust_time_ratio
                if(elapsed_time_ms  > self.time_limit * Searcher.expansion_ratio[search_depth]):
                    break #stop cause not enough time

                self.counter_searched_nood = 0
                self.last_ply_zero = 0
                self.last_best_move = chess.Move.null()
                self.best_move_searched_node = 0

            print(search_depth)
            self.has_searched_at_least_one_move = False
            self.debug_info += f"\nStarting Iteration: {search_depth}"
            self.search_iteration_timer = time.time()


            self.search(search_depth, 0, self.negative_infinity, self.positive_infinity)
            self.history_best_node[search_depth] = self.best_move_this_iteration
            self.history_best_scores[search_depth] = self.best_eval_this_iteration
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
                if self.is_mate_score(self.best_eval):
                    self.debug_info += f" Mate in ply: {self.num_ply_to_mate_from_score(self.best_eval)}"
                print(f"\nIteration result: {self.format_move(self.best_move)} Eval: {self.best_eval}")
                self.best_eval_this_iteration = -float('inf')
                self.best_move_this_iteration = chess.Move.null()

                # Update diagnostics
                self.search_diagnostics.num_completed_iterations = search_depth
                self.search_diagnostics.move = self.format_move(self.best_move)
                self.search_diagnostics.eval = self.best_eval

                # Exit search if found a mate within search depth
                if (self.is_mate_score(self.best_eval) and
                    self.num_ply_to_mate_from_score(self.best_eval) <= search_depth
                ):
                    self.debug_info += "\nExiting search due to mate found within search depth"
                    break

    def search(self,
               ply_remaining,
               ply_from_root,
               alpha,
               beta,
               num_extensions=0,
               prev_move=None,
               prev_was_capture=False
    ):
        if self.search_cancelled:
            return 0
        self.increment_node()
        if(ply_from_root == 0):

            if(self.last_best_move !=self.best_eval_this_iteration ): # if best move change, defaule: nullmove != nullmove
                self.best_move_searched_node = self.get_node_searched_branch()
            self.update_searched_branch()

        if ply_from_root > 0:
            # Detect draw by three-fold repetition or fifty move rule
            if (
                self.board.is_fifty_moves() or
                self.repetition_table.contains(chess.polyglot.zobrist_hash(self.board))
            ):
                return 0

            # Skip positions where we already know a shorter mating sequence
            alpha = max(alpha, -self.immediate_mate_score + ply_from_root)
            beta = min(beta, self.immediate_mate_score - ply_from_root)
            if alpha >= beta:
                return alpha

        # Check transposition table
        tt_val = self.transposition_table.lookup_evaluation(
            ply_remaining,
            ply_from_root,
            alpha,
            beta
        )
        if tt_val != TranspositionTable.lookup_failed:
            if ply_from_root == 0:
                self.best_move_this_iteration = self.transposition_table.try_get_stored_move()
                entry = self.transposition_table.entries.get(self.transposition_table.index)
                if entry:
                    self.best_eval_this_iteration = entry.value
                else:
                    self.best_eval_this_iteration = 0
            return tt_val

        # If at max depth, perform quiescence search
        if ply_remaining == 0:
            eval_score = self.quiescence_search(alpha, beta)
            return eval_score

        # Generate and order moves
        legal_moves = list(self.board.legal_moves)
        prev_best_move = (
            self.best_move
            if ply_from_root == 0 else
            self.transposition_table.try_get_stored_move()
        )

        # Order moves
        opponent_attack_map = chess.SquareSet()
        opponent_pawn_attack_map = chess.SquareSet()
        self.move_orderer.order_moves(
            prev_best_move,
            self.board, legal_moves,
            opponent_attack_map,
            opponent_pawn_attack_map,
            False,
            ply_from_root
        )

        # Check for checkmate or stalemate
        if not legal_moves:
            if self.board.is_check():
                # Checkmate
                mate_score = self.immediate_mate_score - ply_from_root
                return -mate_score
            else:
                # Stalemate
                return 0

        if ply_from_root > 0 and prev_move:
            # Update repetition table
            was_pawn_move = (
                self.board.piece_at(prev_move.to_square) and
                self.board.piece_at(prev_move.to_square).piece_type == chess.PAWN
            )
            self.repetition_table.push(
                chess.polyglot.zobrist_hash(self.board),
                prev_was_capture or was_pawn_move
            )

        evaluation_bound = TranspositionTable.upper_bound
        best_move_in_this_position = chess.Move.null()

        for i, move in enumerate(legal_moves):
            # Get move information
            captured_piece = self.board.piece_at(move.to_square)
            is_capture = captured_piece is not None

            # Make the move
            self.board.push(move)

            # Check for extensions
            extension = 0
            if num_extensions < self.max_extensions:
                moved_piece = self.board.piece_at(move.to_square)
                if moved_piece:
                    target_rank = chess.square_rank(move.to_square)
                    if self.board.is_check():
                        extension = 1
                    elif (moved_piece.piece_type == chess.PAWN and
                          target_rank in [1, 6]
                    ):
                        extension = 1

            # Decide whether to do a full search or reduced depth search
            needs_full_search = True
            eval_score = 0

            # Reduce depth for later moves in the move list
            if extension == 0 and ply_remaining >= 3 and i >= 3 and not is_capture:
                reduce_depth = 1
                eval_score = -self.search(
                    ply_remaining - 1 - reduce_depth,
                    ply_from_root + 1,
                    -alpha - 1,
                    -alpha,
                    num_extensions,
                    move,
                    is_capture
                )
                needs_full_search = eval_score > alpha

            # Perform full-depth search if needed
            if needs_full_search:
                eval_score = -self.search(
                    ply_remaining - 1 + extension,
                    ply_from_root + 1,
                    -beta,
                    -alpha,
                    num_extensions + extension,
                    move,
                    is_capture
                )

            # Unmake move
            self.board.pop()

            if self.search_cancelled:
                return 0

            # Beta cutoff (move was too good)
            if eval_score >= beta:
                # Store in transposition table
                self.transposition_table.store_evaluation(
                    ply_remaining,
                    ply_from_root,
                    beta,
                    TranspositionTable.lower_bound,
                    move
                )

                # Update killer moves and history heuristic
                if not is_capture:
                    if ply_from_root < MoveOrdering.max_killer_move_ply:
                        self.move_orderer.killer_moves[ply_from_root].add(move)
                    history_score = ply_remaining * ply_remaining
                    color_index = int(self.board.turn)
                    self.move_orderer.history[color_index][move.from_square][move.to_square] += history_score

                if ply_from_root > 0:
                    self.repetition_table.try_pop()

                self.search_diagnostics.num_cutoffs += 1
                return beta

            # Found a new best move in this position
            if eval_score > alpha:
                evaluation_bound = TranspositionTable.exact
                best_move_in_this_position = move
                alpha = eval_score

                if ply_from_root == 0:
                    self.best_move_this_iteration = move
                    self.best_eval_this_iteration = eval_score
                    self.has_searched_at_least_one_move = True

        if ply_from_root > 0:
            self.repetition_table.try_pop()

        # Store position in transposition table
        self.transposition_table.store_evaluation(
            ply_remaining,
            ply_from_root,
            alpha,
            evaluation_bound,
            best_move_in_this_position
        )

        return alpha

    def quiescence_search(self, alpha, beta):
        if self.search_cancelled:
            return 0

        # Stand-pat evaluation
        eval_score = self.evaluation.evaluate(self.board)
        self.search_diagnostics.num_positions_evaluated += 1

        if eval_score >= beta:
            self.search_diagnostics.num_cutoffs += 1
            return beta

        if eval_score > alpha:
            alpha = eval_score

        # Generate capture moves only
        moves = [move for move in self.board.legal_moves if self.board.is_capture(move)]

        # Order captures
        moves.sort(key=lambda move: self.score_capture(move), reverse=True)

        for move in moves:
            self.board.push(move)
            eval_score = -self.quiescence_search(-beta, -alpha)
            self.board.pop()

            if eval_score >= beta:
                self.search_diagnostics.num_cutoffs += 1
                return beta

            if eval_score > alpha:
                alpha = eval_score

        return alpha

    def score_capture(self, move):
        """Score a capture move for move ordering in quiescence search"""
        victim_value = self.get_piece_value(self.board.piece_at(move.to_square))
        aggressor_value = self.get_piece_value(self.board.piece_at(move.from_square))
        return victim_value - aggressor_value/10  # MVV-LVA

    def get_piece_value(self, piece):
        """Get the value of a piece for move ordering"""
        if piece is None:
            return 0

        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 320,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 10000
        }
        return values.get(piece.piece_type, 0)

    def format_move(self, move):
        """Format a move for display"""
        if move.null():
            return "null"
        return move.uci()

    def increment_node(self):
        self.counter_searched_nood += 1 # mỗi luồng 1 phần tử-> k cần điều tiết (nếu đa luồng)
    def update_searched_branch(self):
        self.last_ply_zero= self.counter_searched_nood
    def get_node_searched_branch(self):
        return self.counter_searched_nood - self.last_ply_zero

    def get_best_move_changes(self, cur_depth):
        """
        caculate the change rate of best move from previous best moves

        :param best_moves_history: list of best move.
        :param N: Số lần lặp gần đây cần xem xét.
        :return: Tỷ lệ thay đổi của nước đi tốt nhất.
        """
        last_care = 2
        if cur_depth >= 6:
            last_care = cur_depth - 4

        changes = 0
        for i in range(last_care, cur_depth+1):
            if self.history_best_node[i] != self.history_best_node:
                changes += 1 # result change in high depth move valuable

        return changes / (cur_depth + 1 - last_care) 
    
    def score_analysis(self, cur_depth):
        """
        Phân tích điểm số qua các lần lặp để xác định xu hướng tăng, giảm, hoặc dao động.
        
        :param scores_history: Danh sách điểm số từ các lần lặp trước.
        :return: Một từ điển chứa thông tin về độ dao động và biên độ điểm số.
        """

        last_care:int = 2
        if cur_depth >= 5:
            last_care = cur_depth - 3 # care about last 4 one only

        increases = decreases = 0
        max_score:int = Searcher.negative_infinity
        min_score:int = Searcher.positive_infinity

        for i in range(last_care, cur_depth+1):
            if self.history_best_scores[i] > max_score:
                max_score = self.history_best_scores[i]
            if self.history_best_scores[i] < min_score:
                min_score = self.history_best_scores[i]

            if self.history_best_scores[i] > self.history_best_scores[i-1]:
                increases += i #the depth equal with valuable
            elif self.history_best_scores[i] < self.history_best_scores[i-1]:
                decreases += i

        score_change_rate=(max_score - min_score)/ max( abs(max_score), abs(min_score) )

        if increases/(cur_depth + 1 - last_care) > decreases: #only the first one decrease
            trend = "increasing"
        elif decreases/(cur_depth + 1 - last_care) > increases: 
            trend = "decreasing"
        elif score_change_rate > 0.25 and max_score-min_score >= self.panic_eval*0.5:
            trend = "oscillating"
        else:
            trend = "stable"
        
        if (self.history_best_scores[cur_depth -1] - self.history_best_scores[cur_depth] > self.panic_eval):
            trend = "panic"


        return trend, score_change_rate
 
    def subtree_ratio(self):
        return self.best_move_searched_node/self.counter_searched_nood
    
    def adjust_time(self, cur_depth):
        """
        Điều chỉnh thời gian suy nghĩ dựa trên các yếu tố phân tích.
        
        :param best_move_change_rate: Tỷ lệ thay đổi của nước đi tốt nhất.
        :param score_amplitude: Biên độ dao động của điểm số.
        :param subtree_ratio: Tỷ lệ kích thước của cây con.
        :return: Thời gian đã điều chỉnh.
        """
        time_multiplier = 1.0
        best_move_changes=self.get_best_move_changes(cur_depth=cur_depth)
        trend,score_rate=self.score_analysis(cur_depth=cur_depth)
        # Tăng thời gian dựa trên tỷ lệ thay đổi của nước đi tốt nhất
        if best_move_changes == 0:
            time_multiplier -= 0.2# 0 thay đổi thì giảm tgian
        else:
            time_multiplier += 0.25 * best_move_changes 
        
        # Tăng thời gian dựa trên biên độ dao động của điểm số
        if trend == "panic":
            time_multiplier += 0.25
        elif trend == "oscillating":
            time_multiplier += score_rate * 0.15
        elif trend == "decreasing":
            time_multiplier += score_rate * 0.2
        elif trend == "increasing":
            time_multiplier -= 0.15 # dont need to search more        
        else: # trend =stable
            time_multiplier -= 0.15

        # Tăng thời gian dựa trên tỷ lệ kích thước cây con
        tree_ratio = self.subtree_ratio()
        if  tree_ratio > 0.9:
            time_multiplier -= 0.3
        elif tree_ratio > 0.8:
            time_multiplier -= 0.1
        elif tree_ratio < 0.3:
            time_multiplier += 0.2
        
        return time_multiplier

    """in Strock Fish: * điều kiện của bọn này khi bắt đầu tối ưu time là depth_searched >= 10  =))))
    bestMoveInstability = 0.9929 + 1.8519 * (totBestMoveChanges / numThreads)
    bestMoveInstability = 1 + 1.7 * (totBestMoveChanges / numThreads)
    tùy bản
    Time.optimum() * fallingEval * reduction * bestMoveInstability

    timeReduction = 1.37 vs 0.65 tùy trường hợp)​

    

    Stockfish còn tính một đại lượng nodesEffort = rootMoves[0].effort * 100000 / nodes 
    đo tỷ lệ số nút dành cho nhánh tốt nhất. Nếu nodesEffort ≥ 97056 (tức nhánh tốt nhất chiếm >97%) 
    và search đã đủ sâu, engine sẽ dừng sớm (threads.stop = true) mà không chờ hết thời gian tối đa​
    
    không điều chỉnh time theo cây còn mà theo 1 công thức về độ đa dạng của bàn cờ(số move trong legal move,.....)

    bestMoveChanges lớn (ví dụ ≥ 1) thì coi move hiện tại là “khó” 
    và tăng thời gian suy luận (ví dụ nhân thời gian chuẩn với hệ số 1 + α * bestMoveChanges

    """


    @staticmethod
    def is_mate_score(score):
        """Check if a score indicates a mate"""
        if score == -float('inf'):
            return False
        return abs(score) > Searcher.immediate_mate_score - 1000

    @staticmethod
    def num_ply_to_mate_from_score(score):
        """Calculate the number of ply to mate from a mate score"""
        return Searcher.immediate_mate_score - abs(score)

    def announce_mate(self):
        """Announce mate if found"""
        if self.is_mate_score(self.best_eval_this_iteration):
            num_ply_to_mate = self.num_ply_to_mate_from_score(self.best_eval_this_iteration)
            num_moves_to_mate = ceil(num_ply_to_mate / 2)
            side_with_mate = "Black" if (self.best_eval_this_iteration * (1 if self.board.turn == chess.WHITE else -1) < 0) else "White"
            return f"{side_with_mate} can mate in {num_moves_to_mate} move{'s' if num_moves_to_mate > 1 else ''}"
        return "No mate found"

    def get_search_result(self):
        """Return the best move and evaluation"""
        return (self.best_move, self.best_eval)

    def end_search(self):
        """Cancel the search"""
        self.search_cancelled = True

    def clear_for_new_position(self):
        """Clear search data for a new position"""
        self.transposition_table.clear()
        self.move_orderer.clear_killers()

    def get_transposition_table(self):
        """Return the transposition table"""
        return self.transposition_table


class SearchDiagnostics:
    """Class to hold search statistics and diagnostics"""
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
