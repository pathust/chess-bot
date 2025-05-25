import chess
import json
import numpy as np



class PieceSquareTable:

    path="evaluation/piece_square_weight.json"
    # Các bảng điểm cho từng quân cờ
    pawns = [
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         5,  10,  10, -20, -20,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ]
    
    pawns_end = [
         0,   0,   0,   0,   0,   0,   0,   0,
        80,  80,  80,  80,  80,  80,  80,  80,
        50,  50,  50,  50,  50,  50,  50,  50,
        30,  30,  30,  30,  30,  30,  30,  30,
        20,  20,  20,  20,  20,  20,  20,  20,
        10,  10,  10,  10,  10,  10,  10,  10,
        10,  10,  10,  10,  10,  10,  10,  10,
         0,   0,   0,   0,   0,   0,   0,   0
    ]

    rooks = [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0
    ]

    knights = [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ]

    bishops = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ]

    queens = [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ]

    king_start = [
        -80, -70, -70, -70, -70, -70, -70, -80,
        -60, -60, -60, -60, -60, -60, -60, -60,
        -40, -50, -50, -60, -60, -50, -50, -40,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, -5, -5, -5, -5, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20
    ]

    king_end = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -5, 0, 5, 5, 5, 5, 0, -5,
        -10, -5, 20, 30, 30, 20, -5, -10,
        -15, -10, 35, 45, 45, 35, -10, -15,
        -20, -15, 30, 40, 40, 30, -15, -20,
        -25, -20, 20, 25, 25, 20, -20, -25,
        -30, -25, 0, 0, 0, 0, -25, -30,
        -50, -30, -30, -30, -30, -30, -30, -50
    ]

    tables = [pawns,pawns_end,rooks,knights,bishops,queens,king_start,king_end]

    @staticmethod
    def read(table, square: int, is_white: bool):
        if is_white:
            square = chess.square(chess.square_file(square), 7 - chess.square_rank(square))
        return table[square]

    @staticmethod
    def __init__():
        PieceSquareTable.tables = [None] * 6  # 6 quân cờ: Pawn, Rook, Knight, Bishop, Queen, King
        PieceSquareTable.tables[0] = PieceSquareTable.pawns  # Pawn
        PieceSquareTable.tables[1] = PieceSquareTable.rooks  # Rook
        PieceSquareTable.tables[2] = PieceSquareTable.knights  # Knight
        PieceSquareTable.tables[3] = PieceSquareTable.bishops  # Bishop
        PieceSquareTable.tables[4] = PieceSquareTable.queens  # Queen
        PieceSquareTable.tables[5] = PieceSquareTable.king_start  # King (start position)

    @staticmethod
    def get_flipped_table(table):
        """Lật bảng điểm cho quân cờ đối phương"""
        flipped_table = [0] * len(table)
        for i in range(len(table)):
            flipped_coord = chess.Square(63 - i)  # Đảo vị trí quân cờ
            flipped_table[flipped_coord] = table[i]
        return flipped_table

    @staticmethod
    def piece_square_value(piece, square):
        """Trả về giá trị của một quân cờ ở một ô cụ thể"""
        return PieceSquareTable.tables[piece][square]
    
    @staticmethod
    def update(weights:np.array):
        """update giá trị từ array"""
        for i, table in enumerate(PieceSquareTable.tables):
            for j in range(64):
                index = i*64 +j
                PieceSquareTable.tables[i][j] =weights[index]

    @staticmethod
    def tables_to_array():
        # Kết hợp tất cả các bảng thành một mảng 1D numpy array
        return np.array([value for table in PieceSquareTable.tables for value in table])
    
    @staticmethod
    def to_dict():
        """Chuyển tables thành list các dict dạng vị trí(theo kiểu bản cờ vd a1, g5,...): value,"""
        return [
            {chess.square_name(i): table[i] for i in range(64)}
            for table in PieceSquareTable.tables
        ]

    @staticmethod
    def save_to_json(path):
        """Lưu tables ra file JSON"""
        data = PieceSquareTable.to_dict()
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load_from_json():
        """Load tables từ file JSON"""
        try:
            pass
        except Exception:
            print("co loi trong load file PieceSquareTable")
    
