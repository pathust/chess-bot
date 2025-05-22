"""
Background worker for AI chess move computation.
This module handles running AI calculations in a separate thread to prevent UI freezing.
"""

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
import chess
import traceback
import time

from utils.config import Config

class AIWorker(QThread):
    """
    Worker thread for computing AI chess moves in the background.
    
    Signals:
        finished(str): Emitted when computation is complete with the best move in UCI format
        error(str): Emitted when an error occurs during computation
        progress(int): Emitted to report computation progress (0-100)
    """
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, fen, depth, engine_num=1, parent=None):
        """
        Initialize the AI worker.
        
        Args:
            fen (str): FEN string representing the chess position
            depth (int): Search depth for the AI
            engine_num (int, optional): Which engine to use (1 or 2). Defaults to 1.
            parent (QObject, optional): Parent object. Defaults to None.
        """
        super().__init__(parent)
        self.fen = fen
        self.depth = depth
        self.engine_num = engine_num
        self._canceled = False
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()
        self._paused = False
        self.chess_bot = None
        
    def run(self):
        """Execute the AI computation in a background thread."""
        try:
            # Importing here to avoid circular imports
            from bot import ChessBot
            
            # Report starting progress
            self.progress.emit(10)
            
            # Create a fresh chess bot instance each time to prevent state issues
            if self.engine_num == 1:
                self.chess_bot = ChessBot(initial_fen=self.fen, opening_book_path="resources/komodo.bin")
            else:
                self.chess_bot = ChessBot(initial_fen=self.fen)
            
            # Report initialization complete
            self.progress.emit(20)
            
            # Check if already canceled before starting computation
            if self._canceled:
                self.finished.emit("")
                return
                
            # Calculate the estimated thinking time based on depth
            thinking_time = Config.AI_THINKING_TIME
            
            # Get the best move with a custom callback to support cancellation
            result = ""
            
            def move_chosen_callback(move_uci):
                nonlocal result
                result = move_uci
            
            # Set the callback
            self.chess_bot.on_move_chosen = move_chosen_callback
            
            # Start thinking process instead of blocking call
            self.chess_bot.think_timed(thinking_time)
            
            # Wait until move is found or canceled
            start_time = time.time()
            while not result and not self._canceled and (time.time() - start_time) < (thinking_time / 1000) + 5:
                # Check for pause
                self.mutex.lock()
                if self._paused:
                    self.pause_condition.wait(self.mutex)
                self.mutex.unlock()
                
                # Send progress updates
                elapsed = time.time() - start_time
                progress = min(80, 20 + int(elapsed / (thinking_time / 1000) * 60))
                self.progress.emit(progress)
                
                # Sleep a bit to reduce CPU usage
                time.sleep(0.1)
            
            # If canceled, terminate the bot's thinking
            if self._canceled:
                if self.chess_bot:
                    self.chess_bot.stop_thinking()
                self.finished.emit("")
                return
            
            # Validate the move if one was found
            if result:
                try:
                    # Parse the board and verify this is a legal move
                    board = chess.Board(self.fen)
                    move = chess.Move.from_uci(result)
                    
                    if move not in board.legal_moves:
                        self.error.emit(f"AI engine returned illegal move: {result}")
                        
                        # Return a random legal move instead
                        legal_moves = list(board.legal_moves)
                        if legal_moves:
                            import random
                            result = legal_moves[random.randint(0, len(legal_moves)-1)].uci()
                        else:
                            result = ""
                except Exception as e:
                    self.error.emit(f"Error validating move: {str(e)}")
            
            # Final progress update
            self.progress.emit(100)
            
            # Emit the result
            self.finished.emit(result)
            
        except Exception as e:
            # Get full traceback for better debugging
            error_traceback = traceback.format_exc()
            
            # Log the error
            print(f"AI Worker error: {str(e)}")
            print(error_traceback)
            
            # Emit error signal
            self.error.emit(str(e))
            
            # Still emit a finished signal with empty result
            self.finished.emit("")
    
    def cancel(self):
        """Cancel the ongoing computation safely."""
        self.mutex.lock()
        self._canceled = True
        if self._paused:
            self._paused = False
            self.pause_condition.wakeAll()
        self.mutex.unlock()
        
        # Also stop the bot's thinking process if it's active
        if self.chess_bot:
            try:
                self.chess_bot.stop_thinking()
            except Exception as e:
                print(f"Error stopping AI thinking: {str(e)}")
    
    def pause(self):
        """Pause the computation."""
        self.mutex.lock()
        self._paused = True
        self.mutex.unlock()
    
    def resume(self):
        """Resume a paused computation."""
        self.mutex.lock()
        if self._paused:
            self._paused = False
            self.pause_condition.wakeAll()
        self.mutex.unlock()