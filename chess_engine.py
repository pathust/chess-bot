"""
Chess engine using minimax algorithm with alpha-beta pruning
"""

import math
import sys
from typing import List
from temp_table import TranspositionTable
import chess
import chess.polyglot
from evaluation.static_evaluation import evaluate_board


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

def move_priority(move: chess.Move,
                  board: chess.Board):
    target_piece = board.piece_at(move.to_square)
    if target_piece is not None:  # Nếu nước đi ăn quân
        return   target_piece.piece_type + 1
    elif board.gives_check(move):
        return 5
    elif board.piece_at(move.from_square).piece_type == chess.PAWN:
        return 1  
    return 2  

def null_move_search(board: chess.Board,
                    depth: int,
                    alpha: float,
                    beta: float,
                    killer_moves: list[set],
                    tt: TranspositionTable) -> float:
    """hàm thực hiện null move"""

    #khi không thể nullmove thì trả về âm vô cùng
    if not possible_null_move(board):
        return  -math.inf
    if depth -3 < 0:
        return evaluate_board(board.fen())

    board.push(chess.Move.null())
    #theo các báo cáo R=3 là giá trị tối ưu cho null movemove
    eval = minimax(board, depth - 3, alpha, beta,killer_moves, tt ,False, 0, True, False)
    board.pop()
    return eval

def quiescence_search(board: chess.Board,  
                    alpha: float,
                    beta: float,
                    depth: int,
                    maximizing: bool) -> float:
    """sử dụng sau khi đạt được depth =0"""
    """dừng khi game kết thúc hoặc đạt đến depth giới hạn(tránh stack overflow)"""

    if board.is_game_over() or depth == 0:
        return evaluate_board(board.fen())
    moves_significant = [move for move in board.legal_moves if board.gives_check(move) or board.is_capture(move)]
    if maximizing:
        max_eval = -math.inf
        for move in moves_significant:
            board.push(move)
            eval = quiescence_search(board, alpha, beta, depth-1 , False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
            
        if max_eval == -math.inf:
            max_eval = evaluate_board(board.fen())
        return max_eval
    else:
        min_eval = math.inf
        for move in moves_significant:
            board.push(move)
            eval = quiescence_search(board, alpha, beta, depth-1, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break

        if min_eval == math.inf: 
            min_eval = evaluate_board(board.fen())       
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
        return evaluate_board(board.fen())
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
            max_eval = evaluate_board(board.fen())
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
            min_eval = evaluate_board(board.fen())       
        return min_eval

def sub_zzzzzz_quiescense(board: chess.Board,  
                    maximizing: bool,
                    captured: List[List[bool]] #chỗ này nên là truyền tham chiếu // boolen[9][9]
                    ) -> float:
    
    if board.is_game_over():
        return evaluate_board(board.fen())
    
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
            max_eval = evaluate_board(board.fen())
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
            min_eval = evaluate_board(board.fen())       
        return min_eval

def killer_move_search(
            board: chess.Board,
            depth: int,
            alpha: float,
            beta: float,
            killer_moves: list[set],
            tt: TranspositionTable,
            maximizing_player: bool,
            quiescense_depth: int = 1,
            null_move: bool = False) -> float:
    
    if maximizing_player:
        max_eval = -math.inf        
        for move in killer_moves[depth].copy():
            if not board.is_legal(move):
                continue
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, False, quiescense_depth, null_move, True)# killer search on
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in killer_moves[depth].copy():
            if not board.is_legal(move):
                continue
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, True, quiescense_depth, null_move, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval
    
    

def minimax(board: chess.Board,
            depth: int,
            alpha: float,
            beta: float,
            killer_moves: list[set],
            tt: TranspositionTable,
            maximizing_player: bool,
            quiescense_depth: int = 1,
            use_null_move: bool = False,
            use_killer_move: bool = False) -> float:
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

    zobrist_key = chess.polyglot.zobrist_hash(board)
    entry = tt.lookup(zobrist_key)

    if not (entry is None) :
        return entry['value']

    if board.is_game_over():
        return evaluate_board(board.fen())
    if depth == 0:
        return quiescence_search(board, alpha, beta, quiescense_depth, maximizing_player)
    
    legal_moves = list(board.legal_moves)
    legal_moves = sorted(list(board.legal_moves), key=lambda move: move_priority(move, board), reverse=True)
    best = None
    if maximizing_player:
        #on nullmove branch killer search and quiescense turn off
        if use_null_move and possible_null_move(board):
            null_move_score = null_move_search(board, depth, alpha, beta, killer_moves,tt)  
            max_eval=null_move_score
        else:
            max_eval=-math.inf
        if use_killer_move:
            temp = killer_move_search(board, depth, alpha, beta, killer_moves, tt, maximizing_player, quiescense_depth, use_null_move);    
            if temp>max_eval:
                max_eval=temp    

        for move in legal_moves:
            if use_killer_move and (move in killer_moves[depth] ):
                continue
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, False, quiescense_depth, use_null_move,use_killer_move)
            board.pop()
            if(eval>max_eval):
                max_eval=eval
                best=move
            alpha = max(alpha, eval)
            if beta <= alpha:
                best=move                   
                break
        
        if use_null_move and possible_null_move(board):
            if null_move_score == max_eval:
                return -math.inf
        
        if use_killer_move:
            killer_moves[depth].add(best)
            if depth>2:
                killer_moves[depth-2].add(best) 
        if(depth>3 and use_killer_move):    
            killer_moves[depth-4].clear()

        tt.store(zobrist_key,max_eval,depth,best)
        return max_eval
    else:
        min_eval = math.inf
        if use_killer_move:
            temp = killer_move_search(board, depth, alpha, beta, killer_moves, tt, maximizing_player, quiescense_depth, use_null_move);    
            if temp<min_eval:
                min_eval=temp 

        for move in legal_moves:
            if use_killer_move and (move in killer_moves[depth] ):
                continue
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, True, quiescense_depth, use_null_move, use_killer_move)
            board.pop()
            min_eval = min(min_eval, eval)
            if(min_eval<eval):
                min_eval=eval
                best=move
            beta = min(beta, eval)
            if beta <= alpha:
                best=move                   
                break

        if use_killer_move:
            killer_moves[depth].add(best)
            if depth>2:
                killer_moves[depth-2].add(best) 
        if(depth>3 and use_killer_move):    
            killer_moves[depth-4].clear()


        tt.store(zobrist_key,min_eval,depth,best)
        return min_eval

def find_best_move(fen: str,
                   depth: int,
                   quiescense_depth: int = 1,
                   null_move: bool = False,
                   use_killer_move: bool = False) -> str:
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
    tt = TranspositionTable()  # Tạo một đối tượng TranspositionTable
    killer_moves = [set() for _ in range(depth)]
    for move in board.legal_moves:
        for sub_list in killer_moves:
            sub_list.clear()

        board.push(move)
        board_value = minimax(board, depth - 1, best_value, beta, killer_moves, tt,False, quiescense_depth, null_move,use_killer_move)
        # các loại tham số có dùng quiescense, null_move các kiểu nên chuyển thành global var
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
