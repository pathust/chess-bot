"""
Chess engine using minimax algorithm with alpha-beta pruning
"""

import chess
import math
import sys
from evaluation.init_evaluation import evaluate_board

def minimax(board: chess.Board, 
            depth: int, 
            alpha: float, 
            beta: float, 
            maximizing_player: bool) -> float:
    """
    Minimax algorithm with alpha-beta pruning
    
    Args:
    - board: chess.Board
    - depth: int
    - alpha: float
    - beta: float
    - maximizing_player: bool
    
    Returns:
    - float
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board.fen())

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


def find_best_move(fen: str, depth: int) -> str:
    """
    Find the best move using minimax algorithm
    
    Args:
    - fen: str
    - depth: int
    
    Returns:
    - str
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

"""
Usage:
$ python chess_engine.py "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" 3

Output:
g1f3
"""
if __name__ == "__main__":
    fen = sys.argv[1]
    depth = int(sys.argv[2])

    best_move = find_best_move(fen, depth)
    print(best_move)