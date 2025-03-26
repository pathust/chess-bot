import threading
from threading import Event
import chess
from search.searcher import Searcher

class ChessBot:
    def __init__(self, initial_fen=None):
        """
        Khởi tạo Bot cờ vua
        
        Args:
            initial_fen (str, optional): Vị trí bàn cờ FEN ban đầu. Nếu None, sẽ dùng vị trí chuẩn.
        """
        # Khởi tạo bàn cờ
        if initial_fen:
            self.board = chess.Board(initial_fen)
        else:
            self.board = chess.Board()

        # Tạo searcher cho việc tìm kiếm nước đi tốt nhất
        print("initialize searcher")
        self.searcher = Searcher(self.board)

        # Trạng thái tìm kiếm
        self.is_thinking = False
        self.search_timer = None

        # Callback
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

    def think(self, depth=3, time_ms=None, callback=None):
        """
        Bắt đầu tìm kiếm nước đi tốt nhất với độ sâu hoặc thời gian cho trước
        
        Args:
            depth (int): Độ sâu tìm kiếm (mặc định: 3)
            time_ms (int, optional): Thời gian tìm kiếm tối đa (ms)
            callback (function, optional): Hàm callback khi tìm được nước đi tốt nhất
        """
        if self.is_thinking:
            self.stop_thinking()

        self.is_thinking = True

        # Lưu callback
        if callback:
            self.on_move_chosen = callback

        # Thiết lập timer nếu giới hạn thời gian
        if time_ms:
            self.search_timer = threading.Timer(time_ms / 1000.0, self.stop_thinking)
            self.search_timer.daemon = True
            self.search_timer.start()

        # Cài đặt thông tin tìm kiếm
        self.search_depth = depth

        # Kích hoạt thread tìm kiếm
        self.search_event.set()

    def _search_thread(self):
        """Thread tìm kiếm nước đi tốt nhất"""
        while True:
            self.search_event.wait()
            self.search_event.clear()

            # Thiết lập callback cho searcher
            self.searcher.on_search_complete = self._on_search_complete

            # Bắt đầu tìm kiếm (searcher sẽ gọi callback khi hoàn thành)
            self.searcher.start_search()

    def _on_search_complete(self, move):
        """Callback khi tìm kiếm hoàn thành"""
        self.is_thinking = False

        # Hủy timer nếu có
        if self.search_timer:
            self.search_timer.cancel()
            self.search_timer = None

        # Gọi callback của người dùng
        if self.on_move_chosen:
            # Chuyển đổi từ đối tượng Move của python-chess sang chuỗi UCI
            move_uci = move.uci()
            self.on_move_chosen(move_uci)

    def stop_thinking(self):
        """Dừng quá trình tìm kiếm hiện tại"""
        if self.is_thinking:
            self.searcher.end_search()
            self.is_thinking = False

            # Hủy timer nếu có
            if self.search_timer:
                self.search_timer.cancel()
                self.search_timer = None

    def get_best_move(self, depth=3, time_ms=None):
        """
        Tìm và trả về nước đi tốt nhất (blocking)
        
        Args:
            depth (int): Độ sâu tìm kiếm
            time_ms (int, optional): Thời gian tìm kiếm tối đa (ms)
            
        Returns:
            str: Nước đi tốt nhất ở định dạng UCI
        """
        # Tạo một Event để đồng bộ
        result_event = Event()
        best_move = [None]  # Sử dụng list để lưu kết quả từ callback

        def on_move_found(move):
            best_move[0] = move
            result_event.set()

        # Bắt đầu tìm kiếm
        self.think(depth, time_ms, on_move_found)

        # Chờ kết quả
        result_event.wait()

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

    def quit(self):
        """Dọn dẹp tài nguyên khi kết thúc"""
        self.stop_thinking()
        self.search_event.set()  # Wake up thread để nó có thể thoát
