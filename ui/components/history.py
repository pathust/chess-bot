from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
import chess

class MoveHistoryWidget(QFrame):
    """Widget to display the move history with improved contrast"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #cccccc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Title container with improved visibility
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                border: 1px solid #1a2530;
            }
        """)
        
        title_layout = QVBoxLayout(title_container)
        
        # Title label
        title = QLabel("Move History")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: white; 
            padding: 5px;
        """)
        title_layout.addWidget(title)
        layout.addWidget(title_container)
        
        # Custom styled list widget
        self.move_list = QListWidget()
        self.move_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                alternate-background-color: #f0f0f0;
                font-size: 14pt;
                font-family: 'Arial', monospace;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                color: #222222;
                padding: 5px;
                border-bottom: 1px solid #e0e0e0;
                min-height: 30px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6f7ff;
            }
            QListWidget::item:alternate {
                background-color: #f5f5f5;
            }
        """)
        self.move_list.setAlternatingRowColors(True)
        layout.addWidget(self.move_list)
        
    def add_move(self, piece, from_square, to_square, color="White", capture=False, check=False, promotion=None, castling=False):
        """Add a move to the history with proper chess notation"""
        piece_symbols = {
            chess.PAWN: "",
            chess.KNIGHT: "N",
            chess.BISHOP: "B",
            chess.ROOK: "R",
            chess.QUEEN: "Q",
            chess.KING: "K"
        }
        
        notation = ""
        
        # Add move number for White moves
        if color == "White":
            move_number = (self.move_list.count() // 2) + 1
            notation = f"{move_number}. "
        
        # Handle castling notation
        if castling:
            if to_square[0] > from_square[0]:  # King-side castling
                notation += "O-O"
            else:  # Queen-side castling
                notation += "O-O-O"
        else:
            # Add piece symbol
            notation += piece_symbols.get(piece.piece_type, "")
            
            # Add capture symbol
            if capture:
                if piece.piece_type == chess.PAWN:
                    notation += from_square[0] + "x"
                else:
                    notation += "x"
                    
            # Add destination square
            notation += to_square
            
            # Add promotion piece
            if promotion:
                notation += "=" + piece_symbols.get(promotion, "")
                
        # Add check/checkmate symbol
        if check:
            notation += "+"
            
        # Format the move in the list with improved styling
        if color == "White":
            item = QListWidgetItem(f"{notation.ljust(12)}")
            item_color = "#0000aa"  # Dark blue for white's moves
            item.setForeground(QBrush(QColor(item_color)))
            self.move_list.addItem(item)
        else:
            # Update the last item to include the black move
            current_item = self.move_list.item(self.move_list.count() - 1)
            if current_item:
                current_text = current_item.text()
                combined_text = f"{current_text} {notation}"
                current_item.setText(combined_text)
                
                # Apply custom styling with a bold font
                font = current_item.font()
                font.setBold(True)
                current_item.setFont(font)
            
        # Scroll to the bottom
        self.move_list.scrollToBottom()

    def clear_history(self):
        """Clear the move history"""
        self.move_list.clear()