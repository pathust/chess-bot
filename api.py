from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/move/")
def get_best_move(fen: str, depth: int = 3):
    try:
        # Gọi chess_engine.py như một process riêng biệt và truyền FEN cùng depth
        result = subprocess.run(
            ["python3", "chess_engine.py", fen, str(depth)],  # Chạy chess_engine.py với các tham số FEN và depth
            capture_output=True,
            text=True
        )

        # Kiểm tra lỗi từ stderr
        if result.stderr:
            return {"error": result.stderr.strip()}
        
        # Trả về kết quả từ stdout (nước đi tốt nhất)
        best_move = result.stdout.strip()
        
        if not best_move:
            return {"error": "No move found. Please check the chess engine logic."}
        
        return {"best_move": best_move}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Chess API is running"}