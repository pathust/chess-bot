from PyQt5.QtCore import QThread, pyqtSignal
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
                result = chess_bot.get_best_move(time_ms=1000)
            else:
                chess_bot = ChessBot(use_nnue=True, initial_fen=self.fen)
                result = chess_bot.get_best_move(time_ms=1000)

            self.finished.emit(result)
        except Exception as e:
            print(f"AI Worker error: {str(e)}")
            self.finished.emit("")