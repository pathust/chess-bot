import requests
import json
import time
import threading
import random
from typing import Optional, Dict, Any, List
import chess
from bot import ChessBot
from tqdm import tqdm
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lichess_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LichessBot:
    def __init__(self, api_token: str, opening_book_path: str = None):
        """
        Initialize Lichess Bot with auto-challenge capability
        """
        self.api_token = api_token
        self.base_url = "https://lichess.org/api"
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.opening_book_path = opening_book_path
        
        # Active games tracking
        self.active_games = {}
        self.game_threads = {}
        self.is_challenging = False
        self.last_challenge_time = 0
        self.challenge_cooldown = 30  # seconds between challenges
        self.running = True
        self.challenge_declined = False  # Flag to retry immediately
        
        # Dynamic bot list
        self.available_bots = []
        self.tried_bots = set()  # Track bots we've tried this round
        self.last_bot_refresh = 0
        self.bot_refresh_interval = 3600  # 60 minutes
        
        # Bot info
        self.bot_info = self.get_account_info()
        logger.info(f"✅ Bot initialized: {self.bot_info.get('username', 'Unknown')}")
        
        # Fetch initial bot list
        self.refresh_bot_list()
        
        # Start auto-challenger thread
        self.auto_challenge_thread = threading.Thread(target=self.auto_challenge_loop, daemon=True)
        self.auto_challenge_thread.start()
        
    def get_account_info(self) -> Dict[str, Any]:
        """Get bot account information"""
        url = f"{self.base_url}/account"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get account info: {response.status_code}")
    
    def refresh_bot_list(self):
        """Fetch current list of online bots using /api/bot/online"""
        try:
            logger.info("🔄 Refreshing bot list...")
            
            # Get online bots from the correct API
            url = f"{self.base_url}/bot/online"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to get online bots: {response.status_code}")
                return
            
            # Parse NDJSON response
            bots = []
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        bot_data = json.loads(line)
                        if self.is_suitable_bot(bot_data):
                            bots.append(self.format_bot_data(bot_data))
                    except json.JSONDecodeError:
                        continue
            
            self.available_bots = bots
            self.tried_bots.clear()  # Reset tried bots when refreshing
            self.last_bot_refresh = time.time()
            
            logger.info(f"✅ Found {len(self.available_bots)} suitable bots")
            
            # Show some examples
            if self.available_bots:
                examples = self.available_bots[:3]
                for bot in examples:
                    rating = bot.get('rating', 'N/A')
                    logger.info(f"   • {bot['username']} ({rating})")
                if len(self.available_bots) > 3:
                    logger.info(f"   ... and {len(self.available_bots) - 3} more")
            
        except Exception as e:
            logger.error(f"❌ Error refreshing bot list: {e}")
            self.available_bots = []
    
    def format_bot_data(self, bot_data: Dict) -> Dict:
        """Format bot data from API response"""
        # Get best rating from perfs
        perfs = bot_data.get('perfs', {})
        rating = 1500  # default
        
        # Priority order for rating selection
        for perf_type in ['blitz', 'rapid', 'bullet', 'classical']:
            if perf_type in perfs and not perfs[perf_type].get('prov', False):
                rating = perfs[perf_type].get('rating', 1500)
                break
        
        return {
            'username': bot_data['username'],
            'id': bot_data['id'],
            'rating': rating,
            'online': True,  # All bots from /api/bot/online are online
            'games': sum(perf.get('games', 0) for perf in perfs.values())
        }
    
    def is_suitable_bot(self, bot_data: Dict) -> bool:
        """Check if bot is suitable for challenging"""
        username = bot_data.get('username', '')
        
        # Skip our own bot - IMPORTANT!
        my_username = self.bot_info.get('username', '').lower()
        if username.lower() == my_username:
            return False
        
        # Must be a bot
        if bot_data.get('title') != 'BOT':
            return False
        
        # Get rating for filtering
        perfs = bot_data.get('perfs', {})
        has_valid_rating = False
        
        for perf_type in ['blitz', 'rapid', 'bullet']:
            if perf_type in perfs:
                perf = perfs[perf_type]
                rating = perf.get('rating', 0)
                games = perf.get('games', 0)
                
                # Check if has reasonable rating and experience
                if 1000 <= rating <= 3000 and games > 10:
                    has_valid_rating = True
                    break
        
        return has_valid_rating
    
    def auto_challenge_loop(self):
        """Continuously challenge bots when idle"""
        logger.info("🎯 Auto-challenger started!")
        
        while self.running:
            try:
                # Refresh bot list periodically
                if time.time() - self.last_bot_refresh > self.bot_refresh_interval:
                    self.refresh_bot_list()
                
                # Check if we should challenge
                time_since_last = time.time() - self.last_challenge_time
                
                if len(self.active_games) > 0:
                    time.sleep(5)
                    continue
                
                if self.is_challenging:
                    time.sleep(2)
                    continue
                
                # If challenge was declined, try immediately with different bot
                if self.challenge_declined:
                    self.challenge_declined = False
                    logger.info("🔄 Challenge declined, trying different bot...")
                    if self.available_bots:
                        self.challenge_random_bot()
                    continue
                
                # Normal cooldown logic with single progress bar
                if time_since_last < self.challenge_cooldown:
                    remaining = int(self.challenge_cooldown - time_since_last)
                    
                    # Single progress bar that updates in place
                    with tqdm(total=remaining, 
                             desc="⏳ Waiting to challenge", 
                             unit="s", 
                             leave=False,
                             ncols=80,
                             bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}s') as pbar:
                        
                        for i in range(remaining):
                            if not self.running or len(self.active_games) > 0 or self.challenge_declined:
                                break
                            time.sleep(1)
                            pbar.update(1)
                    
                    # Clear the line after progress bar
                    print("\r" + " " * 80 + "\r", end="", flush=True)
                    continue
                
                # Try to challenge
                if self.available_bots:
                    logger.info("🎯 Looking for opponent...")
                    self.challenge_random_bot()
                else:
                    logger.info("❌ No suitable bots found, refreshing list...")
                    self.refresh_bot_list()
                    time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Auto-challenge error: {e}")
                time.sleep(10)
    
    def challenge_random_bot(self):
        """Challenge a random bot from the available list"""
        if self.is_challenging or not self.running or not self.available_bots:
            return
            
        self.is_challenging = True
        
        try:
            # Get our rating to calculate 110% threshold
            my_rating = self.get_my_rating()
            max_rating = int(my_rating * 1.1)  # 110% of our rating
            
            logger.info(f"📊 My rating: {my_rating}, Max opponent rating: {max_rating}")
            
            # Get bots we haven't tried yet
            untried_bots = [bot for bot in self.available_bots if bot['username'] not in self.tried_bots]
            
            # If we've tried all bots, reset and try again
            if not untried_bots:
                logger.info("🔄 Tried all bots, resetting and refreshing list...")
                self.tried_bots.clear()
                self.refresh_bot_list()
                untried_bots = self.available_bots.copy()
            
            if not untried_bots:
                logger.warning("❌ No bots available")
                return
            
            # Filter bots with rating < 110% of our rating
            filtered_bots = [bot for bot in untried_bots if bot.get('rating', 1500) < max_rating]
            
            if not filtered_bots:
                logger.warning(f"❌ No bots with rating < {max_rating} available")
                # Reset tried bots and try again with all available bots
                self.tried_bots.clear()
                filtered_bots = [bot for bot in self.available_bots if bot.get('rating', 1500) < max_rating]
                
                if not filtered_bots:
                    logger.warning(f"❌ No suitable bots found (rating < {max_rating})")
                    return
            
            # Sort by rating (ascending - weakest first)
            sorted_bots = sorted(filtered_bots, key=lambda x: x['rating'])
            
            # Pick from suitable range (prefer closer to our rating)
            # Take bots with rating between 80% and 110% of our rating
            min_rating = int(my_rating * 0.8)
            preferred_bots = [bot for bot in sorted_bots if min_rating <= bot.get('rating', 1500) < max_rating]
            
            # If no preferred bots, use all filtered bots
            suitable_bots = preferred_bots if preferred_bots else sorted_bots
            
            # Shuffle and try up to 5 bots
            random.shuffle(suitable_bots)
            
            for i, bot in enumerate(suitable_bots[:5]):
                if not self.running:
                    break
                    
                # Mark as tried
                self.tried_bots.add(bot['username'])
                
                rating = bot.get('rating', 'N/A')
                rating_percent = (rating / my_rating * 100) if my_rating > 0 else 100
                logger.info(f"🔍 Trying {bot['username']} (rating: {rating}, {rating_percent:.0f}% of mine) ({i+1}/5)")
                
                if self.try_challenge_bot(bot):
                    logger.info(f"✅ Successfully challenged {bot['username']} (rating: {rating})")
                    return
                
                time.sleep(1)  # Small delay between attempts
            
            logger.warning("❌ All challenge attempts failed")
                        
        finally:
            self.is_challenging = False
            self.last_challenge_time = time.time()

    def get_my_rating(self):
        """Get our current rating"""
        try:
            # Get rating from bot info perfs
            perfs = self.bot_info.get('perfs', {})
            
            # Priority order for rating selection
            for perf_type in ['blitz', 'rapid', 'bullet', 'classical']:
                if perf_type in perfs and not perfs[perf_type].get('prov', False):
                    rating = perfs[perf_type].get('rating', 1500)
                    if rating > 0:
                        return rating
            
            # Fallback to default rating
            return 1500
            
        except Exception as e:
            logger.error(f"Error getting my rating: {e}")
            return 1500


    
    def try_challenge_bot(self, bot: Dict) -> bool:
        """Try to challenge a specific bot"""
        try:
            bot_name = bot['username']
            
            # Skip our own bot (double check)
            if bot_name.lower() == self.bot_info.get('username', '').lower():
                return False
            
            # Random time control based on bot's strengths
            time_controls = [
                {"time": 180, "increment": 2},   # 3+0
                {"time": 300, "increment": 2},   # 5+0
                {"time": 300, "increment": 3},   # 5+3
                {"time": 600, "increment": 5},   # 10+0
            ]
            
            time_control = random.choice(time_controls)
            
            # Send challenge
            url = f"{self.base_url}/challenge/{bot_name}"
            data = {
                "rated": "true",
                "clock.limit": time_control["time"],
                "clock.increment": time_control["increment"],
                "color": "random",
                "variant": "standard"
            }
            
            response = requests.post(url, headers=self.headers, data=data)
            
            if response.status_code == 200:
                rating = bot.get('rating', 'N/A')
                logger.info(f"✅ Challenge sent to {bot_name} ({rating}) - {time_control['time']}+{time_control['increment']}")
                return True
            else:
                # Log to file only for failed challenges
                logger.debug(f"Challenge to {bot_name} failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.debug(f"Exception challenging {bot.get('username', 'unknown')}: {e}")
            return False
    
    def stream_events(self):
        """Stream incoming game events from Lichess"""
        url = f"{self.base_url}/stream/event"
        logger.info(f"🌐 Connected to Lichess events")
        
        while self.running:
            try:
                response = requests.get(url, headers=self.headers, stream=True, timeout=None)
                response.raise_for_status()
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip() and self.running:
                        try:
                            event = json.loads(line)
                            self.handle_event(event)
                        except json.JSONDecodeError:
                            continue
                            
            except requests.exceptions.RequestException:
                if self.running:
                    logger.warning("🔄 Reconnecting...")
                    time.sleep(5)
                continue
            except KeyboardInterrupt:
                logger.info("\n👋 Bot stopped by user")
                self.running = False
                break
            except Exception as e:
                if self.running:
                    logger.error(f"Stream error: {e}")
                    time.sleep(5)
                continue
    
    def handle_event(self, event: Dict[str, Any]):
        """Handle different types of events from Lichess"""
        event_type = event.get('type')
        
        if event_type == 'gameStart':
            game_info = event['game']
            game_id = game_info['id']
            logger.info(f"🎮 Game started: {game_id}")
            self.start_game_thread(game_id)
            
        elif event_type == 'gameFinish':
            game_info = event['game']
            game_id = game_info['id']
            logger.info(f"🏁 Game finished: {game_id}")
            self.cleanup_game(game_id)
            # Reset tried bots after game finish to try again
            self.tried_bots.clear()
            
        elif event_type == 'challenge':
            challenge = event['challenge']
            challenger_name = challenge.get('challenger', {}).get('name', '')
            
            # Don't accept challenges from ourselves
            if challenger_name.lower() == self.bot_info.get('username', '').lower():
                return
                
            self.handle_challenge(challenge)
        
        elif event_type == 'challengeDeclined':
            challenge_data = event.get('challenge', {})
            challenger = challenge_data.get('challenger', {}).get('name', 'Unknown')
            destUser = challenge_data.get('destUser', {}).get('name', 'Unknown')
            
            # Only log if we were the challenger
            if challenger.lower() == self.bot_info.get('username', '').lower():
                logger.info(f"❌ Our challenge declined by {destUser}")
                # Set flag to try different bot immediately
                self.challenge_declined = True
        
        elif event_type == 'challengeCanceled':
            challenge_data = event.get('challenge', {})
            challenger = challenge_data.get('challenger', {}).get('name', 'Unknown')
            
            # Only log if we were involved
            if challenger.lower() == self.bot_info.get('username', '').lower():
                logger.info(f"🚫 Our challenge was canceled")
                # Set flag to try different bot immediately
                self.challenge_declined = True
    
    def handle_challenge(self, challenge: Dict[str, Any]):
        """Handle incoming challenges"""
        challenge_id = challenge['id']
        challenger = challenge['challenger']['name']
        variant = challenge.get('variant', {}).get('name', 'standard')
        
        if variant.lower() == 'standard':
            self.accept_challenge(challenge_id)
            logger.info(f"✅ Accepted challenge from {challenger}")
        else:
            self.decline_challenge(challenge_id)
            logger.info(f"❌ Declined non-standard challenge from {challenger}")
    
    def accept_challenge(self, challenge_id: str):
        """Accept a challenge"""
        url = f"{self.base_url}/challenge/{challenge_id}/accept"
        requests.post(url, headers=self.headers)
    
    def decline_challenge(self, challenge_id: str):
        """Decline a challenge"""
        url = f"{self.base_url}/challenge/{challenge_id}/decline"
        requests.post(url, headers=self.headers)
    
    def start_game_thread(self, game_id: str):
        """Start a new thread to handle a game"""
        if game_id not in self.game_threads:
            thread = threading.Thread(target=self.play_game, args=(game_id,), daemon=True)
            self.game_threads[game_id] = thread
            thread.start()
    
    def play_game(self, game_id: str):
        """Play a single game"""
        chess_bot = ChessBot(opening_book_path=self.opening_book_path)
        self.active_games[game_id] = {
            'chess_bot': chess_bot,
            'my_color': None,
            'game_state': None
        }
        
        url = f"{self.base_url}/bot/game/stream/{game_id}"
        
        try:
            response = requests.get(url, headers=self.headers, stream=True, timeout=None)
            
            if response.status_code != 200:
                return
            
            for line in response.iter_lines(decode_unicode=True):
                if line.strip() and self.running:
                    try:
                        data = json.loads(line)
                        if not self.handle_game_event(game_id, data):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception:
            pass
        finally:
            self.cleanup_game(game_id)
    
    def handle_game_event(self, game_id: str, data: Dict[str, Any]) -> bool:
        """Handle game events"""
        event_type = data.get('type')
        
        if event_type == 'gameFull':
            return self.handle_game_full(game_id, data)
        elif event_type == 'gameState':
            return self.handle_game_state(game_id, data)
        elif event_type == 'chatLine':
            self.handle_chat(game_id, data)
        
        return True
    
    def handle_game_full(self, game_id: str, data: Dict[str, Any]) -> bool:
        """Handle initial game state"""
        if game_id not in self.active_games:
            return False
            
        game_info = self.active_games[game_id]
        
        # Determine color
        white_player = data.get('white', {})
        black_player = data.get('black', {})
        my_username = self.bot_info.get('username', '').lower()
        
        if white_player.get('name', '').lower() == my_username:
            game_info['my_color'] = 'white'
            opponent = black_player.get('name', 'Unknown')
        elif black_player.get('name', '').lower() == my_username:
            game_info['my_color'] = 'black'
            opponent = white_player.get('name', 'Unknown')
        else:
            return False
        
        logger.info(f"♟️  Playing as {game_info['my_color']} vs {opponent}")
        
        # Handle initial state
        initial_state = data.get('state', {})
        return self.handle_game_state(game_id, initial_state)
    
    def handle_game_state(self, game_id: str, state: Dict[str, Any]) -> bool:
        """Handle game state updates"""
        if game_id not in self.active_games:
            return False
            
        game_info = self.active_games[game_id]
        chess_bot = game_info['chess_bot']
        my_color = game_info['my_color']
        
        # Check if game is over
        status = state.get('status')
        if status in ['mate', 'resign', 'stalemate', 'timeout', 'draw', 'outoftime', 'cheat', 'noStart', 'aborted']:
            return False
        
        # Update position
        moves_str = state.get('moves', '')
        moves_list = moves_str.split() if moves_str else []
        
        try:
            chess_bot.set_position(moves=moves_list)
        except Exception:
            return False
        
        # Check if our turn
        move_count = len(moves_list)
        is_white_turn = move_count % 2 == 0
        is_my_turn = (my_color == 'white' and is_white_turn) or (my_color == 'black' and not is_white_turn)
        
        if is_my_turn and status == 'started':
            # Calculate thinking time
            wtime = state.get('wtime')
            btime = state.get('btime')
            winc = state.get('winc', 0)
            binc = state.get('binc', 0)
            
            if wtime is not None and btime is not None:
                think_time_ms = chess_bot.choose_think_time(wtime, btime, winc, binc)
            else:
                think_time_ms = 5000
            
            logger.info(f"🤔 Thinking for {think_time_ms/1000:.1f}s...")
            
            # Get move
            def on_move_chosen(move_uci):
                if move_uci:
                    self.send_move(game_id, move_uci)
                    logger.info(f"♟️  Played: {move_uci}")
                else:
                    # Fallback
                    legal_moves = chess_bot.get_legal_moves()
                    if legal_moves:
                        self.send_move(game_id, legal_moves[0])
                        logger.info(f"♟️  Played (fallback): {legal_moves[0]}")
            
            chess_bot.on_move_chosen = on_move_chosen
            chess_bot.think_timed(think_time_ms)
        
        return True
    
    def handle_chat(self, game_id: str, data: Dict[str, Any]):
        """Handle chat messages"""
        text = data.get('text', '')
        
        if text.lower() in ['good luck', 'gl', 'glhf']:
            self.send_chat(game_id, "Good luck!")
        elif text.lower() in ['gg', 'good game']:
            self.send_chat(game_id, "Good game!")
    
    def send_move(self, game_id: str, move_uci: str):
        """Send a move to Lichess"""
        url = f"{self.base_url}/bot/game/{game_id}/move/{move_uci}"
        requests.post(url, headers=self.headers)
    
    def send_chat(self, game_id: str, message: str, room: str = 'player'):
        """Send a chat message"""
        url = f"{self.base_url}/bot/game/{game_id}/chat"
        data = {'room': room, 'text': message}
        requests.post(url, headers=self.headers, data=data)
    
    def cleanup_game(self, game_id: str):
        """Clean up resources for a finished game"""
        if game_id in self.active_games:
            chess_bot = self.active_games[game_id]['chess_bot']
            if hasattr(chess_bot, 'quit'):
                chess_bot.quit()
            del self.active_games[game_id]
        
        if game_id in self.game_threads:
            del self.game_threads[game_id]
    
    def run(self):
        """Start the bot"""
        logger.info("🚀 Lichess bot started!")
        logger.info(f"👤 Account: {self.bot_info.get('username')}")
        
        try:
            self.stream_events()
        except KeyboardInterrupt:
            logger.info("\n👋 Bot stopped")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
            self.running = False
        finally:
            self.cleanup_all_games()
    
    def cleanup_all_games(self):
        """Clean up all active games"""
        for game_id in list(self.active_games.keys()):
            self.cleanup_game(game_id)


def main():
    """Main function to run the bot"""
    API_TOKEN = "lip_n2QO0i6D9IlLSwPaVBxL"
    OPENING_BOOK_PATH = "resources/komodo.bin"
    
    # Test token
    print("🔍 Testing API token...")
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    try:
        response = requests.get("https://lichess.org/api/account", headers=headers)
        if response.status_code != 200:
            print(f"❌ Invalid token: {response.status_code}")
            return
        
        account = response.json()
        print(f"✅ Token valid: {account.get('username')}")
        
        if not account.get('title') == 'BOT':
            print("⚠️  Warning: Not a BOT account")
        else:
            print("✅ BOT account verified!")
        
    except Exception as e:
        print(f"❌ Token error: {e}")
        return
    
    try:
        bot = LichessBot(API_TOKEN, OPENING_BOOK_PATH)
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")


if __name__ == "__main__":
    main()
