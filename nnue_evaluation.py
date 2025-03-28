import torch
import chess
import torch.nn as nn
import numpy as np
from model.config import mui, std

class NNUE(nn.Module):
    def __init__(self, input_size=128):
        super(NNUE, self).__init__()
        self.fc1 = nn.Linear(input_size, 1024)
        self.fc2 = nn.Linear(1024, 512)
        self.fc3 = nn.Linear(512, 256)
        self.fc4 = nn.Linear(256, 128)
        self.fc5 = nn.Linear(128, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.relu(self.fc4(x))
        return self.fc5(x)

class NNUEEvaluation:
    def __init__(self, model_path="model/best_nnue.pth", device=None):
        self.device = (
            device if device else
            torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model = NNUE(input_size=128).to(self.device)  # Initialize the NNUE model
        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device)
        )  # Load the model weights
        self.model.eval()  # Set the model to evaluation mode

    # Piece map to encode the board state
    piece_map = {
        "p": -1, "n": -2, "b": -3, "r": -4, "q": -5, "k": -6,
        "P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "K": 6
    }

    # Scale the input data using predefined mean and std
    def scale(self, x_data):
        return (x_data - mui) / std

    # Encoding FEN string into feature vector
    def encoding(self, fen):
        board = fen.split()[0]
        encoded = np.zeros(128, dtype=np.float32)  # Flatten the board to 128 features

        squares = []
        for row in board.split("/"):
            for char in row:
                if char.isdigit():
                    squares.extend([None] * int(char))
                else:
                    squares.append(char)

        for i, piece in enumerate(squares):
            if piece:
                encoded[i * 2] = self.piece_map[piece]  # First channel for piece type
                encoded[i * 2 + 1] = 1 if piece.isupper() else -1  # Second channel for color

        return encoded

    # Evaluate the position given the FEN string using the NNUE model
    def evaluate(self, board: chess.Board):
        fen = board.fen()
        encoded_fen = self.encoding(fen)  # Convert FEN to feature vector
        encoded_fen = self.scale(encoded_fen)  # Normalize the feature vector
        encoded_fen = torch.tensor(
            encoded_fen,
            dtype=torch.float32
        ).to(self.device)  # Convert to tensor and move to device

        with torch.no_grad():  # Disable gradient computation for inference
            output = self.model(encoded_fen)  # Forward pass through the model

        return output.item()  # Return the scalar evaluation score
