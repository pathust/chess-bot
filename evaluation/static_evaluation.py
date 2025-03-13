import chess
from typing import List

# Đánh giá giá trị quân cờ (Material)
def evaluate_material(board: chess.Board) -> float:
    # Giá trị quân cờ
    piece_value = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 320,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 10000
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_value[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score

# Đánh giá an toàn Vua (King Safety)
def evaluate_king_safety(board: chess.Board) -> float:
  #  Kiểm tra an toàn của vua: Nếu vua có tốt bảo vệ trước mặt, cộng điểm.

    score = 0
    for king_square in board.pieces(chess.KING, chess.WHITE):
        safe_squares = ([sq
            for sq in [king_square - 8, king_square - 9, king_square - 7]
            if 0 <= sq < 64
        ])
        if any(
            board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN
            for sq in safe_squares
        ):
            score += 20  # Vua trắng có tốt bảo vệ

    for king_square in board.pieces(chess.KING, chess.BLACK):
        safe_squares = ([sq
            for sq in [king_square + 8, king_square + 9, king_square + 7]
                if 0 <= sq < 64
        ])
        if any(
            board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN
            for sq in safe_squares
        ):
            score -= 20  # Vua đen có tốt bảo vệ

    return score



# Đánh giá cấu trúc tốt (Pawn Structure)
def evaluate_pawn_structure(board: chess.Board) -> float:

 # - Nếu một cột có nhiều hơn 1 tốt → bị trừ điểm.
 # - Tốt cô lập cũng bị trừ điểm.

    score = 0
    for file in range(8):
        white_pawns = len([
            sq for sq in range(file, 64, 8)
                if board.piece_at(sq) == chess.PAWN and board.color_at(sq) == chess.WHITE
            ])
        black_pawns = len([
            sq for sq in range(file, 64, 8)
                if board.piece_at(sq) == chess.PAWN and board.color_at(sq) == chess.BLACK
            ])
        if white_pawns > 1:
            score -= 10  # Tốt trắng bị chồng
        if black_pawns > 1:
            score += 10  # Tốt đen bị chồng
    return score

# Đánh giá tính cơ động (Mobility)
def evaluate_mobility(board) -> float:
# - Số nước đi hợp lệ càng nhiều, điểm càng cao.
# - Mỗi nước đi hợp lệ cộng 5 điểm.

    return len(list(board.legal_moves)) * 5

# Đánh giá kiểm soát trung tâm (Center Control)
CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]
def evaluate_center_control(board: chess.Board) -> float:
    score = sum(10 for sq in CENTER_SQUARES if board.piece_at(sq))
    return score

# Hàm tổng hợp đánh giá bàn cờ
def evaluate_board(fen: str,
                   weights = [1.0, 0.8, -1.2, 0.7, 1.15]
) -> float:
   # Tính tổng điểm đánh giá bàn cờ dựa trên 5 yếu tố chính.
    board = chess.Board(fen)

   # Tính điểm của từng yếu tố
    material = evaluate_material(board)
    king_safety = evaluate_king_safety(board)
    pawn_structure = evaluate_pawn_structure(board)
    mobility = evaluate_mobility(board)
    center_control = evaluate_center_control(board)

    total_score = (
                material         * weights[0]
                + king_safety    * weights[1]
                + pawn_structure * weights[2]
                + mobility       * weights[3]
                + center_control * weights[4]
    )
    return total_score

if __name__ == "__main__":
    FEN = "r1bq1rk1/pppp1ppp/2n2n2/4p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQ - 0 7"
    print(f"Điểm số của thế cờ: {evaluate_board(FEN)}")
