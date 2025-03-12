import chess

# Hệ số tối ưu (tạm đặt thủ công, sẽ tối ưu bằng Machine Learning sau)
WEIGHTS = {
    "material": 1.0, # giá trị quân cờ
    "king_safety": 0.8, # độ an toàn của quân vua
    "pawn_structure": -1.2, # cấu trúc tốt
    "mobility": 0.7, # tính linh động
    "center_control": 1.15 # kiểm soát trung tâm
}

# Giá trị quân cờ
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 320,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 10000
}

# Đánh giá giá trị quân cờ (Material)
def evaluate_material(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score * WEIGHTS["material"] 

# Đánh giá an toàn Vua (King Safety)
def evaluate_king_safety(board):
  
  #  Kiểm tra an toàn của vua: Nếu vua có tốt bảo vệ trước mặt, cộng điểm.
   
    score = 0
    for king_square in board.pieces(chess.KING, chess.WHITE):
        safe_squares = [sq for sq in [king_square - 8, king_square - 9, king_square - 7] if 0 <= sq < 64]
        if any(board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN for sq in safe_squares):
            score += 20  # Vua trắng có tốt bảo vệ
    
    for king_square in board.pieces(chess.KING, chess.BLACK):
        safe_squares = [sq for sq in [king_square + 8, king_square + 9, king_square + 7] if 0 <= sq < 64]
        if any(board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN for sq in safe_squares):
            score -= 20  # Vua đen có tốt bảo vệ
    
    return score * WEIGHTS["king_safety"]



# Đánh giá cấu trúc tốt (Pawn Structure)
def evaluate_pawn_structure(board):
   
 # - Nếu một cột có nhiều hơn 1 tốt → bị trừ điểm.
 # - Tốt cô lập cũng bị trừ điểm.
  
    score = 0
    for file in range(8):
        white_pawns = len([sq for sq in range(file, 64, 8) if board.piece_at(sq) == chess.PAWN and board.color_at(sq) == chess.WHITE])
        black_pawns = len([sq for sq in range(file, 64, 8) if board.piece_at(sq) == chess.PAWN and board.color_at(sq) == chess.BLACK])
        if white_pawns > 1:
            score -= 10  # Tốt trắng bị chồng
        if black_pawns > 1:
            score += 10  # Tốt đen bị chồng
    return score * WEIGHTS["pawn_structure"]  

# Đánh giá tính cơ động (Mobility)
def evaluate_mobility(board):
# - Số nước đi hợp lệ càng nhiều, điểm càng cao.
# - Mỗi nước đi hợp lệ cộng 5 điểm.

    return len(list(board.legal_moves)) * 5 * WEIGHTS["mobility"]  

# Đánh giá kiểm soát trung tâm (Center Control)
CENTER_SQUARES = [chess.D4, chess.D5, chess.E4, chess.E5]
def evaluate_center_control(board):

    score = sum(10 for sq in CENTER_SQUARES if board.piece_at(sq))
    return score * WEIGHTS["center_control"]  

# Hàm tổng hợp đánh giá bàn cờ
def evaluate_board(fen):
    
   # Tính tổng điểm đánh giá bàn cờ dựa trên 5 yếu tố chính.
    board = chess.Board(fen)

   # Tính điểm của từng yếu tố
    material = evaluate_material(board)
    king_safety = evaluate_king_safety(board)
    pawn_structure = evaluate_pawn_structure(board)
    mobility = evaluate_mobility(board)
    center_control = evaluate_center_control(board)

    total_score = material + king_safety + pawn_structure + mobility + center_control
    return total_score

if __name__ == "__main__":
    fen = "r1bq1rk1/pppp1ppp/2n2n2/4p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQ - 0 7"
    
    score = evaluate_board(fen)
    print(f"Điểm số của thế cờ: {score}")




