import threading
from threading import Event
import chess
import time
from search.searcher import Searcher
from typing import List, Dict, Optional, Tuple
import heapq

class ChessBot:
    def __init__(self, use_nnue=False, initial_fen=None, top_k=3):
        """
        Khởi tạo Bot cờ vua có khả năng pondering
        
        Args:
            use_nnue (bool): Sử dụng NNUE evaluation
            initial_fen (str, optional): Vị trí bàn cờ FEN ban đầu
            top_k (int): Số lượng nước đi hàng đầu của đối thủ cần dự đoán và tìm kiếm
        """
        # Khởi tạo bàn cờ
        if initial_fen:
            self.board = chess.Board(initial_fen)
        else:
            self.board = chess.Board()

        # Khởi tạo searcher
        print("Initializing main searcher")
        self.searcher = Searcher(self.board, use_nnue)
        
        # Lưu số lượng nước đi hàng đầu cần xem xét khi pondering
        self.top_k = top_k
        self.use_nnue = use_nnue
        self.ponder_depth = 2  # Độ sâu mặc định cho pondering
        
        # Trạng thái tìm kiếm chính
        self.is_thinking = False
        self.current_search_id = 0
        self.search_timer = None
        self.search_cancelled = False

        # Callback người dùng
        self.on_move_chosen = None
        
        # Thiết lập thread tìm kiếm chính
        self.search_event = Event()
        self.search_thread = threading.Thread(target=self._search_thread, daemon=True)
        self.search_thread.start()

        # Các biến pondering
        self.is_pondering = False
        self.pondering_cancelled = False
        self.pondering_event = Event()
        self.ponder_results = {}  # Dict lưu kết quả tìm kiếm cho mỗi nước đi dự đoán
        self.pondering_threads = []
        self.ponder_board = None  # Bản sao của bàn cờ để pondering
        self.ponder_searchers = {}  # Dict lưu các searcher cho mỗi nước đi dự đoán
        
        # Khởi tạo thread pondering
        self.ponder_thread = threading.Thread(target=self._pondering_manager_thread, daemon=True)
        self.ponder_thread.start()
        
        # Lock để đồng bộ hóa truy cập vào dữ liệu pondering
        self.ponder_lock = threading.RLock()

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

        # Xóa dữ liệu tìm kiếm cũ khi thay đổi vị trí
        self.searcher.clear_for_new_position()
        
        # Dừng pondering hiện tại nếu có
        self.stop_pondering()

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
                # Dừng pondering hiện tại
                self.stop_pondering()
                
                # Kiểm tra xem nước đi này có trùng với nước đã pondering không
                if self.use_pondering_for_opponent_move(move_uci):
                    print(f"Using pondering results for human move {move_uci}")
                
                # Thực hiện nước đi
                self.board.push(move)
                
                # Lượt của bot, tìm và thực hiện nước đi tốt nhất
                # (Có thể dùng kết quả pondering đã tính trước đó)
                
                return True
            return False
        except ValueError:
            return False

    def choose_think_time(self, time_remaining_white_ms, time_remaining_black_ms, increment_white_ms, increment_black_ms):
        """
        Tính toán thời gian suy nghĩ hợp lý dựa trên thời gian còn lại
        
        Args:
            time_remaining_white_ms (int): Thời gian còn lại của trắng (ms)
            time_remaining_black_ms (int): Thời gian còn lại của đen (ms)
            increment_white_ms (int): Thời gian cộng thêm mỗi nước của trắng (ms)
            increment_black_ms (int): Thời gian cộng thêm mỗi nước của đen (ms)
            
        Returns:
            int: Thời gian suy nghĩ được đề xuất (ms)
        """
        # Lấy thời gian còn lại của bên đang đi
        my_time_remaining_ms = time_remaining_white_ms if self.board.turn else time_remaining_black_ms
        my_increment_ms = increment_white_ms if self.board.turn else increment_black_ms

        # Tính thời gian suy nghĩ là một phần của thời gian còn lại
        think_time_ms = my_time_remaining_ms / 40.0  # Chia cho 40 nước

        # Thêm một phần của thời gian cộng thêm
        if my_time_remaining_ms > my_increment_ms * 2:
            think_time_ms += my_increment_ms * 0.8

        # Đảm bảo thời gian tối thiểu là 50ms hoặc 25% thời gian còn lại
        min_think_time = min(50, my_time_remaining_ms * 0.25)
        return int(max(min_think_time, think_time_ms))

    def think_timed(self, time_ms):
        """
        Bắt đầu tìm kiếm nước đi tốt nhất với thời gian giới hạn
        
        Args:
            time_ms (int): Thời gian tìm kiếm tối đa (ms)
        """
        print(f"Starting timed search with {time_ms} ms")
        self.is_thinking = True

        # Hủy timer tìm kiếm hiện tại nếu có
        if self.search_timer:
            self.search_timer.cancel()

        # Dừng pondering nếu đang thực hiện
        self.stop_pondering()
        
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
                    print("Starting search")
                    self.searcher.start_search()

                    # Sau khi tìm kiếm hoàn thành, lấy nước đi tốt nhất từ searcher
                    best_move = self.searcher.best_move
                    print(f"Search completed, best_move: {best_move}")

                    # Thông báo kết quả
                    if self.is_thinking:
                        self._search_completed(best_move)

                except Exception as e:
                    print(f"Error in search thread: {str(e)}")
                    import traceback
                    traceback.print_exc()

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
            print(f"Calling callback with move: {move_uci}")
            self.on_move_chosen(move_uci)
            
            # Thực hiện nước đi trên bàn cờ
            self.board.push(move)
            
            # Sau khi đã đi nước của bot, bắt đầu pondering cho nước tiếp theo của người chơi
            self.start_pondering(depth=self.ponder_depth)
        elif self.on_move_chosen:
            print("No valid move found or null move")
            self.on_move_chosen(None)

    def _end_search(self, search_id=None):
        """
        Kết thúc quá trình tìm kiếm
        
        Args:
            search_id (int, optional): ID của tìm kiếm cần kết thúc
        """
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

            # Lấy nước đi tốt nhất hiện tại nếu có
            if hasattr(self.searcher, 'best_move') and self.searcher.best_move:
                self._search_completed(self.searcher.best_move)
            else:
                self.is_thinking = False

    def stop_thinking(self):
        """Dừng quá trình tìm kiếm hiện tại"""
        self._end_search()

    def get_best_move(self, depth=3, time_ms=None):
        """
        Tìm và trả về nước đi tốt nhất (blocking)
        
        Args:
            depth (int): Độ sâu tìm kiếm
            time_ms (int, optional): Thời gian tìm kiếm tối đa (ms)
            
        Returns:
            str: Nước đi tốt nhất ở định dạng UCI
        """
        print(f"Finding best move at depth {depth}, time limit: {time_ms} ms")

        # Thiết lập độ sâu cho searcher
        if hasattr(self.searcher, 'max_depth'):
            self.searcher.max_depth = depth

        # Tạo một Event để đồng bộ
        result_event = Event()
        best_move = [None]  # Sử dụng list để lưu kết quả từ callback

        def on_move_found(move):
            print(f"Best move found: {move}")
            best_move[0] = move
            result_event.set()

        # Lưu callback hiện tại
        old_callback = self.on_move_chosen
        self.on_move_chosen = on_move_found

        # Bắt đầu tìm kiếm
        self.think_timed(time_ms if time_ms else 30000)  # Mặc định 30 giây

        # Chờ kết quả
        print("Waiting for search result...")
        result_event.wait()
        print(f"Search completed, result: {best_move[0]}")

        # Khôi phục callback cũ
        self.on_move_chosen = old_callback

        return best_move[0]

    # =============== PONDERING METHODS ===============
    
    def start_pondering(self, depth=2):
        """
        Bắt đầu quá trình pondering - dự đoán nước đi tiếp theo của đối thủ và search
        
        Args:
            depth (int): Độ sâu tìm kiếm cho mỗi nước pondering
        """
        if self.is_thinking or self.is_pondering:
            print("Cannot start pondering while thinking or already pondering")
            return
        
        print(f"Starting pondering with depth: {depth}")
        
        with self.ponder_lock:
            # Tạo bản sao của bàn cờ
            self.ponder_board = self.board.copy()
            
            # Cập nhật trạng thái pondering
            self.is_pondering = True
            self.pondering_cancelled = False
            
            # Xóa kết quả pondering cũ
            self.ponder_results.clear()
            self.ponder_searchers.clear()
            
            # Khởi chạy pondering threads cho các nước tiếp theo
            self.pondering_threads.clear()
            
            # Lưu độ sâu tìm kiếm
            self.ponder_depth = depth
            
            # Kích hoạt thread pondering
            self.pondering_event.set()
    
    def stop_pondering(self):
        """Dừng quá trình pondering hiện tại"""
        if not self.is_pondering:
            return
        
        print("Stopping pondering")
        
        with self.ponder_lock:
            self.pondering_cancelled = True
            
            # Dừng tất cả các searcher đang pondering
            for searcher in self.ponder_searchers.values():
                searcher.end_search()
            
            # Đợi tất cả các thread pondering kết thúc
            for thread in self.pondering_threads:
                if thread.is_alive():
                    thread.join(0.5)  # Chờ tối đa 0.5 giây
            
            # Xóa danh sách thread
            self.pondering_threads.clear()
            
            # Cập nhật trạng thái
            self.is_pondering = False
    
    def _pondering_manager_thread(self):
        """Thread quản lý quá trình pondering"""
        while True:
            # Đợi kích hoạt
            self.pondering_event.wait()
            self.pondering_event.clear()
            
            if not self.pondering_cancelled:
                try:
                    # Dự đoán top-k nước đi tiếp theo của NGƯỜI CHƠI
                    human_moves = self._predict_opponent_moves()
                    
                    if human_moves:
                        print(f"Predicted {len(human_moves)} potential human player moves for pondering")
                        
                        # Tạo thread riêng cho mỗi nước đi người chơi dự đoán
                        with self.ponder_lock:
                            # Xóa thread cũ
                            self.pondering_threads.clear()
                            
                            # Tạo thread mới cho mỗi nước đi
                            for move_uci, _ in human_moves:
                                if self.pondering_cancelled:
                                    break
                                    
                                # Tạo thread mới để xử lý pondering cho nước đi này
                                thread = threading.Thread(
                                    target=self._ponder_move,
                                    args=(move_uci, self.ponder_depth),
                                    daemon=True
                                )
                                
                                # Thêm vào danh sách và bắt đầu
                                self.pondering_threads.append(thread)
                                thread.start()
                                
                            print(f"Started {len(self.pondering_threads)} pondering threads for human moves")
                    
                except Exception as e:
                    print(f"Error in pondering manager: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                finally:
                    # Kiểm tra trạng thái pondering
                    if not self.pondering_threads:
                        with self.ponder_lock:
                            self.is_pondering = False
    
    def _predict_opponent_moves(self) -> List[Tuple[str, float]]:
        """
        Dự đoán top-k nước đi tiếp theo của NGƯỜI CHƠI dựa trên vị trí hiện tại
        
        Returns:
            List[Tuple[str, float]]: Danh sách (move_uci, evaluation) được sắp xếp theo đánh giá
        """
        # Tạo bản sao của bàn cờ hiện tại 
        # Lưu ý: Đây là vị trí sau khi bot đã đi, và đây là lượt của người chơi
        human_board = self.board.copy()
        
        # Tạo danh sách lưu (nước đi, điểm đánh giá)
        candidate_moves = []
        
        # Lấy tất cả nước đi hợp lệ của người chơi từ vị trí hiện tại
        legal_moves = list(human_board.legal_moves)
        
        print(f"Evaluating {len(legal_moves)} legal human player moves for pondering")
        
        # Tạo một searcher tạm thời để đánh giá nhanh các nước đi
        temp_searcher = Searcher(human_board.copy(), self.use_nnue)
        
        # Đánh giá từng nước đi của người chơi
        for move in legal_moves:
            # Tạo bản sao bàn cờ và thực hiện nước đi
            temp_board = human_board.copy()
            temp_board.push(move)
            
            # Search nông để đánh giá vị trí
            evaluation = -100  # Giá trị mặc định
            
            # Sử dụng các phương thức khác nhau tùy thuộc vào searcher
            if hasattr(temp_searcher, 'quick_evaluate'):
                # Nếu có phương thức đánh giá nhanh
                evaluation = temp_searcher.quick_evaluate(temp_board, depth=1)
            elif hasattr(temp_searcher, 'evaluate_position'):
                # Nếu chỉ có phương thức đánh giá vị trí
                evaluation = temp_searcher.evaluate_position(temp_board)
            
            candidate_moves.append((move.uci(), evaluation))
        
        # Sắp xếp theo đánh giá từ góc nhìn của người chơi
        # Người chơi thường sẽ chọn nước đi có lợi nhất cho họ
        # Từ góc nhìn người chơi, họ muốn giá trị thấp nhất (vì màu ngược với bot)
        candidate_moves.sort(key=lambda x: x[1])
        
        # Trả về top-k nước đi tiềm năng nhất của người chơi
        return candidate_moves[:self.top_k]
    
    def _ponder_move(self, human_move_uci, depth):
        """
        Thực hiện pondering cho một nước đi cụ thể của người chơi
        
        Args:
            human_move_uci (str): Nước đi của người chơi ở định dạng UCI
            depth (int): Độ sâu tìm kiếm
        """
        try:
            move_obj = chess.Move.from_uci(human_move_uci)
            
            # Tạo bản sao bàn cờ và thực hiện nước đi của người chơi
            ponder_board = self.board.copy()
            ponder_board.push(move_obj)
            
            # Tạo searcher riêng cho nước đi này
            ponder_searcher = Searcher(ponder_board, self.use_nnue)
            
            with self.ponder_lock:
                # Lưu searcher để có thể dừng nếu cần
                self.ponder_searchers[human_move_uci] = ponder_searcher
                
                # Khởi tạo kết quả
                self.ponder_results[human_move_uci] = {
                    'searched': False,
                    'best_move': None,
                    'evaluation': None,
                    'depth': 0,
                    'time_spent': 0
                }
            
            # Bắt đầu đếm thời gian
            start_time = time.time()
            
            # Thiết lập độ sâu tìm kiếm nếu searcher hỗ trợ
            if hasattr(ponder_searcher, 'max_depth'):
                ponder_searcher.max_depth = depth
            
            # Bắt đầu tìm kiếm
            print(f"Starting pondering for human move {human_move_uci} with depth {depth}")
            ponder_searcher.start_search()
            
            # Tính thời gian đã sử dụng
            time_spent = int((time.time() - start_time) * 1000)
            
            # Lưu kết quả vào dictionary
            with self.ponder_lock:
                if not self.pondering_cancelled:  # Kiểm tra xem pondering đã bị hủy chưa
                    self.ponder_results[human_move_uci] = {
                        'searched': True,
                        'best_move': ponder_searcher.best_move.uci() if hasattr(ponder_searcher, 'best_move') and ponder_searcher.best_move else None,
                        'evaluation': ponder_searcher.evaluation if hasattr(ponder_searcher, 'evaluation') else None,
                        'depth': ponder_searcher.current_depth if hasattr(ponder_searcher, 'current_depth') else depth,
                        'time_spent': time_spent
                    }
                    
                    print(f"Completed pondering for human move {human_move_uci}, bot response: {self.ponder_results[human_move_uci]['best_move']}")
            
        except Exception as e:
            print(f"Error in pondering for move {human_move_uci}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def get_pondering_results(self):
        """
        Lấy kết quả pondering hiện tại
        
        Returns:
            dict: Dictionary chứa kết quả pondering cho mỗi nước đi
        """
        with self.ponder_lock:
            return self.ponder_results.copy()
    
    def use_pondering_for_opponent_move(self, human_move_uci):
        """
        Sử dụng kết quả pondering khi người chơi đã đi một nước đi đã được dự đoán
        
        Args:
            human_move_uci (str): Nước đi của người chơi ở định dạng UCI
            
        Returns:
            bool: True nếu tìm thấy và sử dụng kết quả pondering
        """
        with self.ponder_lock:
            if human_move_uci in self.ponder_results and self.ponder_results[human_move_uci].get('searched', False):
                # Lấy nước đi tốt nhất từ kết quả pondering
                best_response = self.ponder_results[human_move_uci].get('best_move')
                
                # Chia sẻ kết quả từ searcher pondering sang searcher chính
                if best_response and human_move_uci in self.ponder_searchers:
                    ponder_searcher = self.ponder_searchers[human_move_uci]
                    
                    # Nếu searcher có transposition table, sao chép nó sang searcher chính
                    if hasattr(ponder_searcher, 'tt') and hasattr(self.searcher, 'tt'):
                        # Hiện thực phụ thuộc vào cấu trúc tt của searcher
                        # Đây chỉ là ví dụ, cần điều chỉnh tùy theo cấu trúc thực tế
                        if hasattr(ponder_searcher.tt, 'table') and hasattr(self.searcher.tt, 'table'):
                            # Sao chép các entry từ tt của ponder searcher sang searcher chính
                            for key, value in ponder_searcher.tt.table.items():
                                self.searcher.tt.table[key] = value
                    
                    # Nếu searcher có history table, killer moves, sao chép chúng
                    if hasattr(ponder_searcher, 'history') and hasattr(self.searcher, 'history'):
                        self.searcher.history = ponder_searcher.history.copy()
                    
                    if hasattr(ponder_searcher, 'killers') and hasattr(self.searcher, 'killers'):
                        self.searcher.killers = ponder_searcher.killers.copy()
                
                print(f"Using pondering result for human move {human_move_uci}, bot response: {best_response}")
                
                # Nếu nước đi đã được dự đoán, có thể sử dụng trực tiếp 
                # để trả về ngay lập tức mà không cần tìm kiếm lại
                if hasattr(self, 'on_move_chosen') and self.on_move_chosen and best_response:
                    # Đây là nơi bot có thể trả về ngay lập tức nước đi tốt nhất
                    # đã được tính toán trong quá trình pondering
                    # self.on_move_chosen(best_response)
                    # Nhưng có thể vẫn cần tìm kiếm lại với độ sâu cao hơn
                    # để có kết quả chính xác hơn, tùy vào yêu cầu
                    pass
                
                return True
                
        return False
    
    # =============== UTILITY METHODS ===============
    
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

    def notify_new_game(self):
        """Thông báo cho bot rằng một ván cờ mới đã bắt đầu"""
        self.searcher.clear_for_new_position()
        self.stop_pondering()
        self.ponder_results.clear()

    def quit(self):
        """Dọn dẹp tài nguyên khi kết thúc"""
        self.stop_thinking()
        self.stop_pondering()
        self.search_cancelled = True
        self.pondering_cancelled = True
        self.search_event.set()  # Wake up thread để nó có thể thoát
        self.pondering_event.set()  # Wake up pondering thread