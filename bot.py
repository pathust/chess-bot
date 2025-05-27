import threading
from threading import Event
import chess
from search.searcher import Searcher
import time 
import math

class ChessBot:
    def __init__(self, initial_fen=None, opening_book_path=None):
        """
        Khởi tạo Bot cờ vua
        
        Args:
            initial_fen (str, optional): Vị trí bàn cờ FEN ban đầu
            opening_book_path (str, optional): Đường dẫn đến opening book
        """
        # Khởi tạo bàn cờ
        if initial_fen:
            self.board = chess.Board(initial_fen)
        else:
            self.board = chess.Board()

        # Tạo searcher cho việc tìm kiếm nước đi tốt nhất
        # print("Initializing searcher")
        self.searcher = Searcher(self.board, opening_book_path=opening_book_path)

        # Trạng thái tìm kiếm
        self.is_thinking = False
        self.current_search_id = 0
        self.search_timer = None
        self.search_cancelled = False

        # Callback người dùng
        self.on_move_chosen = None

        # Thiết lập thread tìm kiếm
        self.search_event = Event()
        self.search_thread = threading.Thread(target=self._search_thread, daemon=True)
        self.search_thread.start()

    def set_position(self, fen=None, moves=None):
        """
        Thiết lập vị trí bàn cờ
        
        Args:
            fen (str, optional): Chuỗi FEN mô tả vị trí bàn cờ
            moves (list, optional): Danh sách các nước đi từ vị trí FEN
        """
        if fen:
            self.board.set_fen(fen)
        else:
            self.board.reset()

        if moves:
            for move in moves:
                self.board.push_uci(move)

        # Cập nhật searcher với board mới
        self.searcher.board = self.board
        # Xóa dữ liệu tìm kiếm cũ khi thay đổi vị trí
        self.searcher.clear_for_new_position()

    def make_move(self, move_uci):
        """
        Thực hiện một nước đi trên bàn cờ
        
        Args:
            move_uci (str): Nước đi ở định dạng UCI (vd: "e2e4")
            
        Returns:
            bool: True nếu nước đi hợp lệ và đã được thực hiện
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                # Cập nhật searcher với board mới
                self.searcher.board = self.board
                return True
            return False
        except ValueError:
            return False

    def choose_think_time(self, time_remaining_white_ms, time_remaining_black_ms, increment_white_ms, increment_black_ms):
        """
        Tính toán thời gian suy nghĩ tối ưu cho chess engine với alpha-beta pruning và quiescence search
        
        Args:
            time_remaining_white_ms (int): Thời gian còn lại của trắng (ms)
            time_remaining_black_ms (int): Thời gian còn lại của đen (ms)
            increment_white_ms (int): Thời gian cộng thêm mỗi nước của trắng (ms)
            increment_black_ms (int): Thời gian cộng thêm mỗi nước của đen (ms)
            
        Returns:
            int: Thời gian suy nghĩ được đề xuất (ms)
        """
        # Lấy thông tin của bên đang đi
        my_time_remaining_ms = time_remaining_white_ms if self.board.turn else time_remaining_black_ms
        my_increment_ms = increment_white_ms if self.board.turn else increment_black_ms
        
        # Safety buffer để tránh timeout
        safety_buffer = 100
        
        ply = self.board.ply()
        
        # Ước tính số nước còn lại dựa trên giai đoạn game
        if ply < 20:  # Opening
            moves_to_go = max(50, 80 - ply)
            phase_multiplier = 0.8  # Ít thời gian hơn trong opening
        elif ply < 50:  # Middlegame  
            moves_to_go = max(25, 60 - ply)
            phase_multiplier = 1.2  # Nhiều thời gian hơn trong middlegame
        else:  # Endgame
            moves_to_go = max(15, 40 - ply // 3)
            phase_multiplier = 1.0  # Thời gian cân bằng trong endgame
        
        # Tính thời gian cơ bản
        effective_time = my_time_remaining_ms + moves_to_go * (my_increment_ms - safety_buffer)
        base_time_ms = max(0, effective_time) / moves_to_go
        
        # Điều chỉnh dựa trên đặc điểm của alpha-beta với quiescence search
        complexity_factor = 1.0
        
        complexity_factor *= 1.3  # Tăng 30% cho quiescence search
        
        # Alpha-beta với killer moves hiệu quả hơn ở depth cao
        if ply > 30:  # Endgame positions benefit more from deeper search
            complexity_factor *= 1.15
        
        # Điều chỉnh theo tình huống thời gian
        if my_time_remaining_ms < 30000:  # Dưới 30 giây
            time_pressure_factor = 0.7
        elif my_time_remaining_ms < 60000:  # Dưới 1 phút
            time_pressure_factor = 0.85
        else:
            time_pressure_factor = 1.0
        
        # Tính thời gian cuối cùng
        optimal_time = base_time_ms * phase_multiplier * complexity_factor * time_pressure_factor
        
        # Giới hạn thời gian
        min_think_time = 50
        max_think_time = min(my_time_remaining_ms // 3, 60000)  # Không quá 1/3 thời gian còn lại hoặc 1 phút
        
        final_time = int(max(min_think_time, min(optimal_time, max_think_time)))
        
        # Cập nhật depth cho searcher dựa trên thời gian
        self.searcher.update_start_depth(final_time)
        
        return final_time

    def think_timed(self, time_ms):
        """
        Bắt đầu tìm kiếm nước đi tốt nhất với thời gian giới hạn
        
        Args:
            time_ms (int): Thời gian tìm kiếm tối đa (ms)
        """
        # print(f"Starting timed search with {time_ms} ms")
        self.is_thinking = True

        # Disable opening book after 20 moves
        if self.searcher.opening_book and self.board.ply() > 20:
            # print(f"Disabling opening book at ply {self.board.ply()}")
            self.searcher.opening_book = None

        # Hủy timer tìm kiếm hiện tại nếu có
        if self.search_timer:
            self.search_timer.cancel()

        # Bắt đầu tìm kiếm mới
        self._start_search(time_ms)

    def _start_search(self, time_ms=None):
        """
        Khởi tạo quá trình tìm kiếm mới
        
        Args:
            time_ms (int, optional): Thời gian tìm kiếm tối đa (ms)
        """
        # Tăng ID tìm kiếm để phân biệt các tìm kiếm
        self.current_search_id += 1

        # Kích hoạt thread tìm kiếm
        self.search_cancelled = False
        self.search_event.set()

        # Thiết lập timer nếu có giới hạn thời gian
        if time_ms:
            self.search_timer = threading.Timer(time_ms / 1000.0,
                                               lambda: self._end_search(self.current_search_id))
            self.search_timer.daemon = True
            self.search_timer.start()

    def _search_thread(self):
        """Thread tìm kiếm nước đi tốt nhất"""
        while True:
            # Đợi kích hoạt
            self.search_event.wait()
            self.search_event.clear()

            if not self.search_cancelled:
                # Bắt đầu tìm kiếm
                try:
                    # print("Starting search")
                    start = time.time()
                    self.searcher.start_search()

                    # Sau khi tìm kiếm hoàn thành, lấy nước đi tốt nhất từ searcher
                    best_move = self.searcher.best_move
                    # print(f"Search completed, best_move: {best_move}")

                    # Thông báo kết quả
                    if self.is_thinking:
                        self._search_completed(best_move)
                    duration = time.time() - start
                    # print("Executed Time: ", duration)

                except Exception as e:
                    # print(f"Error in search thread: {str(e)}")
                    import traceback
                    # traceback.print_exc()

                    # Nếu lỗi, trả về nước đi đầu tiên nếu có
                    legal_moves = list(self.board.legal_moves)
                    if legal_moves and self.is_thinking:
                        self._search_completed(legal_moves[0])
                    else:
                        self._search_completed(None)

    def _search_completed(self, move):
        """
        Xử lý khi tìm kiếm hoàn thành
        
        Args:
            move (chess.Move): Nước đi tốt nhất được tìm thấy
        """
        # Ghi lại thời điểm khi tìm kiếm hoàn thành
        search_complete_time = time.time()
        # print(f"SEARCH_COMPLETED: {search_complete_time:.6f}")
        
        if hasattr(self, 'end_search_start_time') and self.end_search_start_time > 0:
            delay = search_complete_time - self.end_search_start_time
            # print(f"SEARCH_CANCEL_DELAY: {delay:.6f} seconds")

        if not self.is_thinking:
            return

        # Cập nhật trạng thái
        self.is_thinking = False

        if self.search_timer:
            self.search_timer.cancel()
            self.search_timer = None

        # Gọi callback với nước đi tốt nhất
        if self.on_move_chosen and move and not (hasattr(move, 'null') and move.null()):
            move_uci = move.uci()
            # print(f"Calling callback with move: {move_uci}")
            self.on_move_chosen(move_uci)
        elif self.on_move_chosen:
            # print("No valid move found or null move")
            self.on_move_chosen(None)

    def _end_search(self, search_id=None):
        """
        Kết thúc quá trình tìm kiếm
        
        Args:
            search_id (int, optional): ID của tìm kiếm cần kết thúc
        """
        # Ghi lại thời điểm bắt đầu thực hiện end_search
        self.end_search_start_time = time.time()
        # print(f"END_SEARCH_START: {self.end_search_start_time:.6f}")
        
        # Nếu search_id được chỉ định, chỉ kết thúc tìm kiếm đó
        if search_id is not None and search_id != self.current_search_id:
            return

        # Hủy timer nếu có
        if self.search_timer:
            self.search_timer.cancel()
            self.search_timer = None

        # Thông báo cho searcher dừng tìm kiếm
        if self.is_thinking:
            self.search_cancelled = True
            self.searcher.end_search()
            # print(f"END_SEARCH_SIGNAL_SENT: {time.time():.6f}")

            # Lấy nước đi tốt nhất hiện tại nếu có
            if hasattr(self.searcher, 'best_move') and self.searcher.best_move:
                self._search_completed(self.searcher.best_move)
            else:
                self.is_thinking = False

    def stop_thinking(self):
        """Dừng quá trình tìm kiếm hiện tại"""
        self._end_search()

    def get_best_move(self, max_depth=9, time_ms=None):
        """
        Tìm và trả về nước đi tốt nhất (blocking) - Modified to capture depth results
        
        Args:
            max_depth (int): Độ sâu tìm kiếm tối đa (default: 9)
            time_ms (int, optional): Thời gian tìm kiếm tối đa (ms)
            
        Returns:
            str: Nước đi tốt nhất ở định dạng UCI
        """
        # print(f"Finding best move with max depth {max_depth}, time limit: {time_ms} ms")

        # Thiết lập độ sâu cho searcher
        self.searcher.max_depth = max_depth

        # Tạo một Event để đồng bộ
        result_event = Event()
        best_move = [None]  # Sử dụng list để lưu kết quả từ callback

        def on_move_found(move):
            # print(f"Best move found: {move}")
            best_move[0] = move
            result_event.set()

        # Lưu callback hiện tại
        old_callback = self.on_move_chosen
        self.on_move_chosen = on_move_found

        # Bắt đầu tìm kiếm
        self.think_timed(time_ms if time_ms else 30000)  # Mặc định 30 giây

        # Chờ kết quả
        # print("Waiting for search result...")
        result_event.wait()
        # print(f"Search completed, result: {best_move[0]}")

        # Khôi phục callback cũ
        self.on_move_chosen = old_callback

        return best_move[0]

    def get_depth_results(self):
        """
        Get detailed results for each depth from the last search
        
        Returns:
            dict: Dictionary containing results for each depth
                  Format: {depth: {'best_move': str, 'execution_time': float, 'eval': int, ...}}
        """
        if hasattr(self.searcher, 'get_depth_results'):
            return self.searcher.get_depth_results()
        else:
            # Fallback for older searcher versions
            # print("Warning: Searcher doesn't support depth results capture")
            return {}

    def was_opening_book_used(self):
        """
        Check if the opening book was used in the last search
        
        Returns:
            bool: True if opening book was used
        """
        if hasattr(self.searcher, 'used_opening_book'):
            return self.searcher.used_opening_book
        return False

    def get_search_statistics(self):
        """
        Get comprehensive statistics from the last search
        
        Returns:
            dict: Search statistics including timing, nodes, etc.
        """
        depth_results = self.get_depth_results()
        if not depth_results:
            return {}
        
        stats = {
            'total_depths_searched': len(depth_results),
            'max_depth_reached': max(depth_results.keys()) if depth_results else 0,
            'total_time': sum(r.get('execution_time', 0) for r in depth_results.values()),
            'opening_book_used': self.was_opening_book_used(),
            'completed_depths': len([r for r in depth_results.values() if r.get('completed', False)]),
            'partial_depths': len([r for r in depth_results.values() if r.get('partial_search', False)])
        }
        
        return stats

    def get_board_fen(self):
        """Trả về trạng thái bàn cờ dưới dạng FEN"""
        return self.board.fen()

    def get_legal_moves(self):
        """Trả về danh sách các nước đi hợp lệ"""
        return [move.uci() for move in self.board.legal_moves]

    def is_game_over(self):
        """Kiểm tra xem trò chơi đã kết thúc chưa"""
        return self.board.is_game_over()

    def get_game_result(self):
        """Trả về kết quả của trò chơi nếu đã kết thúc"""
        if not self.board.is_game_over():
            return "Game in progress"

        if self.board.is_checkmate():
            return "Checkmate - " + ("Black wins" if self.board.turn == chess.WHITE else "White wins")
        elif self.board.is_stalemate():
            return "Draw by stalemate"
        elif self.board.is_insufficient_material():
            return "Draw by insufficient material"
        elif self.board.is_fifty_moves():
            return "Draw by fifty-move rule"
        elif self.board.is_repetition():
            return "Draw by repetition"
        return "Game over"

    def get_board_unicode(self):
        """Trả về bàn cờ dưới dạng Unicode để hiển thị trong console"""
        return str(self.board)

    def get_board_evaluation(self):
        """
        Get current board evaluation
        
        Returns:
            float: Board evaluation from engine's perspective
        """
        if hasattr(self.searcher, 'best_eval'):
            return self.searcher.best_eval
        return 0

    def get_principal_variation(self):
        """
        Get the principal variation (best line) from the last search
        
        Returns:
            list: List of moves in UCI format representing the best line
        """
        # This would require additional implementation in the searcher
        # For now, return the best move found
        if hasattr(self.searcher, 'best_move') and self.searcher.best_move:
            return [self.searcher.best_move.uci()]
        return []

    def notify_new_game(self):
        """Thông báo cho bot rằng một ván cờ mới đã bắt đầu"""
        self.searcher.clear_for_new_position()
        # Reset board to starting position
        self.board.reset()
        self.searcher.board = self.board

    def quit(self):
        """Dọn dẹp tài nguyên khi kết thúc"""
        self.stop_thinking()
        self.search_cancelled = True
        self.search_event.set()  # Wake up thread để nó có thể thoát

    # Utility methods for analysis
    def analyze_position(self, max_depth=9, time_ms=30000):
        """
        Analyze current position and return comprehensive results
        
        Args:
            max_depth (int): Maximum depth to analyze
            time_ms (int): Time limit in milliseconds
            
        Returns:
            dict: Comprehensive analysis results
        """
        # print(f"🔍 Analyzing position: {self.get_board_fen()}")
        
        start_time = time.time()
        best_move = self.get_best_move(max_depth=max_depth, time_ms=time_ms)
        analysis_time = time.time() - start_time
        
        depth_results = self.get_depth_results()
        search_stats = self.get_search_statistics()
        
        analysis = {
            'fen': self.get_board_fen(),
            'best_move': best_move,
            'analysis_time': analysis_time,
            'depth_results': depth_results,
            'search_statistics': search_stats,
            'evaluation': self.get_board_evaluation(),
            'opening_book_used': self.was_opening_book_used(),
            'legal_moves_count': len(list(self.board.legal_moves)),
            'game_phase': self._get_game_phase(),
            'position_complexity': self._estimate_position_complexity()
        }
        
        return analysis

    def _get_game_phase(self):
        """Estimate the current game phase"""
        ply = self.board.ply()
        if ply < 20:
            return "opening"
        elif ply < 50:
            return "middlegame"
        else:
            return "endgame"

    def _estimate_position_complexity(self):
        """Estimate position complexity based on various factors"""
        legal_moves = len(list(self.board.legal_moves))
        piece_count = len(self.board.piece_map())
        
        # Simple complexity estimate
        if legal_moves > 35 and piece_count > 20:
            return "high"
        elif legal_moves > 20 and piece_count > 15:
            return "medium"
        else:
            return "low"

    def compare_moves(self, moves, max_depth=6, time_per_move=5000):
        """
        Compare multiple moves and return analysis for each
        
        Args:
            moves (list): List of moves in UCI format to compare
            max_depth (int): Depth to analyze each move
            time_per_move (int): Time limit per move in milliseconds
            
        Returns:
            dict: Analysis results for each move
        """
        original_fen = self.get_board_fen()
        move_analysis = {}
        
        for move_uci in moves:
            try:
                # Make the move
                move = chess.Move.from_uci(move_uci)
                if move not in self.board.legal_moves:
                    move_analysis[move_uci] = {'error': 'Illegal move'}
                    continue
                
                self.board.push(move)
                self.searcher.board = self.board
                
                # Analyze the resulting position
                analysis = self.analyze_position(max_depth=max_depth, time_ms=time_per_move)
                move_analysis[move_uci] = analysis
                
                # Undo the move
                self.board.pop()
                self.searcher.board = self.board
                
            except Exception as e:
                move_analysis[move_uci] = {'error': str(e)}
                # Restore original position
                self.set_position(fen=original_fen)
        
        return move_analysis