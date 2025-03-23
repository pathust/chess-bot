from PyQt5.QtCore import QThread, pyqtSignal
from chess_engine import find_best_move as find_best_move1
from chess_engine2 import find_best_move as find_best_move2

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
                result = find_best_move1(self.fen, self.depth)
            else:
                result = find_best_move2(self.fen, self.depth)
            self.finished.emit(result)
        except Exception as e:
            print(f"AI Worker error: {str(e)}")
            self.finished.emit("")