import chess
import math
import sys

# Define basic evaluation for the board
def evaluate_board(board: chess.Board) -> int:
    """
    A basic board evaluation function that calculates the material balance.
    
    Args:
    - board: chess.Board
    
    Returns:
    - int: The evaluation score of the board
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # We don't evaluate the king in this simple evaluation
    }
    
    evaluation = 0

    # Loop through all the pieces and calculate material balance
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Add piece value if it's white, subtract if it's black
            value = piece_values.get(piece.piece_type, 0)
            if piece.color == chess.WHITE:
                evaluation += value
            else:
                evaluation -= value

    return evaluation

# Minimax with alpha-beta pruning
def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
    """
    Minimax algorithm with alpha-beta pruning to find the best move.
    
    Args:
    - board: chess.Board
    - depth: int
    - alpha: int
    - beta: int
    - maximizing_player: bool
    
    Returns:
    - int: The evaluation score for the board at this depth
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
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

# Find the best move
def find_best_move(fen: str, depth: int) -> str:
    """
    Find the best move using the minimax algorithm with alpha-beta pruning.
    
    Args:
    - fen: str
    - depth: int
    
    Returns:
    - str: The best move in UCI format (e.g., 'e2e4')
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

# Entry point when running as a script
if __name__ == "__main__":
    try:
        # Get FEN and depth from command-line arguments
        fen = sys.argv[1]  # FEN string
        depth = int(sys.argv[2])  # Search depth

        # Find the best move
        best_move = find_best_move(fen, depth)
        print(best_move)  # Print the best move to stdout (UCI format)
    except Exception as e:
        print(f"Error: {e}")