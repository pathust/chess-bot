import chess
from typing import List

# Đánh giá giá trị quân cờ (Material)
def evaluate_material(board: chess.Board, piece_values) -> float:
    # Giá trị quân cờ
    value_dict = {
        chess.PAWN: piece_values[0],
        chess.KNIGHT: piece_values[1],
        chess.BISHOP: piece_values[2],
        chess.ROOK: piece_values[3],
        chess.QUEEN: piece_values[4],
        chess.KING: piece_values[5]
    }

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = value_dict[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score

# Đánh giá an toàn Vua (King Safety)
def evaluate_king_safety(board: chess.Board, bonus: float) -> float:
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
            score += bonus  # Vua trắng có tốt bảo vệ

    for king_square in board.pieces(chess.KING, chess.BLACK):
        safe_squares = ([sq
            for sq in [king_square + 8, king_square + 9, king_square + 7]
                if 0 <= sq < 64
        ])
        if any(
            board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN
            for sq in safe_squares
        ):
            score -= bonus  # Vua đen có tốt bảo vệ

    return score



# Đánh giá cấu trúc tốt (Pawn Structure)
import chess

def evaluate_pawn_structure(board: chess.Board, doubled_penalty: float, isolated_penalty: float) -> float:
    """
    Đánh giá cấu trúc tốt dựa trên số lượng tốt chồng và tốt cô lập.

    Args:
        board (chess.Board): Bàn cờ hiện tại.
        doubled_penalty (float): Hệ số phạt cho tốt chồng.
        isolated_penalty (float): Hệ số phạt cho tốt cô lập.

    Returns:
        float: Điểm số đánh giá cấu trúc tốt (giá trị âm là xấu, giá trị dương là tốt).
    """
    score = 0

    # Lấy danh sách vị trí tốt của mỗi bên
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    # Xác định cột có ít nhất một tốt
    white_pawn_columns = {sq % 8 for sq in white_pawns}
    black_pawn_columns = {sq % 8 for sq in black_pawns}

    # Duyệt từng cột trên bàn cờ (0 - 7 tương ứng với cột 'a' đến 'h')
    for column in range(8):
        # Đếm số tốt trong mỗi cột
        white_count = sum(1 for sq in white_pawns if sq % 8 == column)
        black_count = sum(1 for sq in black_pawns if sq % 8 == column)

        # Áp dụng hình phạt cho tốt chồng (có nhiều hơn 1 tốt trên cùng một cột)
        if white_count > 1:
            score -= (white_count - 1) * doubled_penalty
        if black_count > 1:
            score += (black_count - 1) * doubled_penalty

        # Áp dụng hình phạt cho tốt cô lập (không có tốt nào ở cột bên cạnh)
        if column not in white_pawn_columns and (column - 1 not in white_pawn_columns and column + 1 not in white_pawn_columns):
            score -= isolated_penalty
        if column not in black_pawn_columns and (column - 1 not in black_pawn_columns and column + 1 not in black_pawn_columns):
            score += isolated_penalty

    return score



# Đánh giá tính cơ động (Mobility)
def evaluate_mobility(board, bonus: float) -> float:
# - Số nước đi hợp lệ càng nhiều, điểm càng cao.
# - Mỗi nước đi hợp lệ cộng 5 điểm.

    return len(list(board.legal_moves)) * bonus

# Đánh giá kiểm soát trung tâm (Center Control)
CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]
def evaluate_center_control(board: chess.Board, bonus: float) -> float:
    score = sum(bonus for sq in CENTER_SQUARES if board.piece_at(sq))
    return score

# Hàm tổng hợp đánh giá bàn cờ
def evaluate_board(fen: str,
                   chromosomes = [
                                1.0, 0.8, -1.2, 0.7, 1.15,
                                100, 300, 320, 500, 900, 10000,
                                10, 10,
                                20,
                                5,
                                10
                            ]
) -> float:
    # Tính tổng điểm đánh giá bàn cờ dựa trên 5 yếu tố chính.
    board = chess.Board(fen)

    # Trong so cua tung yeu to
    weights = chromosomes[:5]

    # Tính điểm của từng yếu tố
    piece_values = chromosomes[5:11]
    material = evaluate_material(board, piece_values)

    doubled_penalty, isolated_penalty = chromosomes[11:13]
    pawn_structure = evaluate_pawn_structure(board, doubled_penalty, isolated_penalty)

    bonus = chromosomes[13]
    king_safety = evaluate_king_safety(board, bonus)

    bonus = chromosomes[14]
    mobility = evaluate_mobility(board, bonus)

    bonus = chromosomes[15]
    center_control = evaluate_center_control(board, bonus)

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
