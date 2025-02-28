from fastapi import FastAPI
import chess

app = FastAPI()

# Basic evaluation function
def evaluate_board(board):
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                score += value  
            else:
                score -= value
    return score

# Minimax algorithm (without Alpha-Beta Pruning)
def minimax(board, depth, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if maximizing:
        max_eval = -float("inf")
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, False)
            board.pop()
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float("inf")
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, True)
            board.pop()
            min_eval = min(min_eval, eval)
        return min_eval

# Find best move using Minimax
def find_best_move(board, depth=3):
    best_move = None
    best_value = -float("inf")

    for move in board.legal_moves:
        board.push(move)
        move_value = minimax(board, depth - 1, False)
        board.pop()

        if move_value > best_value:
            best_value = move_value
            best_move = move

    return best_move

# API endpoint
@app.post("/move/")
def get_best_move(fen: str, depth: int = 3):
    try:
        board = chess.Board(fen)
        best_move = find_best_move(board, depth)
        return {"best_move": best_move.uci() if best_move else None}
    except Exception as e:
        return {"error": str(e)}

# API test
@app.get("/")
def read_root():
    return {"message": "Chess API is running"}