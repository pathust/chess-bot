"""
Move history widget for the chess application.
This module provides a widget to display the move history with proper chess notation.
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
import chess

class MoveHistoryWidget(QFrame):
    """Widget to display the move history with improved contrast and proper chess notation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        
        # Create scroll area for move list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Custom styled list widget
        self.move_list = QListWidget()
        self.move_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                alternate-background-color: #f0f0f0;
                font-size: 14pt;
                font-family: 'Arial', sans-serif;
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
        
        scroll_area.setWidget(self.move_list)
        layout.addWidget(scroll_area)
        
    # Update the MoveHistoryWidget.add_move method to improve the format

    def add_move(self, piece, from_square, to_square, color="White", capture=False, 
                check=False, promotion=None, castling=False, en_passant=False):
        """
        Add a move to the history with proper chess notation and improved formatting.
        
        Args:
            piece (chess.Piece): The chess piece being moved
            from_square (str): UCI notation for the source square (e.g., "e2")
            to_square (str): UCI notation for the destination square (e.g., "e4")
            color (str): "White" or "Black" to indicate which player moved
            capture (bool): Whether the move captured a piece
            check (bool): Whether the move gives check
            promotion (int): Chess piece type for pawn promotion (if applicable)
            castling (bool): Whether the move is castling
            en_passant (bool): Whether the move is an en passant capture
        """
        try:
            # Map chess piece types to standard notation symbols
            piece_symbols = {
                chess.PAWN: "",
                chess.KNIGHT: "N",
                chess.BISHOP: "B",
                chess.ROOK: "R",
                chess.QUEEN: "Q",
                chess.KING: "K"
            }
            
            # Map promotion piece types to notation symbols
            promotion_symbols = {
                chess.QUEEN: "Q",
                chess.ROOK: "R", 
                chess.BISHOP: "B",
                chess.KNIGHT: "N"
            }
            
            notation = ""
            
            # Add move number for White moves
            if color == "White":
                move_number = (self.move_list.count() // 2) + 1
                notation = f"{move_number}. "
            
            # Handle castling notation
            if castling:
                # King-side castling (moving right)
                if ord(to_square[0]) > ord(from_square[0]):
                    notation += "O-O"  # King-side
                else:
                    notation += "O-O-O"  # Queen-side
            else:
                # Add piece symbol (except for pawns)
                notation += piece_symbols.get(piece.piece_type, "")
                
                # Add source file for pawns making a capture
                if capture and piece.piece_type == chess.PAWN:
                    notation += from_square[0]
                
                # For enhanced formatting, always add the from square except for castling
                from_coord = from_square
                
                # Add capture symbol if needed
                if capture or en_passant:
                    notation += "x"
                    
                # Add destination square
                notation += to_square
                
                # Add en passant annotation
                if en_passant:
                    notation += " e.p."
                
                # Add promotion piece
                if promotion:
                    notation += "=" + promotion_symbols.get(promotion, "Q")
                    
            # Add check/checkmate symbol
            if check:
                notation += "+"  # For simplicity, we use + for check
                
            # Format the move in the list with improved display
            # New enhanced format showing from-to coordinates
            enhanced_format = f"{from_square}-{to_square}"
            
            if color == "White":
                # Format: "1. e4 (e2-e4)"
                item = QListWidgetItem(f"{notation.ljust(10)} ({enhanced_format})")
                item_color = "#0000aa"  # Dark blue for white's moves
                item.setForeground(QBrush(QColor(item_color)))
                self.move_list.addItem(item)
            else:
                # Update the last item to include the black move
                current_item = self.move_list.item(self.move_list.count() - 1)
                if current_item:
                    current_text = current_item.text()
                    # Format: "1. e4 (e2-e4)    Nc6 (b8-c6)"
                    combined_text = f"{current_text.ljust(25)} {notation} ({enhanced_format})"
                    current_item.setText(combined_text)
                    
                    # Apply custom styling with a bold font
                    font = current_item.font()
                    font.setBold(True)
                    current_item.setFont(font)
                else:
                    # If there's no white move (unlikely but possible in custom positions),
                    # create a new item for black's move
                    move_number = (self.move_list.count()) + 1
                    item = QListWidgetItem(f"{move_number}. ... {notation} ({enhanced_format})")
                    item_color = "#000000"  # Black for black's moves
                    item.setForeground(QBrush(QColor(item_color)))
                    self.move_list.addItem(item)
                
            # Scroll to the bottom to show the latest move
            self.move_list.scrollToBottom()
        except Exception as e:
            print(f"Error adding move to history: {str(e)}")
            # Add a fallback entry if normal notation fails
            if color == "White":
                self.move_list.addItem(f"{from_square}-{to_square}")
            else:
                self.move_list.addItem(f"... {from_square}-{to_square}")

    def clear_history(self):
        """Clear the move history."""
        self.move_list.clear()
        
    def remove_last_move(self):
        """Remove the last move from the history."""
        count = self.move_list.count()
        if count > 0:
            last_item = self.move_list.item(count - 1)
            text = last_item.text()
            
            # Check if the last item has both white and black moves
            if " " in text and not text.startswith(f"{count}."):
                # Extract just the white move part (keep first part before space)
                white_move = text.split(" ", 1)[0]
                last_item.setText(white_move)
                
                # Reset formatting for item with only white's move
                font = last_item.font()
                font.setBold(False)
                last_item.setFont(font)
            else:
                # If it only has one move, remove the entire item
                self.move_list.takeItem(count - 1)