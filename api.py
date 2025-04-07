"""
Chess API for external communication.
This module provides a REST API for interacting with the chess engine.
"""

from fastapi import FastAPI, HTTPException
import subprocess
import logging
import sys
import os
import chess

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Chess API",
    description="API for chess move analysis and engine interaction",
    version="1.0.0"
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("chess_api")

@app.post("/move/")
async def get_best_move(fen: str, depth: int = 3):
    """
    API endpoint to get the best move for a given chess position.
    
    Args:
        fen (str): FEN string representing the chess board.
        depth (int): Depth of the minimax search (1-5).
        
    Returns:
        dict: The best move in UCI format or an error message.
    """
    logger.info(f"Received request for position: {fen}, depth: {depth}")
    
    # Validate FEN string
    try:
        chess.Board(fen)
    except ValueError as e:
        logger.error(f"Invalid FEN string: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid FEN string: {str(e)}")
    
    # Validate depth
    if depth < 1 or depth > 5:
        logger.error(f"Invalid depth: {depth}. Must be between 1 and 5.")
        raise HTTPException(status_code=400, detail="Depth must be between 1 and 5")
    
    try:
        # Call chess_engine.py as a separate process with FEN and depth parameters
        logger.info(f"Running engine with depth {depth}")
        result = subprocess.run(
            ["python3", "chess_engine.py", fen, str(depth)],
            capture_output=True,
            text=True,
            timeout=60  # Set a timeout to prevent hanging
        )

        # Check for errors from stderr
        if result.stderr:
            logger.error(f"Engine error: {result.stderr.strip()}")
            return {"error": result.stderr.strip()}
        
        # Return the result from stdout (best move)
        best_move = result.stdout.strip()
        logger.info(f"Engine returned move: {best_move}")
        
        if not best_move:
            logger.warning("No move found by engine")
            return {"error": "No move found. Please check the chess engine logic."}
        
        # Validate the returned move
        try:
            board = chess.Board(fen)
            move = chess.Move.from_uci(best_move)
            if move not in board.legal_moves:
                logger.error(f"Engine returned illegal move: {best_move}")
                return {"error": f"Engine returned illegal move: {best_move}"}
        except ValueError as e:
            logger.error(f"Invalid move format: {str(e)}")
            return {"error": f"Invalid move format: {str(e)}"}
        
        return {"best_move": best_move}
    except subprocess.TimeoutExpired:
        logger.error("Engine process timed out")
        return {"error": "Engine computation timed out"}
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": str(e)}

@app.get("/")
async def read_root():
    """Root endpoint to check if the API is running."""
    return {"message": "Chess API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)