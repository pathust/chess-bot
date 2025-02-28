import chess
import chess.engine

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()

    def reset_board(self):
        """Khởi tạo lại bàn cờ về trạng thái ban đầu."""
        self.board.reset()

    def make_move(self, move_uci):
        """Thực hiện một nước đi theo định dạng UCI (ví dụ: 'e2e4')."""
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
        """Hàm đánh giá đơn giản dựa trên giá trị quân cờ."""
        piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000
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
        return score
    

import math

def minimax(board, depth, alpha, beta, maximizing):
    """Thuật toán Minimax với cắt tỉa Alpha-Beta."""
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Cắt tỉa
        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Cắt tỉa
        return min_eval

def find_best_move(board, depth):
    """Tìm nước đi tốt nhất dựa trên Minimax."""
    best_move = None
    best_value = -math.inf
    alpha, beta = -math.inf, math.inf

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, alpha, beta, False)
        board.pop()
        
        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move.uci() if best_move else None