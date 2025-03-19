import chess

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

# Bảng thưởng Mobility từ Stockfish 1.9 cho từng loại quân
MOBILITY_BONUS = {
    chess.KNIGHT:  [(-38, -33), (-25, -23), (-12, -13), (0, -3), (12, 7), (25, 17), (31, 22), (38, 27), (38, 27)],  # Mã
    chess.BISHOP:  [(-25, -30), (-11, -16), (3, -2), (17, 12), (31, 26), (45, 40), (57, 52), (65, 60), (71, 65), 
                    (74, 69), (76, 71), (78, 73), (79, 74), (80, 75), (81, 76), (81, 76)],  # Tượng
    chess.ROOK:    [(-20, -36), (-14, -19), (-8, -3), (-2, 13), (4, 29), (10, 46), (14, 62), (19, 79), (23, 95), 
                    (26, 106), (27, 111), (28, 114), (29, 116), (30, 117), (31, 118), (32, 118)],  # Xe
    chess.QUEEN:   [(-10, -18), (-8, -13), (-6, -7), (-3, -2), (-1, 3), (1, 8), (3, 13), (5, 19), (8, 23), 
                    (10, 27), (12, 32), (15, 34), (16, 35), (17, 35), (18, 35), (20, 35)],  # Hậu
}

# Hàm tính trọng số λ
def phase_weight(board: chess.Board) -> float:
    """
    Tính trọng số λ để xác định giai đoạn của trò chơi (trung cuộc vs tàn cuộc).
    λ = 1 (trung cuộc), λ = 0 (tàn cuộc), giảm dần khi số quân trên bàn giảm.
    """
    total_phase = 24  # Giá trị phase tối đa khi ván cờ mới bắt đầu
    phase = total_phase

    # Giá trị phase giảm dựa trên số lượng quân trên bàn
    phase -= len(board.pieces(chess.QUEEN, chess.WHITE)) * 4
    phase -= len(board.pieces(chess.QUEEN, chess.BLACK)) * 4
    phase -= len(board.pieces(chess.ROOK, chess.WHITE)) * 2
    phase -= len(board.pieces(chess.ROOK, chess.BLACK)) * 2
    phase -= len(board.pieces(chess.BISHOP, chess.WHITE)) * 1
    phase -= len(board.pieces(chess.BISHOP, chess.BLACK)) * 1
    phase -= len(board.pieces(chess.KNIGHT, chess.WHITE)) * 1
    phase -= len(board.pieces(chess.KNIGHT, chess.BLACK)) * 1

    # Đảm bảo λ nằm trong khoảng [0,1]
    return max(0, min(1, phase / total_phase))

# Đánh giá tính cơ động (Mobility)
def evaluate_mobility(board: chess.Board) -> float:
    """
    Đánh giá mobility dựa trên số bước đi hợp lệ của từng quân cờ.
    Tính điểm mobility dựa trên bảng thưởng điểm của Stockfish, có cân nhắc hệ số λ.
    """
    total_mg = 0  # Điểm mobility trung cuộc
    total_eg = 0  # Điểm mobility tàn cuộc

    # Duyệt qua tất cả quân cờ trên bàn
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type in MOBILITY_BONUS:
            # Đếm số nước đi hợp lệ của quân cờ
            mobility_count = sum(1 for move in board.legal_moves if move.from_square == square)
            mobility_bonus = MOBILITY_BONUS[piece.piece_type]

            # Giới hạn số bước đi trong phạm vi bảng MobilityBonus
            mobility_index = min(mobility_count, len(mobility_bonus) - 1)
            mg_bonus, eg_bonus = mobility_bonus[mobility_index]  # Lấy điểm mobility MG & EG

           # Nếu là quân trắng -> cộng, quân đen -> trừ
            sign = 1 if piece.color == chess.WHITE else -1
            total_mg += sign * mg_bonus
            total_eg += sign * eg_bonus

    # Xác định trọng số λ (để cân bằng MG và EG)
    lambda_phase = phase_weight(board)
    
    # Tính điểm tổng kết mobility dựa trên pha chơi
    return lambda_phase * total_mg + (1 - lambda_phase) * total_eg
    
# Đánh giá kiểm soát trung tâm (Center Control)
CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]
def evaluate_center_control(board: chess.Board, bonus: float) -> float:
    score = sum(bonus for sq in CENTER_SQUARES if board.piece_at(sq))
    return score

# Hàm đánh giá vị trí quân cờ (Piece-Square Table)
def evaluate_piece_square(board: chess.Board, piece_square_weight) -> float:
    # Bảng điểm vị trí cho tất cả quân cờ
    piece_square_table = {
        chess.PAWN: [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        chess.KNIGHT: [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ],
        chess.BISHOP: [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ],
        chess.ROOK: [
            [0, 0, 0, 5, 5, 0, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        chess.QUEEN: [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ],
        chess.KING: [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20]
        ]
    }
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type in piece_square_table:
            rank, file = divmod(square, 8)

            if piece.color == chess.WHITE:
                score += piece_square_table[piece.piece_type][rank][file] * piece_square_weight[0]
            else:  # Quân đen
                score -= piece_square_table[piece.piece_type][7 - rank][file] * piece_square_weight[1]

    return score

# Hàm đánh giá các vị trí chiến thuật đặc biệt (Evaluation Pieces)
def evaluate_tactical_positions(board: chess.Board, tactical_weight) -> float:
    """
    Đánh giá vị trí chiến thuật của các quân cờ trên bàn cờ.
    - Cộng điểm cho Xe trên cột mở
    - Cộng điểm cho Mã ở outpost
    - Cộng điểm cho Tượng trên đường chéo dài
    - Trừ điểm nếu Hậu di chuyển quá sớm
    """
    score = 0
    move_count = len(board.move_stack)  # Số nước đi đã diễn ra

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue

        # Xe trên cột mở (Open File)
        if piece.piece_type == chess.ROOK and is_open_file(board, square):
            score += 10 * tactical_weight if piece.color == chess.WHITE else -10 * tactical_weight

        # Mã ở vị trí outpost
        if piece.piece_type == chess.KNIGHT and is_outpost(board, square):
            score += 15 * tactical_weight if piece.color == chess.WHITE else -15 * tactical_weight

        # Tượng trên đường chéo dài
        if piece.piece_type == chess.BISHOP and is_long_diagonal(board, square):
            score += 8 * tactical_weight if piece.color == chess.WHITE else -8 * tactical_weight

        # Phạt nếu Hậu di chuyển quá sớm
        if piece.piece_type == chess.QUEEN and is_early_queen_move(move_count):
            score -= 10 * tactical_weight if piece.color == chess.WHITE else 10 * tactical_weight

    return score

# HÀM HỖ TRỢ
def is_open_file(board, square) -> bool:
    """Kiểm tra xem Xe có đứng trên cột mở không (không có tốt trên cột này)."""
    file = square % 8  # Lấy cột của quân cờ
    for rank in range(8):
        piece = board.piece_at(rank * 8 + file)
        if piece and piece.piece_type == chess.PAWN:  # Nếu có tốt, không phải cột mở
            return False
    return True  # Không có tốt nào trên cột -> Cột mở

def is_outpost(board, square) -> bool:
    """Kiểm tra xem Mã có đang ở một vị trí outpost hay không (được bảo vệ bởi tốt, không bị tốt đối phương đe dọa)."""
    rank, file = divmod(square, 8)
    piece = board.piece_at(square)

    if not piece or piece.piece_type != chess.KNIGHT:
        return False

    # Kiểm tra có tốt bảo vệ không
    friendly_pawn_1 = board.piece_at((rank - 1) * 8 + file - 1) if rank > 0 and file > 0 else None
    friendly_pawn_2 = board.piece_at((rank - 1) * 8 + file + 1) if rank > 0 and file < 7 else None

    # Kiểm tra có tốt đối phương tấn công không
    enemy_pawn_1 = board.piece_at((rank + 1) * 8 + file - 1) if rank < 7 and file > 0 else None
    enemy_pawn_2 = board.piece_at((rank + 1) * 8 + file + 1) if rank < 7 and file < 7 else None

    # Mã phải được bảo vệ bởi tốt phe ta và không bị tốt đối phương tấn công
    if ((friendly_pawn_1 and friendly_pawn_1.piece_type == chess.PAWN and friendly_pawn_1.color == piece.color) or
        (friendly_pawn_2 and friendly_pawn_2.piece_type == chess.PAWN and friendly_pawn_2.color == piece.color)) and \
       not ((enemy_pawn_1 and enemy_pawn_1.piece_type == chess.PAWN and enemy_pawn_1.color != piece.color) or
            (enemy_pawn_2 and enemy_pawn_2.piece_type == chess.PAWN and enemy_pawn_2.color != piece.color)):
        return True

    return False

def is_long_diagonal(board, square) -> bool:
    """Kiểm tra xem Tượng có đang đứng trên đường chéo dài không."""
    rank, file = divmod(square, 8)
    return min(rank, file) >= 3 or min(rank, 7 - file) >= 3  # Đường chéo phải có ít nhất 3 ô

def is_early_queen_move(move_count) -> bool:
    """Phạt nếu Hậu di chuyển quá sớm trong 10 nước đi đầu tiên."""
    return move_count < 10  # Nếu tổng số nước đi <10, phạt nếu Hậu đã rời vị trí ban đầu

# Hàm đánh giá Tempo**
def evaluate_tempo(board: chess.Board, tempo_weight) -> float:
    move_count = len(board.move_stack)
    return -move_count * tempo_weight 

# Hàm tổng hợp đánh giá bàn cờ
def evaluate_board(fen: str,
                   chromosomes = [
                                1.0, 0.8, -1.2, 0.7, 1.15, 1.05, 0.85, -0.95, # trọng số tối ưu từng hàm 
                                100, 300, 320, 500, 900, 10000, # giá trị từng quân cờ trong bàn cờ - cố định
                                10, 10, # pawn_structure
                                20, # king_safety
                                10, #centrer_control
                                10,10, # piece-square table
                                15, # eva piecee
                                7 # tempo
                            ]
) -> float:
    # Tính tổng điểm đánh giá bàn cờ dựa trên 5 yếu tố chính.
    board = chess.Board(fen)

    # Trong so cua tung yeu to
    weights = chromosomes[:8]

    # Tính điểm của từng yếu tố
    piece_values = chromosomes[8:14]
    material = evaluate_material(board, piece_values)

    doubled_penalty, isolated_penalty = chromosomes[14:16]
    pawn_structure = evaluate_pawn_structure(board, doubled_penalty, isolated_penalty)

    bonus = chromosomes[16]
    king_safety = evaluate_king_safety(board, bonus)

    mobility = evaluate_mobility(board)

    bonus = chromosomes[17]
    center_control = evaluate_center_control(board, bonus)

    bonus = chromosomes[17:19]
    Piece_Square_Table = evaluate_piece_square(board, bonus)

    bonus = chromosomes[19]
    tactical_score = evaluate_tactical_positions(board, bonus)

    bonus = chromosomes[20]
    tempo_score = evaluate_tempo(board, bonus)



    total_score = (
                material             * weights[0]
                + king_safety        * weights[1]
                + pawn_structure     * weights[2]
                + mobility           * weights[3]
                + center_control     * weights[4]
                + Piece_Square_Table * weights[5]
                + tactical_score     * weights[6]
                + tempo_score        * weights[7]
    )
    return total_score

if __name__ == "__main__":
    FEN = "r1bq1rk1/pppp1ppp/2n2n2/4p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQ - 0 7"
    print(f"Điểm số của thế cờ: {evaluate_board(FEN)}")
