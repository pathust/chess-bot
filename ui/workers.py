from PyQt5.QtCore import QThread, pyqtSignal
from bot import ChessBot
import chess

class AIWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, fen, depth, engine_num=1):
        super().__init__()
        self.fen = fen
        self.depth = depth
        self.engine_num = engine_num
        
    def run(self):
        try:
            # Create a fresh chess bot instance each time to prevent state issues
            if self.engine_num == 1:
                chess_bot = ChessBot(initial_fen=self.fen)
            else:
                chess_bot = ChessBot(use_nnue=True, initial_fen=self.fen)
            
            # Make sure the bot has the correct current position
            result = chess_bot.get_best_move(time_ms=5000, depth=self.depth)
            
            # Validate the move
            if result:
                try:
                    # Parse the board and verify this is a legal move
                    board = chess.Board(self.fen)
                    move = chess.Move.from_uci(result)
                    if move not in board.legal_moves:
                        print(f"AI engine returned illegal move: {result}")
                        # Return a random legal move instead
                        legal_moves = list(board.legal_moves)
                        if legal_moves:
                            import random
                            result = legal_moves[random.randint(0, len(legal_moves)-1)].uci()
                        else:
                            result = ""
                except Exception as e:
                    print(f"Error validating move: {str(e)}")
            
            print(f"Search completed, best_move: {result}")
            self.finished.emit(result)
        except Exception as e:
            print(f"AI Worker error: {str(e)}")
            self.finished.emit("")