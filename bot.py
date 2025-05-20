import math
import threading
from threading import Event
import chess
from search.searcher import Searcher

class ChessBot:
    def __init__(self, use_nnue=False, initial_fen=None):
        """
        Khởi tạo Bot cờ vua
        
        Args:
            initial_fen (str, optional): Vị trí bàn cờ FEN ban đầu
        """
        # Khởi tạo bàn cờ
        if initial_fen:
            self.board = chess.Board(initial_fen)
        else:
            self.board = chess.Board()

        # Tạo searcher cho việc tìm kiếm nước đi tốt nhất
        print("Initializing searcher")
        self.searcher = Searcher(self.board, use_nnue)

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

        # thông số thời gian
        self.total_time = math.inf
        self.remain_time_white = math.inf
        self.remain_time_black = math.inf
        self.increment_time = 0

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
                return True
            return False
        except ValueError:
            return False

    def set_think_time_second(self, total_time: int, increment_time: int =0):
        """nhận input đầu vào là thời gian với đơn vị giây"""
        total_time = total_time * 1000
        self.total_time = total_time
        self.remain_time_white = total_time
        self.remain_time_black = total_time
        self.increment_time = increment_time

    #cái này t chữa rõ nên đặt đâu vs logic lúc ng chơi 
    def time_reduction(self):
        if self.board.turn:
            self.remain_time_white -= self.searcher.search_total_timer
        else:
            self.remain_time_black -= self.searcher.search_total_timer
    
  
    def new_choose_think_time(self):
        """
        Tính toán thời gian suy nghĩ hợp lý dựa trên thời gian còn lại trong trường hợp không chia thời gian theo giai đoạn
        Lấy ý tưởng từ stock fish
            
        Returns:
            int: Thời gian suy nghĩ được đề xuất (ms)
        """
        # Lấy thời gian còn lại của bên đang đi
        offset_time = 30 #thời gian dự tính để xử lý mỗi ply
        my_time_remaining_ms = self.remain_time_white if self.board.turn else self.remain_time_black
        my_increment_ms = self.increment_time -offset_time 

        centiMTG = 5051

        # Make sure timeLeft is > 0 since we may use it as a divisor
        timeLeft =my_time_remaining_ms+ (my_increment_ms * (centiMTG - 100) - 50 * (200 + centiMTG)) / 100       
        originalTimeAdjust = 0.3128 * math.log10(timeLeft) - 0.4354
        if originalTimeAdjust < 0:
            originalTimeAdjust = 0.13

        # Calculate time constants based on current time left.
        logTimeInSec = math.log10(my_time_remaining_ms / 1000.0)
        optConstant  = min(0.0032116 + 0.000321123 * logTimeInSec, 0.00508017)
        
        optScale = min(0.0121431 + math.pow(self.board.ply() + 2.94693, 0.461073) * optConstant,
                            0.213035 * my_time_remaining_ms / timeLeft) * originalTimeAdjust
        
        optScale = min (0.5,optScale)
        #maxConstant  = max(3.3977 + 3.03950 * logTimeInSec, 2.94761)
        #maxScale = min(6.67704, maxConstant + ply / 11.9847)
        
        opt_time = optScale * my_time_remaining_ms
        return opt_time

    """MTG (Moves To Go): số nước tối ưu engine cần thực hiện để kết thúc ván đấu nếu cả hai bên chơi hoàn hảo (theo tablebase hoặc phân tích rất sâu).
    Centi-MTG: chỉ là MTG × 100 để có độ chính xác cao hơn (giống như centipawn là pawn × 100).
    lấy defaulse = 5051"""
    # t có để biến  self.use_time_manager trong searcher = false nếu để chỉnh thời gian thì set lên true sau
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

    def quit(self):
        """Dọn dẹp tài nguyên khi kết thúc"""
        self.stop_thinking()
        self.search_cancelled = True
        self.search_event.set()  # Wake up thread để nó có thể thoát


