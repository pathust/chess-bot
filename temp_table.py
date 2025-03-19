class TranspositionTable:
    """Basic Transposition table"""
    def __init__(self):
        self.table = {}

    def store(self, zobrist_key, value, depth, best_move=None):
        self.table[zobrist_key] = {
            'value': value,
            'depth': depth,
            'best_move': best_move
        }

    def lookup(self, zobrist_key):
        return self.table.get(zobrist_key, None)


