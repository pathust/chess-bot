from PyQt5.QtCore import QThread, pyqtSignal
from bot import ChessBot

class AIWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, fen, depth, engine_num=1):
        super().__init__()
        self.fen = fen
        self.depth = depth
        self.engine_num = engine_num
        self.white_bot = ChessBot(initial_fen=self.fen)
        self.black_bot = ChessBot(use_nnue=True, initial_fen=self.fen)

    def run(self):
        try:
            chess_bot = self.white_bot if self.engine_num == 1 else self.black_bot
            chess_bot.set_position(self.fen)
            result = chess_bot.get_best_move(time_ms=5000, depth=self.depth)
            self.finished.emit(result)
        except Exception as e:
            print(f"AI Worker error: {str(e)}")
            self.finished.emit("")