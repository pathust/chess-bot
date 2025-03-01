from fastapi import FastAPI
import chess

app = FastAPI()

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