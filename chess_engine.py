"""
Chess engine using minimax algorithm with alpha-beta pruning
"""

import math
import sys
from typing import List
import chess
from evaluation.init_evaluation import evaluate_board

def possible_null_move(board: chess.Board ) -> bool:
    """Hàm kiểm tra xem có thể thực hiện nullMove không""" 

    #the previous move in the search was also a null move.
    if board.peek() is chess.Move.null():
        return False
    #the side to move is in check
    if board.is_check():
        return False
    other = False
    number_pieces = 0
    #the side to move has only its king and pawns remaining
    #the side to move has a small number of pieces remaining
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == board.turn:
                number_pieces+=1
            if piece.piece_type != chess.PAWN and piece.piece_type != chess.KING:
                other = True
    return other and (number_pieces>4)

def null_move_search(board: chess.Board,
                    depth: int,
                    alpha: float,
                    beta: float) -> float:
    """hàm thực hiện null move"""

    #khi không thể nullmove thì trả về âm vô cùng
    if not possible_null_move(board):
        return  -math.inf
    if depth <= 0:
        return evaluate_board(board)

    board.push(chess.Move.null)
    #theo các báo cáo R=3 là giá trị tối ưu cho null movemove
    eval = minimax(board, depth - 3, alpha, beta, False)
    board.pop()
    alpha = max(alpha, eval)
    return eval

def quiescence_search(board: chess.Board,  
                    alpha: float,
                    beta: float,
                    depth: int,
                    maximizing: bool) -> float:
    """sử dụng sau khi đạt được depth =0"""
    """dừng khi game kết thúc hoặc đạt đến depth giới hạn(tránh stack overflow)"""

    if board.is_game_over() or depth == 0:
        return evaluate_board(board)
    legal_moves = list(board.legal_moves)
    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            if(board.gives_check(move) or board.is_capture(move)):
                board.push(move)
                eval = quiescence_search(board, alpha, beta, depth-1 , False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        if max_eval == -math.inf:
            max_eval = evaluate_board(board)
        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            if(board.is_capture(move)):    
                board.push(move)
                eval = quiescence_search(board, alpha, beta, depth-1, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        if min_eval == math.inf: 
            min_eval = evaluate_board(board)       
        return min_eval

def zzzzzz_quiescence_search(board: chess.Board,  
                    alpha: float,
                    beta: float,
                    depth: int,
                    maximizing: bool,
                    captured: List[List[bool]] #chỗ này nên là truyền tham chiếu // boolen[9][9]
                    ) -> float:
    """sử dụng sau khi đạt được depth =0"""
    """chỉ cho tự do ăn và chiếu depth lần, những quân ăn và chiếu sẽ bị đánh dấu, sau depth lần chỉ xét những nước ăn những quân đó """

    if board.is_game_over():
        return evaluate_board(board)
    #if depth = 0 do eval
    if depth==0:
        sub_zzzzzz_quiescense(board, maximizing, captured)
    legal_moves = list(board.legal_moves)
    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            if(board.gives_check(move) or board.is_capture(move)):
                temp = move.uci()
                board.push(move)
                #lưu trữ trạng thái các quân cờ đã bị đánh dấu chưa trước khi di chuyển
                old_1 = captured[temp[1]][ord(temp[0])]
                old_2 = captured[temp[3]][ord(temp[2])]
                captured[temp[3]][ord(temp[2])]=True
                captured[temp[1]][ord(temp[0])]=False
                eval = zzzzzz_quiescence_search(board, alpha, beta, depth-1 , False, captured)

                board.pop()
                #trả lại trạng thái sau khi di quay lui
                captured[temp[1]][ord(temp[0])] = old_1
                captured[temp[3]][ord(temp[2])] = old_2

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        if max_eval == -math.inf:
            max_eval = evaluate_board(board)
        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            if(board.gives_check(move) or board.is_capture(move)):
                temp = move.uci() 
                board.push(move)
                old_1 = captured[temp[1]][ord(temp[0])]
                old_2 = captured[temp[3]][ord(temp[2])]
                captured[temp[3]][ord(temp[2])]=True
                captured[temp[1]][ord(temp[0])]=False
                eval = zzzzzz_quiescence_search(board, alpha, beta, depth-1, True, captured)
                board.pop()
                captured[temp[1]][ord(temp[0])] = old_1
                captured[temp[3]][ord(temp[2])] = old_2

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        if min_eval == math.inf: 
            min_eval = evaluate_board(board)       
        return min_eval

def sub_zzzzzz_quiescense(board: chess.Board,  
                    maximizing: bool,
                    captured: List[List[bool]] #chỗ này nên là truyền tham chiếu // boolen[9][9]
                    ) -> float:
    
    if board.is_game_over():
        return evaluate_board(board)
    
    legal_moves = list(board.legal_moves)
    if maximizing:
        max_eval = -math.inf
        for move in legal_moves:
            # neu captured true nghia la an duoc quan co frag
            if(captured[temp[3]][ord(temp[2])]):
                temp = move.uci()
                board.push(move)
                old_1 = captured[temp[1]][ord(temp[0])]
                captured[temp[1]][ord(temp[0])]=False
                eval = sub_zzzzzz_quiescense(board, False, captured)
                board.pop()
                captured[temp[1]][ord(temp[0])] = old_1

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        if max_eval == -math.inf:
            max_eval = evaluate_board(board)
        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            if(board.is_capture(move)):   
                temp = move.uci()
                board.push(move)
                old_1 = captured[temp[1]][ord(temp[0])]
                captured[temp[1]][ord(temp[0])]=False
                eval = sub_zzzzzz_quiescense(board, True, captured)
                board.pop()
                captured[temp[1]][ord(temp[0])] = old_1

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        if min_eval == math.inf: 
            min_eval = evaluate_board(board)       
        return min_eval

def minimax(board: chess.Board,
            depth: int,
            alpha: float,
            beta: float,
            maximizing_player: bool,
            quiescense_depth: int = 1,
            null_move: bool = False) -> float:
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
    if board.is_game_over():
        return evaluate_board(board.fen())
    if depth == 0:
        quiescence_search(board, alpha, beta, quiescense_depth, maximizing_player)

    legal_moves = list(board.legal_moves)

    if maximizing_player:
        max_eval = null_move_search(board, depth, alpha,beta) if null_move else -math.inf
        null_move_Search=max_eval
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        if(null_move_search==max_eval):
            max_eval=-math.inf
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


def find_best_move(fen: str,
                   depth: int,
                   quiescense_depth: int = 1,
                   null_move: bool = False) -> str:
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
        board_value = minimax(board, depth - 1, alpha, beta, False, quiescense_depth, null_move)
        board.pop()

        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move.uci() if best_move else None


# Usage:
# $ python chess_engine.py "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" 3 5 True

# Output:
# g1f3

if __name__ == "__main__":
    FEN = sys.argv[1]
    DEPTH = int(sys.argv[2])
    QUIESCENCE_DEPTH = int(sys.argv[3])
    NULL_MOVE = bool(sys.argv[4])

    BEST_MOVE = find_best_move(FEN, DEPTH, QUIESCENCE_DEPTH, NULL_MOVE)
    print(BEST_MOVE)
