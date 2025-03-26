import chess
import threading
from search.searcher import Searcher
from threading import Event
from opening_book import OpeningBook

class Bot:
    # Settings
    use_opening_book = True
    max_book_ply = 16
    # Limit the amount of time the bot can spend per move (mainly for
    # games against human opponents, so not boring to play against).
    use_max_think_time = False
    max_think_time_ms = 2500

    def __init__(self):
        self.board = chess.Board()
        self.searcher = Searcher(self.board)
        self.book = OpeningBook("resources/book.txt")  # Đường dẫn tới file book
        self.search_wait_handle = Event()
        self.cancel_search_timer = None

        # State
        self.current_search_id = 0
        self.is_quitting = False
        self.is_thinking = False
        self.latest_move_is_book_move = False

        # Callbacks
        self.on_move_chosen = None  # Callback function when move is chosen

        # Set the callback from the searcher to our method
        self.searcher.on_search_complete = self.on_search_complete

        # Start search thread
        self.search_thread = threading.Thread(target=self.search_thread, daemon=True)
        self.search_thread.start()

    def notify_new_game(self):
        """Reset search data for a new game"""
        self.searcher.clear_for_new_position()

    def set_position(self, fen):
        """Set the board to a specific position"""
        self.board.set_fen(fen)

    def make_move(self, move_string):
        """Make a move on the board"""
        move = chess.Move.from_uci(move_string)
        self.board.push(move)
    
    def choose_think_time(self, time_remaining_white_ms, time_remaining_black_ms, 
                         increment_white_ms, increment_black_ms):
        """Calculate how much time to spend thinking about the current move"""
        my_time_remaining_ms = time_remaining_white_ms if self.board.turn == chess.WHITE else time_remaining_black_ms
        my_increment_ms = increment_white_ms if self.board.turn == chess.WHITE else increment_black_ms
        
        # Get a fraction of remaining time to use for current move
        think_time_ms = my_time_remaining_ms / 40.0
        
        # Clamp think time if a maximum limit is imposed
        if self.use_max_think_time:
            think_time_ms = min(self.max_think_time_ms, think_time_ms)
        
        # Add increment
        if my_time_remaining_ms > my_increment_ms * 2:
            think_time_ms += my_increment_ms * 0.8
        
        min_think_time = min(50, my_time_remaining_ms * 0.25)
        return int(max(min_think_time, think_time_ms))
    
    def think_timed(self, time_ms):
        """Start thinking about a move with a time limit"""
        self.latest_move_is_book_move = False
        self.is_thinking = True
        
        if self.cancel_search_timer:
            self.cancel_search_timer.cancel()
            self.cancel_search_timer = None
        
        # Try to get a move from the opening book
        if self.try_get_opening_book_move():
            self.latest_move_is_book_move = True
            self.on_search_complete(self.book_move)
        else:
            self.start_search(time_ms)
    
    def start_search(self, time_ms):
        """Start the search with a time limit"""
        self.current_search_id += 1
        self.search_wait_handle.set()
        
        # Set up timer to stop search
        search_id = self.current_search_id
        self.cancel_search_timer = threading.Timer(time_ms / 1000.0, lambda: self.end_search(search_id))
        self.cancel_search_timer.daemon = True
        self.cancel_search_timer.start()
    
    def search_thread(self):
        """Thread that performs the actual search"""
        while not self.is_quitting:
            self.search_wait_handle.wait()
            self.search_wait_handle.clear()
            if not self.is_quitting:
                self.searcher.start_search()
    
    def stop_thinking(self):
        """Stop the current search"""
        self.end_search()
    
    def quit(self):
        """Stop all operations and prepare for program exit"""
        self.is_quitting = True
        self.end_search()
        self.search_wait_handle.set()  # Wake up search thread so it can exit
    
    def get_board_diagram(self):
        """Get a string representation of the current board"""
        return str(self.board)
    
    def end_search(self, search_id=None):
        """End the current search"""
        if self.cancel_search_timer:
            self.cancel_search_timer.cancel()
            self.cancel_search_timer = None
        
        if search_id is not None:
            # If search timer has been cancelled, the search will have been stopped already
            if self.cancel_search_timer and self.cancel_search_timer.is_alive():
                return
            
            if self.current_search_id != search_id:
                return  # Don't end a different search than the one requested
        
        if self.is_thinking:
            self.searcher.end_search()
    
    def on_search_complete(self, move):
        """Called when a search completes or a book move is found"""
        self.is_thinking = False
        
        # Convert move to UCI format without promotion symbol '='
        move_name = move.uci().replace("=", "")
        
        # Call the callback with the chosen move
        if self.on_move_chosen:
            self.on_move_chosen(move_name)
    
    def try_get_opening_book_move(self):
        """Try to get a move from the opening book"""
        if (self.use_opening_book and 
            len(self.board.move_stack) <= self.max_book_ply):
            
            book_move_str = self.book.try_get_book_move(self.board)
            if book_move_str:
                self.book_move = chess.Move.from_uci(book_move_str)
                return True
        
        self.book_move = chess.Move.null()
        return False
