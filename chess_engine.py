import chess
import math
import sys

class ChessEngine:
    def __init__(self, fen: str):
        """
        Khởi tạo ChessEngine với bàn cờ từ FEN.
        :param fen: FEN string đại diện cho bàn cờ.
        """
        self.board = chess.Board(fen)

    def evaluate_board(self):
        """
        Đánh giá bàn cờ dựa trên giá trị quân cờ.
        :return: Điểm đánh giá của bàn cờ.
        """
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
        return score

    def get_legal_moves(self):
        """
        Lấy tất cả các nước đi hợp lệ cho bàn cờ hiện tại.
        :return: Danh sách các nước đi hợp lệ.
        """
        return list(self.board.legal_moves)


def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Thuật toán Minimax với Alpha-Beta Pruning.
    :param board: Bàn cờ hiện tại.
    :param depth: Độ sâu tìm kiếm.
    :param alpha: Giá trị Alpha (dùng cho pruning).
    :param beta: Giá trị Beta (dùng cho pruning).
    :param maximizing_player: Boolean, True nếu là lượt của người chơi tối đa (trắng).
    :return: Giá trị của bàn cờ ở mức độ sâu hiện tại.
    """
    if depth == 0 or board.is_game_over():
        return ChessEngine(board.fen()).evaluate_board()  # Đánh giá bàn cờ tại leaf node

    legal_moves = list(board.legal_moves)

    if maximizing_player:
        max_eval = -math.inf
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
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
                break
        return min_eval


def find_best_move(fen: str, depth: int):
    """
    Tìm nước đi tốt nhất cho bàn cờ dựa trên FEN và độ sâu tìm kiếm.
    :param fen: FEN string đại diện cho bàn cờ.
    :param depth: Độ sâu tìm kiếm.
    :return: Nước đi tốt nhất trong định dạng UCI.
    """
    board = chess.Board(fen)
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


# Nếu đây là file chính, chạy chức năng tìm nước đi tốt nhất từ FEN và độ sâu.
if __name__ == "__main__":
    # Lấy FEN và độ sâu từ dòng lệnh
    fen = sys.argv[1]  # FEN bàn cờ
    depth = int(sys.argv[2])  # Độ sâu tìm kiếm

    best_move = find_best_move(fen, depth)
    print(best_move)  # In ra nước đi tốt nhất