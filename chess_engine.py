import chess
import math

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()

    def reset_board(self):
        """Khởi tạo lại bàn cờ về trạng thái ban đầu."""
        self.board.reset()

    def make_move(self, move_uci):
        """Thực hiện một nước đi theo định dạng UCI."""
        move = chess.Move.from_uci(move_uci)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def undo_move(self):
        """Hoàn tác nước đi cuối cùng."""
        if self.board.move_stack:
            self.board.pop()

    def get_legal_moves(self):
        """Lấy danh sách các nước đi hợp lệ."""
        return [move.uci() for move in self.board.legal_moves]

    def evaluate_board(self):
        """Hàm đánh giá đơn giản dựa trên giá trị quân cờ và các yếu tố khác."""
        piece_values = {
            chess.PAWN: 1, 
            chess.KNIGHT: 3, 
            chess.BISHOP: 3,
            chess.ROOK: 5, 
            chess.QUEEN: 9, 
            chess.KING: 1000
        }
        score = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        # Cộng thêm điểm cho các yếu tố khác như: Di chuyển quân, bảo vệ quân, các mối đe dọa, v.v.
        return score

    def null_move_heuristic(self, depth):
        """Áp dụng Null Move Heuristic để giảm chiều sâu tìm kiếm ban đầu."""
        self.board.push(chess.Move.null())  # Thực hiện nước đi null cho đối thủ
        score = minimax(self.board, depth - 1, -math.inf, math.inf, False, True)
        self.board.pop()  # Hoàn tác nước đi null
        return score

    def quiescence_search(self, alpha, beta, maximizing):
        """Quiescence Search để tránh các nước đi không ổn định như bắt quân."""
        if self.board.is_game_over():
            return self.evaluate_board()

        # Lấy tất cả các nước đi hợp lệ
        legal_moves = list(self.board.legal_moves)

        # Tìm kiếm tối đa nếu là lượt của player trắng
        if maximizing:
            max_eval = -math.inf
            for move in legal_moves:
                self.board.push(move)
                eval = self.quiescence_search(alpha, beta, False)
                self.board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            # Tìm kiếm tối thiểu nếu là lượt của player đen
            min_eval = math.inf
            for move in legal_moves:
                self.board.push(move)
                eval = self.quiescence_search(alpha, beta, True)
                self.board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

# Minimax Algorithm with Alpha-Beta Pruning and Null Move Heuristic
def minimax(board, depth, alpha, beta, maximizing, null_move=False):
    """Minimax algorithm with alpha-beta pruning and null move heuristic."""
    # Nếu đã đến độ sâu tối đa hoặc ván cờ đã kết thúc, trả về giá trị của bàn cờ
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    # Áp dụng Null Move Heuristic tại đây nếu depth > 1
    if null_move and depth > 1:
        null_move_score = null_move_heuristic(board, depth)
        if null_move_score >= beta:
            return null_move_score

    legal_moves = list(board.legal_moves)

    # Nếu là lượt của player trắng (maximizing)
    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False, null_move)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  
        return max_eval
    else:
        # Nếu là lượt của player đen (minimizing)
        min_eval = math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True, null_move)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break 
        return min_eval

def find_best_move(fen, depth):
    """Tìm nước đi tốt nhất dựa trên Minimax."""
    board = chess.Board(fen)
    best_move = None
    best_value = -math.inf
    alpha, beta = -math.inf, math.inf

    # Lặp qua các nước đi hợp lệ và đánh giá
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, alpha, beta, False, True)
        board.pop()
        
        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move.uci() if best_move else None