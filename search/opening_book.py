import chess
import chess.polyglot
import os
import random
from random import choices

class OpeningBook:
    def __init__(self, path):
        self.path = path
        self.reader = None
        if os.path.exists(path):
            try:
                self.reader = chess.polyglot.open_reader(path)
            except Exception as e:
                print(f"Error opening book: {e}")
                self.reader = None

    def get_move_info(self, board):
        if not self.reader:
            return
        try:
            entries = list(self.reader.find_all(board))  # Lấy tất cả entries
            print(f"FEN: {board.fen()}")
            for entry in entries:
                move = entry.move
                weight = entry.weight
                learn = entry.learn
                print(f"Move: {move.uci()} | Weight: {weight} | Learn: {learn}")
            print("-" * 50)
        except Exception as e:
            print(f"Error getting move from book: {e}")

    def get_weighted_book_move(self, board):
        """Trả về một nước đi từ book theo trọng số `weight`."""
        if not self.reader:
            return None
        try:
            entries = list(self.reader.find_all(board))
            if not entries:
                return None

            moves = [entry.move for entry in entries]
            weights = [entry.weight for entry in entries]

            if sum(weights) == 0:
                return random.choice(moves)

            return choices(moves, weights=weights, k=1)[0]
        except Exception as e:
            print(f"Error selecting book move: {e}")
            return None