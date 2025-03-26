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



use_null_move: bool = False
use_killer_move: bool = False
use_pvs: bool = False
use_transposition_table:bool = False
use_moveorder:bool = False
depth_pvs:int=0

evalue_time = 0
pruning_time =0
number_node=0

def evalue_inc():
    global evalue_time
    evalue_time =evalue_time+1

def prun_inc():
    global pruning_time
    pruning_time =pruning_time+1

def node_inc():
    global number_node
    number_node =number_node+1

def set_find_technique(_use_null_move: bool=False,
                       _use_killer_move: bool=False,
                       _use_pvs:bool = False,
                       _use_transposition_table:bool = False,
                       _use_moveorder:bool = False,
                       _depth:int = 0) -> bool:
    global use_null_move
    global use_killer_move
    global use_pvs
    global use_transposition_table
    global use_moveorder
    global depth_pvs
    use_null_move=_use_null_move
    use_killer_move=_use_killer_move
    use_pvs=_use_pvs
    use_transposition_table=_use_transposition_table
    use_moveorder=_use_moveorder
    depth_pvs=_depth/2

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

"""killer move đã được tích hợp vào move order với add Score"""
def move_priority(move: chess.Move,
                  board: chess.Board,
                  killer_moves: list[set],
                  depth: int
                  ):
    target_piece = board.piece_at(move.to_square)
    addScore=0
    if move in killer_moves[depth]:
        addScore=3
    if target_piece is not None:  # Nếu nước đi ăn quân
        return   target_piece.piece_type + addScore
    elif board.gives_check(move):
        return 5+addScore
    elif board.piece_at(move.from_square).piece_type == chess.PAWN:
        return 2+addScore
    return 1 +addScore

def null_move_search(board: chess.Board,
                    depth: int,
                    alpha: float,
                    beta: float,
                    killer_moves: list[set],
                    tt: TranspositionTable,
                    use_pvs: bool,
                    maximizing:bool = True
                    ) -> float:
    """hàm thực hiện null move"""

    #khi không thể nullmove thì trả về âm vô cùng
    if not possible_null_move(board):
        if maximizing:
            return  -math.inf
        else:
            return math.inf
    if depth -3 < 0:
        return evaluate_board(board.fen())

    board.push(chess.Move.null())
    #theo các báo cáo R=3 là giá trị tối ưu cho null movemove
    if use_pvs:
        eval=pvs(board,depth-2,alpha,beta,killer_moves,tt,not maximizing)
    else:
        eval = minimax(board, depth - 3, alpha, beta,killer_moves, tt ,not maximizing, 0, False)
        #trên nhánh null move không cho add thêm vào killer move
    board.pop()
    return eval

def quiescence_search(board: chess.Board,  
                    alpha: float,
                    beta: float,
                    depth: int,
                    maximizing: bool) -> float:
    """sử dụng sau khi đạt được depth =0"""
    """dừng khi game kết thúc hoặc đạt đến depth giới hạn(tránh stack overflow)"""
    node_inc()
    if board.is_game_over() or depth == 0:
        evalue_inc()
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
                prun_inc()
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
                prun_inc()
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

"""giống minimax nhưng với pvs nullmove không dùng trong minimax, 
k quiescense, k lưu kết quả vào bảng băm, chỉ xét small window (alpha, alpha+1) và (beta, beta+1)"""
def pvs(board: chess.Board,
            depth: int,
            alpha: float,
            beta: float,
            killer_moves: list[set],
            tt: TranspositionTable,
            maximizing_player: bool) -> float:
    node_inc()
    global use_killer_move
    global use_transposition_table
    global use_null_move
    global use_moveorder
    global depth_pvs
    #dùng bảng băm tra trạng thái
    if use_transposition_table:
        zobrist_key = chess.polyglot.zobrist_hash(board)
        entry = tt.lookup(zobrist_key)
        if not (entry is None):
            if entry['depth']+2 >= depth:
                return entry['value']
            else:
                killer_moves[depth].add(entry['best_move'])

    if board.is_game_over() or depth <= depth_pvs:
        evalue_inc()
        return evaluate_board(board.fen())

    if use_moveorder:
        legal_moves = sorted(list(board.legal_moves), key=lambda move: move_priority(move, board,killer_moves,depth), reverse=True)
    else:
        legal_moves = list(board.legal_moves)
    best=chess.Move.null()
    if maximizing_player:
        if(use_null_move):
            max_eval = null_move_search(board, depth, alpha, beta, killer_moves,tt,True,True)  
        else:
            max_eval=-math.inf

        for move in legal_moves:
            board.push(move)
            eval = pvs(board, depth - 1, alpha, beta, killer_moves, tt, False)
            board.pop()
            if(eval>max_eval):
                best=move
                max_eval=eval
            alpha = max(alpha, eval)
            if beta <= alpha:
                prun_inc()
                break
        
        if use_killer_move:
            if(not best is chess.Move.null()):
                killer_moves[depth].add(best)
            if depth>2:
                killer_moves[depth-2].clear()

        return max_eval
    else:
        if(use_null_move):
            min_eval = null_move_search(board, depth, alpha, beta, killer_moves,tt,True,False)  
        else:
            min_eval=math.inf

        for move in legal_moves:
            board.push(move)
            eval = pvs(board, depth - 1, alpha, beta, killer_moves, tt, True)
            board.pop()
            if(eval<min_eval):
                best=move
                min_eval = eval
            beta = min(beta, eval)
            if beta <= alpha:
                prun_inc()
                break

        if use_killer_move:
            killer_moves[depth].add(best)
            if depth>2:
                killer_moves[depth-2].clear() 
        return min_eval

def minimax(board: chess.Board,
            depth: int,
            alpha: float,
            beta: float,
            killer_moves: list[set],
            tt: TranspositionTable,
            maximizing_player: bool,
            quiescense_depth: int = 1,
            allow_add_best_move: bool=True) -> float:
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
    node_inc()
    global use_null_move
    global use_killer_move
    global use_pvs
    global use_transposition_table
    #Transposition table
    if use_transposition_table:
        zobrist_key = chess.polyglot.zobrist_hash(board)
        entry = tt.lookup(zobrist_key)
        if not (entry is None):
            #nếu depth đã search kém hơn không quá nhiều thì k search lại
            if entry['depth'] +2 >= depth:
                return entry['value']
            else:
                killer_moves[depth].add(entry['best_move'])

    if board.is_game_over():
        evalue_inc()
        return evaluate_board(board.fen())
    if depth == 0:
        return quiescence_search(board, alpha, beta, quiescense_depth, maximizing_player)
    
    if use_moveorder:
        legal_moves = sorted(list(board.legal_moves), key=lambda move: move_priority(move, board,killer_moves,depth), reverse=True)
    else:
        legal_moves = list(board.legal_moves)    
        
    best = None
    if(use_pvs): 
        first = True

    if maximizing_player:
        if (not use_pvs) and use_null_move:
            #on nullmove branch killer search and quiescense turn off
            null_move_score = null_move_search(board, depth, alpha, beta, killer_moves,tt,use_pvs)  
            max_eval=null_move_score            
        else:
            max_eval=-math.inf

        for move in legal_moves:
            board.push(move)
            #pvs search
            if(use_pvs):
                if first:
                    eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, False, quiescense_depth, allow_add_best_move)
                    first=False
                else:
                    eval = pvs(board, depth - 1, alpha, alpha+1, killer_moves, tt, False)
                    if(eval>alpha and eval<beta):
                        eval=minimax(board, depth - 1, alpha, beta, killer_moves, tt, False, quiescense_depth,allow_add_best_move)

            #normal minimax
            else:
                eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, False, quiescense_depth,allow_add_best_move)
            
            board.pop()
            if(eval>max_eval):
                max_eval=eval
                best=move
            alpha = max(alpha, eval)
            if beta <= alpha:
                prun_inc()
                best=move                   
                break
        
        #nếu đã nhường 1 nhưng đối thủ không tăng trạng thái đối phương lên được thì cắt tỉa(cần xem lại)
        if (not use_pvs) and use_null_move:
            if null_move_score == max_eval:
                return -math.inf
        #thêm best move vào set killer_move
        if use_killer_move and allow_add_best_move:
            killer_moves[depth].add(best)
            if depth>2:
                killer_moves[depth-2].clear()
        #thêm các giá trị tính được vào transposition table 
        if use_transposition_table:
            tt.store(zobrist_key,max_eval,depth,best)

        return max_eval
    else:
        min_eval = math.inf
        for move in legal_moves:
            board.push(move)
            #pvs search 
            if(use_pvs):
                if first:
                    first=False
                    eval =  minimax(board, depth - 1, alpha, beta, killer_moves, tt, True, quiescense_depth, allow_add_best_move)
                else:
                    eval = pvs(board, depth - 1, beta-1,beta, killer_moves, tt, True)
                    if(eval>alpha and eval<beta):
                        eval=minimax(board, depth - 1, alpha, beta, killer_moves, tt, True, quiescense_depth, allow_add_best_move)
            #normal minimax
            else:
                eval = minimax(board, depth - 1, alpha, beta, killer_moves, tt, True, quiescense_depth, allow_add_best_move)
            
            board.pop()
            min_eval = min(min_eval, eval)
            if(min_eval<eval):
                min_eval=eval
                best=move
            beta = min(beta, eval)
            if beta <= alpha:
                prun_inc()
                best=move                   
                break

        if use_killer_move and allow_add_best_move:
            killer_moves[depth].add(best)
            if depth>2:
                killer_moves[depth-2].clear()

        if use_transposition_table:
            tt.store(zobrist_key,min_eval,depth,best)
        return min_eval

def find_best_move(fen: str,
                   depth: int,
                   quiescense_depth: int = 1,
                   _use_null_move: bool = False,
                   _use_killer_move: bool = True,
                   _use_pvs:bool = True,
                   _use_transposition_table:bool = True,
                   _use_moveorder:bool = True) -> str:
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
    #đặt các kỹ thuật sử dụng =True vào biến global
    set_find_technique(_use_null_move,_use_killer_move,_use_pvs,_use_transposition_table,_use_moveorder,depth)

    killer_moves = [set() for _ in range(depth)]
    for move in board.legal_moves:
        for sub_list in killer_moves:
            sub_list.clear()

        board.push(move)
        board_value = minimax(board, depth - 1, best_value, beta, killer_moves, tt,False, quiescense_depth)
        # các loại tham số có dùng quiescense, null_move các kiểu nên chuyển thành global var
        board.pop()
        
        if board_value > best_value:
            best_value = board_value
            best_move = move

    global evalue_time
    global pruning_time
    global number_node
    print("evaluate time:")
    print(evalue_time)
    print("prun time:")
    print(pruning_time)
    print("max point")
    print(best_value)
    print("number node")
    print(number_node)

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