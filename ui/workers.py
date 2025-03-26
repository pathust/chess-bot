from PyQt5.QtCore import QThread, pyqtSignal
from chess_engine import find_best_move
from bot import ChessBot

class AIWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, fen, depth, engine_num=1):
        super().__init__()
        self.fen = fen
        self.depth = depth
        self.engine_num = engine_num

    def run(self):
        try:
            if self.engine_num == 1:
                chess_bot = ChessBot(self.fen)
                result = chess_bot.get_best_move(depth=3)
            else:
                result = find_best_move(self.fen, self.depth)

            self.finished.emit(result)
        except Exception as e:
            print(f"AI Worker error: {str(e)}")
            self.finished.emit("")