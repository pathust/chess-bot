import torch
import chess
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from evaluation.evaluation import Evaluation

# Load mảng đã lưu
eval_min = np.load("docs/eval_min.npy")
eval_max = np.load("docs/eval_max.npy")

eval = Evaluation()
# c2i=lambda c: (8-int(c[1]),ord(c[0])-97)
# i2c=lambda i,j: chr(j+97)+str(8-i)

# class ConditionalBatchNorm2d(nn.Module):
#     def __init__(self, num_features, num_conditions):
#         super(ConditionalBatchNorm2d, self).__init__()
#         self.num_features = num_features
#         self.bn = nn.BatchNorm2d(num_features, affine=False)
#         self.gamma = nn.Embedding(num_conditions, num_features)
#         self.beta = nn.Embedding(num_conditions, num_features)
#         nn.init.ones_(self.gamma.weight)
#         nn.init.zeros_(self.beta.weight)

#     def forward(self, x, condition):
#         out = self.bn(x)
#         gamma = self.gamma(condition).unsqueeze(-1).unsqueeze(-1)
#         beta = self.beta(condition).unsqueeze(-1).unsqueeze(-1)
#         return gamma * out + beta

# class ChessEvaluationCNN(nn.Module):
#     def __init__(self, num_piece_channels, num_classes, num_conditions):
#         super(ChessEvaluationCNN, self).__init__()
        
#         # Convolutional layers
#         self.conv1 = nn.Conv2d(num_piece_channels, 64, kernel_size=3, padding=1)
#         self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
#         self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        
#         # Conditional batch normalization for active player
#         self.cbn1 = ConditionalBatchNorm2d(64, num_conditions)
#         self.cbn2 = ConditionalBatchNorm2d(128, num_conditions)
#         self.cbn3 = ConditionalBatchNorm2d(256, num_conditions)
        
#         # Fully connected layers
#         self.fc1 = nn.Linear(256, 1024)  # Adjusted from 256 * 8 * 8 to 256
#         self.fc2 = nn.Linear(1024 + 1, num_classes)  # Extra input for halfmove count

#     def forward(self, board_tensor, active_player, halfmove_clock):
#         # First convolution + conditional batch norm + ReLU
#         x = self.conv1(board_tensor)
#         x = self.cbn1(x, active_player)
#         x = F.relu(x)
        
#         # Second convolution + conditional batch norm + ReLU
#         x = self.conv2(x)
#         x = self.cbn2(x, active_player)
#         x = F.relu(x)
        
#         # Third convolution + conditional batch norm + ReLU
#         x = self.conv3(x)
#         x = self.cbn3(x, active_player)
#         x = F.relu(x)
        
#         # Global average pooling
#         x = F.adaptive_avg_pool2d(x, (1, 1))  # Reduce to (batch_size, 256, 1, 1)
#         x = torch.flatten(x, 1)  # Flatten to (batch_size, 256)
        
#         # Fully connected layer
#         x = F.relu(self.fc1(x))  # Input to fc1 is now (batch_size, 256)
        
#         halfmove_clock = halfmove_clock.float()
        
#         # Concatenate halfmove clock and pass through the final fully connected layer
#         x = torch.cat([x, halfmove_clock.unsqueeze(1)], dim=1)
#         output = self.fc2(x)
        
#         return output

# class CNNEvaluation:
#     def __init__(self, model_path="model/chess_model.pth", device=None):
#         self.device = (
#             device if device else
#             torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         )
#         self.model = ChessEvaluationCNN(num_piece_channels=13, num_classes=1, num_conditions=2).to(self.device)  # Initialize the NNUE model
#         self.model.load_state_dict(
#             torch.load(model_path, map_location=self.device)
#         )  # Load the model weights
#         self.model.eval()  # Set the model to evaluation mode

#     # Piece map to encode the board state
#     piece_map = {
#     'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,  # White pieces
#     'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11  # Black pieces
#     }

#     # Encoding FEN string into feature vector
#     def encoding(self, fen):

#         board = chess.Board(fen)
#         board_tensor = torch.zeros((13, 8, 8), dtype=torch.float32)  # 13 channels, 8x8 board

#         d={'K':(7,6),'Q':(7,2),'k':(0,6),'q':(0,2)} #mapping dictionary for castling squares

#         # Fill the tensor based on piece positions
#         for square in chess.SQUARES:
#             piece = board.piece_at(square)
#             if piece:
#                 row = 7 - chess.square_rank(square)  # flip rows
#                 col = chess.square_file(square)
#                 index = self.piece_map[piece.symbol()]
#                 board_tensor[index, row, col] = 1  # mark piece with 1 in the appropriate channel
        
#         #get fen features
#         split=fen.split(' ')
#         active_player = 1 if split[1] == 'w' else 0  # 1 for white, 0 for black
#         en_passant=split[3]
#         castle=split[2]
#         halfmove_clock = int(split[4]) / 100.0  # Normalize by 100
#         #encoding en passant and castling information on the same channel 
#         if en_passant!='-':
#             r,c=c2i(en_passant)
#             board_tensor[12,r,c]=1 #encode en_passant square with 1 if there is any
#         if castle!='-':
#             for piece in castle:
#                 r,c=d[piece]
#                 board_tensor[12,r,c]=1 # casteling squares
                
#         return board_tensor, active_player, halfmove_clock

#     # Evaluate the position given the FEN string using the NNUE model
#     def evaluate(self, board: chess.Board):
#         fen = board.fen()
#         board_tensor, active_player, halfmove_clock = self.encoding(fen)  # Convert FEN to feature vector
#         board_tensor = board_tensor.unsqueeze(0).to(self.device)  # Add batch dimension
#         active_player = torch.tensor([active_player], dtype=torch.long).to(self.device)
#         halfmove_clock = torch.tensor([halfmove_clock], dtype=torch.float32).to(self.device)

#         with torch.no_grad():  # Disable gradient computation for inference
#             output = self.model(board_tensor, active_player, halfmove_clock).to(self.device)  # Forward pass through the model
        # return output.item()  # Return the scalar evaluation score

class NNUE(nn.Module):
    def __init__(self, input_size):
        super(NNUE, self).__init__()
        
        # Reduced number of units in each layer and fewer layers
        self.fc1 = nn.Linear(input_size, 512)  # First hidden layer
        self.fc2 = nn.Linear(512, 256)         # Second hidden layer
        self.fc3 = nn.Linear(256, 128)         # Third hidden layer
        self.fc4 = nn.Linear(128, 64)          # Fourth hidden layer
        self.fc5 = nn.Linear(64, 1)            # Output layer
        
        self.relu = nn.ReLU()
        self.tanh = nn.Tanh()

    def forward(self, x):
        x = self.relu(self.fc1(x))  # First hidden layer
        x = self.relu(self.fc2(x))  # Second hidden layer
        x = self.relu(self.fc3(x))  # Third hidden layer
        x = self.relu(self.fc4(x))  # Fourth hidden layer
        return self.tanh(self.fc5(x))  # Output layer
    
class NNUEEvaluation:
    def __init__(self, model_path="docs/best_model3.pth", device=None):
        self.device = (
            device if device else
            torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model = NNUE(input_size=832).to(self.device)  # Initialize the NNUE model
        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device)
        )  # Load the model weights
        self.model.eval()  # Set the model to evaluation mode

    # Piece map to encode the board state
    piece_map = {"p": 1, "n": 2, "b": 3, "r": 4, "q": 5, "k": 6,
                "P": 7, "N": 8, "B": 9, "R": 10, "Q": 11, "K": 12}
    # Scale the input data using predefined mean and std
    def scale(self, x_data):
        return 2 * (x_data - eval_min) / (eval_max - eval_min) - 1

    # Encoding FEN string into feature vector
    def encoding(self, fen):
        
        # Initialize an empty tensor of shape (13, 8, 8), one for each piece type and additional features
        tensor = torch.zeros(13, 8, 8, dtype=torch.float)
        
        # Create a chess board from the FEN string
        board = chess.Board(fen)
        
        # Fill the tensor with the piece positions from the board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                piece_idx = self.piece_map[piece.symbol()] - 1  # Convert piece symbol to index (0-based)
                row, col = divmod(square, 8)
                tensor[piece_idx, row, col] = 1.0
        
        # Add extra features like castling rights and turn indicator
        tensor[12, 0, 0] = 1.0 if board.turn == chess.WHITE else 0.0  # Whose turn it is
        tensor[12, 0, 1] = 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0
        tensor[12, 0, 2] = 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0
        tensor[12, 0, 3] = 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0
        tensor[12, 0, 4] = 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0
        
        # Add en passant square if available
        if board.ep_square:
            ep_row = board.ep_square // 8
            tensor[12, ep_row, 5] = 1.0
        # You may choose to flatten the tensor if the model expects a 1D vector, 
        # otherwise, you can return the 3D tensor for processing in a CNN or similar architecture
        return tensor.flatten()  # Flatten the tensor to 1D to match input size for the model

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
            output = self.model(encoded_fen)# Forward pass through the model

        return output.item()  # Return the scalar evaluation score
