import chess

class RepetitionTable:
    def __init__(self):
        self.hashes = [0] * 256
        self.start_indices = [0] * (len(self.hashes) + 1)
        self.count = 0

    def init(self, board: chess.Board):
        """Initialize the repetition table with the board's repetition history."""
        initial_hashes = list(reversed(board.repetition_history()))
        self.count = len(initial_hashes)

        for i in range(self.count):
            self.hashes[i] = initial_hashes[i]
            self.start_indices[i] = 0
        self.start_indices[self.count] = 0

    def push(self, hash_value: int, reset: bool):
        """Push a new hash value onto the repetition table."""
        if self.count < len(self.hashes):
            self.hashes[self.count] = hash_value
            self.start_indices[self.count + 1] = self.count if reset else self.start_indices[self.count]
        self.count += 1

    def try_pop(self):
        """Pop the last entry from the repetition table."""
        self.count = max(0, self.count - 1)

    def contains(self, h: int) -> bool:
        """Check if a given hash is already in the repetition table."""
        s = self.start_indices[self.count]
        # up to count-1 to not include the current position
        for i in range(s, self.count - 1):
            if self.hashes[i] == h:
                return True
        return False

# Example usage:

# Create a chess board
board = chess.Board()

# Initialize the repetition table
repetition_table = RepetitionTable()

# Simulate initializing the table with the board's repetition history
repetition_table.init(board)

# Simulate pushing a new hash (e.g., after a move)
new_hash = board.zobrist_hash()  # Assuming the board has a method `zobrist_hash` to get the position hash
repetition_table.push(new_hash, reset=False)

# Simulate checking for repetition
if repetition_table.contains(new_hash):
    print("Repetition detected")
else:
    print("No repetition detected")

# Simulate popping the last position from the table
repetition_table.try_pop()
