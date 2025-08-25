import os
import sys
import subprocess
import importlib
import json

# Auto-requirements checker
def check_and_install_requirements():
    """Check and install missing requirements automatically"""
    required_packages = {
        "discord": "discord==2.3.2",
        "requests": "requests==2.31.0", 
        "asyncio": "asyncio==3.4.3",
        "dotenv": "python-dotenv==1.0.0",
        "google.generativeai": "google-generativeai==0.3.2",
        "langdetect": "langdetect==1.0.9",
        "emoji": "emoji==2.10.1",
        "colorama": "colorama==0.4.6",
        "psutil": "psutil==5.9.8",
        "schedule": "schedule==1.2.1",
        "fake_useragent": "fake-useragent==1.4.0",
        "dateutil": "python-dateutil==2.8.2"
    }
    
    missing_packages = []
    
    # Check each package
    for package, pip_name in required_packages.items():
        try:
            if package == "dotenv":
                importlib.import_module("dotenv")
            elif package == "google.generativeai":
                importlib.import_module("google.generativeai")
            elif package == "fake_useragent":
                importlib.import_module("fake_useragent")
            elif package == "dateutil":
                importlib.import_module("dateutil")
            else:
                importlib.import_module(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    # Install missing packages
    if missing_packages:
        print("🔍 Checking Discord Bot Requirements...")
        print("=" * 50)
        print(f"📦 Found {len(missing_packages)} missing packages")
        print("🚀 Installing automatically...")
        print("=" * 50)
        
        for package in missing_packages:
            try:
                print(f"📦 Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} installed successfully!")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
        
        print("🎉 All packages installed! Restarting bot...")
        print("=" * 50)
        return True
    
    return True

# Check requirements before importing
if not check_and_install_requirements():
    print("❌ Failed to install required packages. Exiting...")
    sys.exit(1)

# Now import all packages
import requests
import random
import time
import asyncio
import google.generativeai as palm
import json
from dotenv import load_dotenv
from langdetect import detect
from emoji import emojize
from datetime import datetime

# Load .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Parse unlimited keys from .env (comma/semicolon/newline separated)
_env_keys_raw = os.getenv("GEMINI_API_KEYS", "")
ENV_GEMINI_KEYS = []
for sep in ["\n", ";", ","]:
    parts = []
    if _env_keys_raw:
        for chunk in _env_keys_raw.split(sep):
            val = (chunk or "").strip()
            if val:
                parts.append(val)
    if parts:
        ENV_GEMINI_KEYS = parts
        break

HEADERS = {
    "Authorization": DISCORD_TOKEN,
    "Content-Type": "application/json"
}

# Max Gemini API keys to use
MAX_GEMINI_KEYS = 10

# Gemini key manager for multi-key rotation (placed early so it's available everywhere)
class GeminiKeyManager:
    def __init__(self, initial_key: str = None):
        self.keys = []
        self.index = 0
        self.cooldowns = {}  # key -> available_after_timestamp
        if initial_key:
            self._add_key(initial_key)
        # Load extra keys from env and config if available
        try:
            for k in (ENV_GEMINI_KEYS or []):
                self._add_key(k)
            if 'config_manager' in globals() and hasattr(config_manager, 'config'):
                extra = config_manager.config.get('gemini_api_keys') or []
                for k in extra:
                    self._add_key(k)
        except Exception:
            pass
        if self.keys:
            palm.configure(api_key=self.keys[0])
    
    def _add_key(self, key: str):
        if isinstance(key, str) and len(key) > 10 and key not in self.keys:
            self.keys.append(key)
            self.cooldowns[key] = 0
    
    def current_key(self):
        return self.keys[self.index] if self.keys else None
    
    def _advance_to_available(self):
        if not self.keys:
            return None
        start = self.index
        now = time.time()
        for _ in range(len(self.keys)):
            k = self.keys[self.index]
            if now >= self.cooldowns.get(k, 0):
                palm.configure(api_key=k)
                return k
            self.index = (self.index + 1) % len(self.keys)
        return None
    
    def next_key(self):
        if not self.keys:
            return None
        self.index = (self.index + 1) % len(self.keys)
        return self._advance_to_available()
    
    def set_cooldown(self, key: str, seconds: int):
        if key in self.cooldowns:
            self.cooldowns[key] = max(self.cooldowns.get(key, 0), time.time() + max(0, seconds))

# Initialize key manager early
key_manager = None
try:
    key_manager = GeminiKeyManager(GEMINI_API_KEY)
except Exception:
    key_manager = None

# Check requirements before importing
if not check_and_install_requirements():
    print("❌ Failed to install required packages. Exiting...")
    sys.exit(1)

# Now import all packages
import requests
import random
import time
import asyncio
import google.generativeai as palm
import json
from dotenv import load_dotenv
from langdetect import detect
from emoji import emojize
from datetime import datetime

# Load .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HEADERS = {
    "Authorization": DISCORD_TOKEN,
    "Content-Type": "application/json"
}

# Gemini AI Configuration
palm.configure(api_key=GEMINI_API_KEY)
model = palm.GenerativeModel("gemini-1.5-flash")

# Language Detection Function
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'  # Default to English if detection fails

# Get Random Emojis based on message sentiment
def get_random_emojis(count=2, sentiment='happy'):
    emoji_map = {
        'happy': [':grinning_face:', ':beaming_face_with_smiling_eyes:', ':face_with_tears_of_joy:', 
                 ':smiling_face_with_hearts:', ':star-struck:', ':face_blowing_a_kiss:', 
                 ':smiling_face_with_heart-eyes:', ':winking_face:', ':partying_face:'],
        'thinking': [':thinking_face:', ':face_with_monocle:', ':face_with_raised_eyebrow:', 
                    ':face_with_hand_over_mouth:', ':nerd_face:', ':face_with_hand_over_mouth:'],
        'helpful': [':thumbs_up:', ':OK_hand:', ':raising_hands:', ':folded_hands:', 
                   ':sparkles:', ':light_bulb:', ':check_mark:', ':rocket:'],
        'sympathetic': [':slightly_smiling_face:', ':hugging_face:', ':relieved_face:', ':heart:', ':pray:'],
        'confused': [':confused_face:', ':thinking_face:', ':face_with_raised_eyebrow:', ':face_with_monocle:'],
        'excited': [':partying_face:', ':star-struck:', ':face_with_cowboy_hat:', ':fire:', ':zap:'],
        'supportive': [':thumbs_up:', ':heart:', ':pray:', ':clap:', ':muscle:', ':tada:']
    }
    emojis = emoji_map.get(sentiment, emoji_map['happy'])
    selected = random.sample(emojis, min(count, len(emojis)))
    return ' '.join(emojize(emoji) for emoji in selected)


# Rate limiting for API calls
class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self):
        now = time.time()
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

# Initialize rate limiter (max 15 requests per minute - safer for Discord)
ai_rate_limiter = RateLimiter(max_requests=15, time_window=60)

# Channel slow mode configuration
CHANNEL_SLOW_MODES = {}

# Anti-ban configuration
ANTI_BAN_CONFIG = {
    'max_continuous_hours': 4,  # Max 4 hours continuously
    'break_duration_minutes': 30,  # 30 minutes break
    'max_daily_hours': 12,  # Max 12 hours per day
    'channel_rotation': True,  # Auto switch channels
    'response_patterns': ['casual', 'professional', 'funny', 'helpful', 'quiet']
}

# AI Reply Function with improved context handling
def get_gemini_response(prompt, detected_lang, message_type='general'):
    try:
        # Ensure key manager exists (lazy init)
        global key_manager
        if 'key_manager' not in globals() or key_manager is None:
            extra = []
            try:
                extra = config_manager.config.get('gemini_api_keys') or []
            except Exception:
                extra = []
            keys = []
            if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
                keys.append(GEMINI_API_KEY)
            for k in extra:
                if isinstance(k, str) and len(k) > 10 and k not in keys:
                    keys.append(k)
            # Apply cap
            keys = keys[:MAX_GEMINI_KEYS]
            
            class _KM:
                def __init__(self, keys_list):
                    self.keys = keys_list or []
                    self.index = 0
                    if self.keys:
                        palm.configure(api_key=self.keys[0])
                def current_key(self):
                    return self.keys[self.index] if self.keys else None
                def next_key(self):
                    if not self.keys:
                        return None
                    self.index = (self.index + 1) % len(self.keys)
                    palm.configure(api_key=self.keys[self.index])
                    return self.current_key()
            key_manager = _KM(keys)

        if not ai_rate_limiter.can_make_request():
            return "Rate limit exceeded. Please try again later."

        # Enhanced language and context instructions with emphasis on brevity
        lang_instructions = {
            'hi': 'Reply in Hindi language with 1-2 friendly sentences.',
            'en': 'Reply in English language with 1-2 friendly sentences.',
            'es': 'Reply in Spanish language with 1-2 friendly sentences.',
            'fr': 'Reply in French language with 1-2 friendly sentences.',
            'de': 'Reply in German language with 1-2 friendly sentences.',
            'ja': 'Reply in Japanese language with 1-2 friendly sentences.',
            'ko': 'Reply in Korean language with 1-2 friendly sentences.',
            'ar': 'Reply in Arabic language with 1-2 friendly sentences.',
            'ru': 'Reply in Russian language with 1-2 friendly sentences.',
            'zh': 'Reply in Chinese language with 1-2 friendly sentences.'
        }
        
        # Response templates based on message type
        templates = {
            'general': ['Keep the response natural and conversational.',
                       'Add some personality to the response.',
                       'Make the response engaging but concise.',
                       'Be friendly and approachable.'],
            'question': ['Provide a helpful and clear answer.',
                        'Be informative but keep it simple.',
                        'Answer directly with a friendly tone.',
                        'Give practical and actionable advice.'],
            'help': ['Offer assistance in a supportive way.',
                     'Be encouraging and helpful.',
                     'Provide guidance with a positive tone.',
                     'Show empathy and understanding.'],
            'reply': ['Acknowledge the previous message naturally.',
                      'Respond in a contextually appropriate way.',
                      'Keep the conversation flowing smoothly.',
                      'Build on the previous message naturally.'],
            'casual': ['Keep it casual and friendly like talking to a friend.',
                      'Use simple, everyday language.',
                      'Be relaxed and informal.'],
            'professional': ['Keep it professional but warm.',
                           'Be helpful and informative.',
                           'Maintain a helpful tone.'],
            'funny': ['Make the response humorous and entertaining.',
                     'Add some jokes or witty remarks.',
                     'Keep it light and fun.']
        }
        
        # Get current pattern safely (fallback if smart_timer not available)
        try:
            current_pattern = smart_timer.get_current_pattern()
        except:
            current_pattern = 'general'
        
        # Select template based on current pattern
        if current_pattern == 'quiet':
            # Quiet mode - minimal responses
            template = "Keep response very short and simple."
        elif current_pattern == 'casual':
            template = random.choice(templates.get('casual', templates['general']))
        elif current_pattern == 'professional':
            template = random.choice(templates.get('professional', templates['general']))
        elif current_pattern == 'funny':
            template = random.choice(templates.get('funny', templates['general']))
        else:
            template = random.choice(templates.get(message_type, templates['general']))
        
        # Add human-like variations to prompt
        human_variations = [
            "Make it sound like a real person typing, not a bot.",
            "Use casual, everyday language like a friend would.",
            "Sometimes add small mistakes or casual language.",
            "Keep it natural and conversational.",
            "Vary your writing style naturally.",
            "Sometimes be more formal, sometimes more casual."
        ]
        human_instruction = random.choice(human_variations)
        
        full_prompt = f"{lang_instructions.get(detected_lang, 'Reply with 1-2 friendly sentences.')}\n" \
                     f"{template}\n{human_instruction}\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Remove greeting openings to avoid bot-like starts
        lowered = response_text.lower().lstrip()
        for greet in ["hey", "hi", "hello", "hey there", "hi there", "hello there"]:
            if lowered.startswith(greet):
                # Remove the greeting word and following punctuation/space
                parts = response_text.split(' ', 1)
                if len(parts) == 2:
                    response_text = parts[1].lstrip("-,.!:; ")
                else:
                    # If only greeting, keep it minimal
                    response_text = response_text.lstrip("-,.!:; ")
                break
        
        # Control response length to avoid Discord issues
        if len(response_text) > 200:
            response_text = response_text[:200] + "..."
        
        # Add human-like variations (sometimes add typos, casual language)
        if random.random() < 0.2:  # 20% chance
            response_text = response_text.replace('.', '...').replace('!', '!!')
        
        # Randomly decide emoji placement and count (more human-like)
        emoji_count = random.randint(0, 2)  # Sometimes no emojis
        if emoji_count > 0:
            emojis = get_random_emojis(count=emoji_count, sentiment=message_type)
        else:
            emojis = ""
        
        # Emoji placement: no prefix; prefer suffix or inline by keyword
        if not emojis:
            return response_text
        
        # Try simple inline placement after a relevant keyword
        keywords_map = {
            'happy': ["great", "awesome", "amazing", "good", "nice"],
            'helpful': ["help", "fix", "try", "steps", "idea"],
            'thinking': ["think", "maybe", "perhaps", "consider"],
            'sympathetic': ["sorry", "understand", "feel", "hope"],
            'confused': ["confused", "unsure", "hmm"],
            'excited': ["wow", "cool", "excited", "love"],
            'supportive': ["you can", "go ahead", "good luck", "nice work"]
        }
        placed = False
        try:
            words = response_text.split()
            targets = keywords_map.get(message_type, [])
            for i, w in enumerate(words):
                lw = w.strip(',.!?').lower()
                if any(t == lw or t in lw for t in targets):
                    words[i] = f"{w} {emojis}"
                    placed = True
                    break
            if placed:
                return " ".join(words)
        except Exception:
            placed = False
        
        # Fallback: suffix placement only
        return f"{response_text} {emojis}"
    except Exception as e:
        # On rate limits or key-related errors, rotate key and retry once
        err_text = str(e).lower()
        if any(t in err_text for t in ["rate limit", "quota", "permission", "unauthorized", "invalid api"]):
            try:
                old_key = key_manager.current_key() if 'key_manager' in globals() and key_manager else None
                # Parse retry delay seconds if present
                retry_seconds = 30
                for token in err_text.replace('\n', ' ').split():
                    try:
                        val = int(token)
                        if 0 < val < 3600:
                            retry_seconds = val
                            break
                    except Exception:
                        pass
                if old_key and key_manager:
                    key_manager.set_cooldown(old_key, retry_seconds)
                new_key = key_manager.next_key() if key_manager else None
            except Exception:
                new_key = None
                old_key = None
            if new_key and new_key != old_key:
                try:
                    response = model.generate_content(full_prompt)
                    response_text = response.text.strip()
                    # Re-apply post-processing
                    lowered = response_text.lower().lstrip()
                    for greet in ["hey", "hi", "hello", "hey there", "hi there", "hello there"]:
                        if lowered.startswith(greet):
                            parts = response_text.split(' ', 1)
                            if len(parts) == 2:
                                response_text = parts[1].lstrip("-,.!:; ")
                            else:
                                response_text = response_text.lstrip("-,.!:; ")
                            break
                    if len(response_text) > 200:
                        response_text = response_text[:200] + "..."
                    if random.random() < 0.2:
                        response_text = response_text.replace('.', '...').replace('!', '!!')
                    emoji_count = random.randint(0, 2)
                    emojis = get_random_emojis(count=emoji_count, sentiment=message_type) if emoji_count > 0 else ""
                    if emojis:
                        # suffix only on retry
                        return f"{response_text} {emojis}"
                    return response_text
                except Exception as e2:
                    return f"AI Error: {e2}"
        return f"AI Error: {e}"

# Custom Timer Function with Human-like Behavior
async def send_reply(channel_id, message, delay, message_id=None):
    # Simulate human typing (random typing time based on message length)
    typing_time = min(len(message) * 0.1, 3)  # Max 3 seconds typing
    await asyncio.sleep(typing_time)
    
    # Add random delay before sending
    await asyncio.sleep(delay)
    
    data = {
        "content": message,
        "message_reference": {
            "message_id": message_id,
            "channel_id": channel_id
        } if message_id else None
    }
    requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=HEADERS, json=data)

# Get Server Channels Function
def get_servers_and_channels():
    try:
        # Get all guilds (servers)
        guilds_response = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=HEADERS)
        guilds = guilds_response.json()
        
        servers_with_channels = []
        
        for guild in guilds:
            guild_id = guild["id"]
            guild_name = guild["name"]
            
            # Get channels for this guild
            channels_response = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=HEADERS)
            channels = channels_response.json()
            
            # Filter text channels only
            text_channels = []
            for channel in channels:
                if channel["type"] == 0:  # Type 0 is text channel
                    text_channels.append({
                        "id": channel["id"],
                        "name": channel["name"]
                    })
            
            if text_channels:
                servers_with_channels.append({
                    "id": guild_id,
                    "name": guild_name,
                    "channels": text_channels
                })
        
        return servers_with_channels
    except Exception as e:
        print(f"⚠ Error getting servers: {e}")
        return []

# Smart Break Timer Function
class SmartBreakTimer:
    def __init__(self):
        self.start_time = time.time()
        self.last_break = time.time()
        self.daily_start = time.time()
        self.daily_hours = 0
        self.current_channel = None
        self.channels_used = []
        self.last_reply_time = 0  # Track when last reply was sent
        self.waiting_for_response = False  # Track if waiting for response
        self.last_reply_to_user = None  # Track who we replied to
        
        # Conversation tracking system
        self.active_conversations = {}  # Track ongoing conversations
        self.conversation_timeout = 300  # 5 minutes timeout for conversations
        self.max_conversations = 10  # keep at most 10 active users
        
        # Alternating priority flag (robust default)
        self.prefer_new_first = False
    
    def should_take_break(self):
        current_time = time.time()
        continuous_hours = (current_time - self.last_break) / 3600
        daily_hours = (current_time - self.daily_start) / 3600
        
        # Take break if continuous for too long
        if continuous_hours >= ANTI_BAN_CONFIG['max_continuous_hours']:
            return True, "continuous_limit"
        
        # Take break if daily limit reached
        if daily_hours >= ANTI_BAN_CONFIG['max_daily_hours']:
            return True, "daily_limit"
        
        return False, None
    
    def get_break_duration(self):
        return ANTI_BAN_CONFIG['break_duration_minutes'] * 60
    
    def should_rotate_channel(self):
        return ANTI_BAN_CONFIG['channel_rotation'] and len(self.channels_used) > 1
    
    def get_current_pattern(self):
        # Rotate through different response patterns
        pattern_index = int((time.time() - self.start_time) / 3600) % len(ANTI_BAN_CONFIG['response_patterns'])
        return ANTI_BAN_CONFIG['response_patterns'][pattern_index]
    
    def add_channel(self, channel_id):
        if channel_id not in self.channels_used:
            self.channels_used.append(channel_id)
    
    def get_next_channel(self):
        if len(self.channels_used) > 1:
            current_index = self.channels_used.index(self.current_channel) if self.current_channel else 0
            next_index = (current_index + 1) % len(self.channels_used)
            return self.channels_used[next_index]
        return None
    
    def can_send_new_reply(self):
        """Check if we can send a new reply (not waiting for response)"""
        current_time = time.time()
        
        # If waiting for response, check if enough time has passed (5 minutes)
        if self.waiting_for_response:
            if current_time - self.last_reply_time > 300:  # 5 minutes
                self.waiting_for_response = False
                return True
            return False
        
        # If not waiting, can send reply
        return True
    
    def mark_reply_sent(self, user_id):
        """Mark that we sent a reply to someone"""
        self.last_reply_time = time.time()
        self.waiting_for_response = True
        self.last_reply_to_user = user_id
    
    def check_response_received(self, messages):
        """Check if we received a response from the user we replied to"""
        if not self.waiting_for_response or not self.last_reply_to_user:
            return False
        
        current_time = time.time()
        
        # Look for recent messages from the user we replied to
        for msg in messages[:10]:  # Check last 10 messages
            author_id = msg.get('author', {}).get('id')
            if author_id == self.last_reply_to_user:
                # Check if message is recent (within last 2 minutes)
                timestamp = msg.get('timestamp', '')
                if timestamp:
                    try:
                        message_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        message_timestamp = message_time.timestamp()
                        
                        if current_time - message_timestamp < 120:  # 2 minutes
                            # User responded, stop waiting
                            self.waiting_for_response = False
                            return True
                    except:
                        pass
        
        return False
    
    def start_conversation(self, user_id, username):
        """Start a new conversation with a user"""
        current_time = time.time()
        self.active_conversations[user_id] = {
            'start_time': current_time,
            'last_message_time': current_time,
            'message_count': 1,
            'username': username
        }
        self.enforce_capacity()
        print_status(f"💬 Started conversation with {username}", 'info')
    
    def continue_conversation(self, user_id, username):
        """Continue an existing conversation"""
        if user_id in self.active_conversations:
            current_time = time.time()
            conv = self.active_conversations[user_id]
            conv['last_message_time'] = current_time
            conv['message_count'] += 1
            self.enforce_capacity()
            print_status(f"💬 Continuing conversation with {username} (Message #{conv['message_count']})", 'info')
            return True
        return False
    
    def can_continue_conversation(self, user_id):
        """Check if we can continue conversation (within 5 minute timeout)"""
        if user_id not in self.active_conversations:
            return False
        
        current_time = time.time()
        conv = self.active_conversations[user_id]
        time_since_last = current_time - conv['last_message_time']
        
        # If more than 5 minutes, conversation expired
        if time_since_last > self.conversation_timeout:
            del self.active_conversations[user_id]
            print_status(f"⏰ Conversation with {conv['username']} expired (5 min timeout)", 'warning')
            return False
        
        return True
    
    def cleanup_expired_conversations(self):
        """Remove expired conversations and enforce capacity"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv in list(self.active_conversations.items()):
            if current_time - conv['last_message_time'] > self.conversation_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            username = self.active_conversations[user_id]['username']
            del self.active_conversations[user_id]
            print_status(f"⏰ Conversation with {username} expired and removed", 'warning')
        
        self.enforce_capacity()
    
    def enforce_capacity(self):
        """Ensure at most max_conversations remain; drop expired first, then oldest by last_message_time."""
        current_time = time.time()
        # Remove expired first
        expired = [uid for uid, conv in self.active_conversations.items() if current_time - conv['last_message_time'] > self.conversation_timeout]
        for uid in expired:
            username = self.active_conversations[uid]['username']
            del self.active_conversations[uid]
            print_status(f"⏰ Conversation with {username} expired and removed", 'warning')
        # If still over capacity, remove oldest by last_message_time
        if len(self.active_conversations) > self.max_conversations:
            # Sort by last_message_time ascending (oldest first)
            sorted_items = sorted(self.active_conversations.items(), key=lambda x: x[1]['last_message_time'])
            to_remove = len(self.active_conversations) - self.max_conversations
            for i in range(to_remove):
                uid, conv = sorted_items[i]
                if uid in self.active_conversations:
                    del self.active_conversations[uid]
                    print_status(f"♻️ Removed oldest conversation ({conv['username']}) to keep top {self.max_conversations}", 'info')

    def get_conversation_status(self):
        """Get current conversation status"""
        if not self.active_conversations:
            return "No active conversations"
        
        status = []
        current_time = time.time()
        for user_id, conv in self.active_conversations.items():
            time_left = self.conversation_timeout - (current_time - conv['last_message_time'])
            if time_left > 0:
                status.append(f"{conv['username']}: {int(time_left)}s left")
        
        return ", ".join(status) if status else "No active conversations"

    def set_prefer_new_first(self, value: bool):
        try:
            setattr(self, 'prefer_new_first', bool(value))
        except Exception:
            self.prefer_new_first = bool(value)
    
    def should_prefer_new_first(self) -> bool:
        return bool(getattr(self, 'prefer_new_first', False))

# Initialize smart break timer
smart_timer = SmartBreakTimer()
# Ensure alternating flag exists even if older objects are reused
if not hasattr(smart_timer, 'prefer_new_first'):
    smart_timer.prefer_new_first = False

# Advanced Error Handling & Recovery System
class ErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.last_error_time = 0
        self.error_types = {}
    
    def handle_error(self, error, context, operation):
        """Handle different types of errors with recovery strategies"""
        current_time = time.time()
        error_type = type(error).__name__
        
        # Update error tracking
        self.error_count += 1
        self.last_error_time = current_time
        
        if error_type not in self.error_types:
            self.error_types[error_type] = 0
        self.error_types[error_type] += 1
        
        # Log error
        print_status(f"❌ Error in {operation}: {error_type}", 'error')
        print_status(f"Context: {context}", 'warning')
        
        # Update dashboard
        bot_dashboard.update_stats(error_occurred=True)
        
        # Recovery strategies
        if error_type == 'ConnectionError':
            return self.handle_connection_error()
        elif error_type == 'RateLimitError':
            return self.handle_rate_limit_error()
        elif error_type == 'TimeoutError':
            return self.handle_timeout_error()
        else:
            return self.handle_generic_error()
    
    def handle_connection_error(self):
        """Handle connection errors"""
        print_status("🔄 Connection error detected. Attempting to reconnect...", 'warning')
        time.sleep(5)  # Wait before retry
        return True
    
    def handle_rate_limit_error(self):
        """Handle rate limit errors"""
        print_status("⏰ Rate limit reached. Waiting 30 seconds...", 'warning')
        time.sleep(30)
        return True
    
    def handle_timeout_error(self):
        """Handle timeout errors"""
        print_status("⏱️ Timeout error. Retrying with longer timeout...", 'warning')
        time.sleep(3)
        return True
    
    def handle_generic_error(self):
        """Handle generic errors"""
        print_status("⚠️ Generic error. Waiting 10 seconds before retry...", 'warning')
        time.sleep(10)
        return True
    
    def should_continue_operation(self):
        """Check if we should continue operations after errors"""
        if self.error_count > 10:  # Too many errors
            return False
        if time.time() - self.last_error_time < 60:  # Recent errors
            return False
        return True

# Initialize error handler
error_handler = ErrorHandler()

# Enhanced Function to fetch messages from a channel
async def fetch_channel_messages(channel_id, limit=20):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(
                f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}", 
                headers=HEADERS, 
                timeout=30
            )
            
            if response.status_code == 200:
                messages = response.json()
                bot_dashboard.update_stats(message_processed=True)
                return messages
            elif response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 30))
                print_status(f"⏰ Rate limited. Waiting {retry_after} seconds...", 'warning')
                await asyncio.sleep(retry_after)
            else:
                print_status(f"❌ HTTP Error {response.status_code}: {response.text}", 'error')
                error_handler.handle_error(Exception(f"HTTP {response.status_code}"), 
                                       f"Channel {channel_id}", "fetch_messages")
                
        except requests.exceptions.Timeout:
            print_status("⏱️ Request timeout. Retrying...", 'warning')
            error_handler.handle_error(Exception("Timeout"), f"Channel {channel_id}", "fetch_messages")
        except requests.exceptions.ConnectionError:
            print_status("🔌 Connection error. Retrying...", 'warning')
            error_handler.handle_error(Exception("Connection Error"), f"Channel {channel_id}", "fetch_messages")
        except Exception as e:
            print_status(f"❌ Unexpected error: {e}", 'error')
            error_handler.handle_error(e, f"Channel {channel_id}", "fetch_messages")
        
        retry_count += 1
        if retry_count < max_retries:
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
    
    print_status("❌ Max retries reached for fetch_messages", 'error')
    return []

from colorama import init, Fore, Back, Style

# Initialize colorama for Windows
init()

# Simple event logger for UI
class EventLogger:
    def __init__(self, capacity: int = 5):
        self.capacity = capacity
        self.events = []
    
    def add(self, text: str):
        ts = time.strftime('%H:%M:%S')
        self.events.append(f"[{ts}] {text}")
        if len(self.events) > self.capacity:
            self.events.pop(0)
    
    def last(self):
        return list(self.events)

ui_events = EventLogger(5)

# Professional Dashboard UI System
class BotDashboard:
    def __init__(self):
        self.stats = {
            'messages_processed': 0,
            'responses_sent': 0,
            'errors_occurred': 0,
            'start_time': time.time(),
            'active_conversations': 0
        }
        self.status = "🟢 Online"
        self.channel_name = ""
        self.channel_id = ""
        self.mode = "casual"
        self.slowmode = 5
        self.next_refresh_eta = 0
    
    def update_stats(self, message_processed=False, response_sent=False, error_occurred=False):
        if message_processed:
            self.stats['messages_processed'] += 1
        if response_sent:
            self.stats['responses_sent'] += 1
        if error_occurred:
            self.stats['errors_occurred'] += 1
    
    def set_context(self, channel_id: str, channel_name: str, mode: str, slowmode: int, eta: int):
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.mode = mode
        self.slowmode = slowmode
        self.next_refresh_eta = eta
    
    def get_uptime(self):
        uptime_seconds = time.time() - self.stats['start_time']
        return uptime_seconds / 3600
    
    def get_response_rate(self):
        if self.stats['messages_processed'] == 0:
            return 0.0
        return (self.stats['responses_sent'] / self.stats['messages_processed']) * 100
    
    def display_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        uptime = self.get_uptime()
        response_rate = self.get_response_rate()
        
        header = f"{Fore.YELLOW}{Style.BRIGHT}Server/Channel: {self.channel_name or self.channel_id}  |  Mode: {self.mode.upper()}  |  Slowmode: {self.slowmode}s  |  Next Refresh: ~{self.next_refresh_eta}s{Style.RESET_ALL}"
        print("=" * max(80, len(header)))
        print(header)
        print("=" * max(80, len(header)))
        
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                        🤖 ADVANCED DISCORD BOT DASHBOARD                    ║")
        print("╠══════════════════════════════════════════════════════════════════════════════╣")
        print(f"║ Status: {self.status:<65} ║")
        print(f"║ Uptime: {uptime:.1f} hours{' ' * 55} ║")
        print("╠══════════════════════════════════════════════════════════════════════════════╣")
        print(f"║ 📊 Messages Processed: {self.stats['messages_processed']:<45} ║")
        print(f"║ 💬 Responses Sent: {self.stats['responses_sent']:<48} ║")
        print(f"║ ⚠️  Errors Occurred: {self.stats['errors_occurred']:<46} ║")
        print(f"║ 📈 Response Rate: {response_rate:.1f}%{' ' * 50} ║")
        print(f"║ 💭 Active Conversations: {self.stats['active_conversations']:<42} ║")
        print("╠══════════════════════════════════════════════════════════════════════════════╣")
        print("║ Recent Events:                                                               ║")
        last = ui_events.last()
        if not last:
            print("║   (no recent events)                                                         ║")
        else:
            for ev in last[-5:]:
                line = ev[:74]
                print(f"║ {line:<74} ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")

# Enhanced Terminal UI Functions
def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{text.center(60)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}\n")

def print_status(text, status_type='info'):
    colors = {
        'success': Fore.GREEN,
        'error': Fore.RED,
        'info': Fore.BLUE,
        'warning': Fore.YELLOW
    }
    color = colors.get(status_type, Fore.WHITE)
    print(f"{color}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def show_progress_bar(description, current, total, width=50):
    """Show animated progress bar"""
    progress = int(width * current / total)
    bar = '█' * progress + '░' * (width - progress)
    percentage = current / total * 100
    
    sys.stdout.write(f'\r{Fore.CYAN}{description}: [{bar}] {percentage:.1f}%{Style.RESET_ALL}')
    sys.stdout.flush()
    
    if current == total:
        print()

# Initialize dashboard
bot_dashboard = BotDashboard()

# Cooldown tracking (per-user)
USER_COOLDOWNS = {}

def is_on_cooldown(user_id: str, min_seconds: int = 60, max_seconds: int = 120) -> bool:
    now = time.time()
    window = USER_COOLDOWNS.get(user_id)
    if window and now < window:
        return True
    # Not on cooldown; assign a new randomized cooldown end
    USER_COOLDOWNS[user_id] = now + random.randint(min_seconds, max_seconds)
    return False

# Config manager
class ConfigManager:
    def __init__(self, path: str = "config.json"):
        self.path = path
        self.last_mtime = 0
        self.config = {
            "default_mode": "casual",
            "cooldown_seconds": {"min": 60, "max": 120},
            "channels": {"default_slowmode": 5, "overrides": {}},
            "response_patterns": ["casual", "professional", "funny", "helpful", "quiet"],
            "webhook_url": "",
            "owner_id": "",
            "gemini_api_keys": [] # Added for multiple API keys
        }
        self.load(force=True)
    
    def load(self, force: bool = False):
        try:
            if not os.path.exists(self.path):
                return
            mtime = os.path.getmtime(self.path)
            if force or mtime != self.last_mtime:
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.config.update(data)
                        self.last_mtime = mtime
                        print_status("🔁 Config loaded", 'info')
        except Exception as e:
            print_status(f"Config load error: {e}", 'error')
    
    def get_owner_id(self):
        return self.config.get("owner_id") or os.getenv("BOT_OWNER_ID", "")
    
    def get_mode(self):
        return self.config.get("default_mode", "casual")
    
    def get_slowmode(self, channel_id: str):
        overrides = self.config.get("channels", {}).get("overrides", {})
        if channel_id in overrides and isinstance(overrides[channel_id], int):
            return overrides[channel_id]
        return self.config.get("channels", {}).get("default_slowmode", 5)
    
    def get_cooldown_range(self):
        cd = self.config.get("cooldown_seconds", {})
        return int(cd.get("min", 60)), int(cd.get("max", 120))

# Initialize config
config_manager = ConfigManager()

# Startup validation checks
def validate_startup():
    problems = []

    # Check env vars
    if not DISCORD_TOKEN or len(DISCORD_TOKEN) < 10:
        problems.append("DISCORD_TOKEN is missing/invalid in .env")
    if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 10:
        problems.append("GEMINI_API_KEY is missing/invalid in .env")

    # Check Discord reachability (best-effort)
    try:
        resp = requests.get("https://discord.com/api/v9/users/@me", headers=HEADERS, timeout=15)
        if resp.status_code not in (200, 401):
            problems.append(f"Discord API unusual status: {resp.status_code}")
        elif resp.status_code == 401:
            problems.append("Discord token unauthorized (401). Check DISCORD_TOKEN format.")
    except Exception as e:
        problems.append(f"Discord reachability error: {e}")

    # Check Gemini reachable (best-effort)
    try:
        _ = model.generate_content("ping")
    except Exception as e:
        err = str(e).lower()
        # If it's a rate-limit/quota error, warn but don't block startup
        if any(t in err for t in ["rate limit", "quota", "retry_delay", "exceeded"]):
            print_status(f"⚠ Gemini quota warning: {e}", 'warning')
        else:
            problems.append(f"Gemini check failed: {e}")

    if problems:
        print_header("Startup Checks Failed")
        for p in problems:
            print_status(f"- {p}", 'error')
        return False

    print_status("✅ Startup checks passed", 'success')
    return True

# Selfbot Main Function
async def selfbot():
    print_header("Discord Chat Bot")
    print_status("Bot is starting...", 'info')

    # Validate environment and connectivity
    if not validate_startup():
        print_status("Fix the above issues and restart the bot.", 'error')
        return
    
    # Ask for channel IDs with validation
    channels_input = input(f"{Fore.CYAN}👉 Enter channel IDs (separate with comma for multiple): {Style.RESET_ALL}").strip()
    if not channels_input:
        print_status("Channel IDs cannot be empty. Please try again.", 'error')
        return
    
    # Parse multiple channels
    channel_ids = [cid.strip() for cid in channels_input.split(',')]
    valid_channels = []
    
    for cid in channel_ids:
        if not cid.isdigit():
            print_status(f"Invalid channel ID: {cid}. Skipping...", 'warning')
            continue
        valid_channels.append(cid)
    
    if not valid_channels:
        print_status("No valid channel IDs provided. Exiting...", 'error')
        return
    
    # Use first channel as primary, others for rotation
    channel_id = valid_channels[0]
    for cid in valid_channels:
        smart_timer.add_channel(cid)
    
    print_status(f"✅ Added {len(valid_channels)} channels for rotation", 'success')

    # Ask for slow mode with validation
    if channel_id not in CHANNEL_SLOW_MODES:
        while True:
            slow_mode_input = input(f"{Fore.CYAN}🔄 Enter Slow Mode (seconds, default 5): {Style.RESET_ALL}").strip()
            if not slow_mode_input:  # Use default value if empty
                slow_mode = random.randint(3, 8)  # Random delay between 3-8 seconds
                break
            try:
                slow_mode = int(slow_mode_input)
                if slow_mode < 0:
                    print_status("Slow mode must be a positive number. Please try again.", 'error')
                    continue
                break
            except ValueError:
                print_status("Please enter a valid number for slow mode.", 'error')
        CHANNEL_SLOW_MODES[channel_id] = slow_mode
    
    # Register channel with smart timer
    smart_timer.add_channel(channel_id)
    smart_timer.current_channel = channel_id
    
    print_status("✅ Bot successfully initialized!", 'success')
    print_status(f"🛡️ Anti-ban mode: ON (Max {ANTI_BAN_CONFIG['max_continuous_hours']}h continuous, {ANTI_BAN_CONFIG['max_daily_hours']}h daily)", 'info')
    print_status(f"🔄 Channel rotation: {'ON' if ANTI_BAN_CONFIG['channel_rotation'] else 'OFF'}", 'info')
    print_status(f"🎭 Response patterns: {', '.join(ANTI_BAN_CONFIG['response_patterns'])}", 'info')
    
    # Show initial dashboard
    bot_dashboard.display_dashboard()
    
    BOT_OWNER_ID = os.getenv("BOT_OWNER_ID", "")
    BOT_PAUSED = False
    CURRENT_MODE = "casual"

    while True:
        try:
            # Hot-reload config
            config_manager.load()
            
            # Apply dynamic owner/mode/slowmode/cooldown
            BOT_OWNER_ID = config_manager.get_owner_id()
            CURRENT_MODE = config_manager.get_mode()
            CHANNEL_SLOW_MODES[channel_id] = config_manager.get_slowmode(channel_id)
            cd_min, cd_max = config_manager.get_cooldown_range()
            
            # Check if we should take a break (anti-ban)
            should_break, break_reason = smart_timer.should_take_break()
            if should_break:
                ui_events.add(f"Taking break: {break_reason}")
                break_duration = smart_timer.get_break_duration()
                print_status(f"🛡️ Taking anti-ban break for {break_duration//60} minutes...", 'warning')
                print_status(f"Reason: {break_reason}", 'info')
                
                # Countdown for break
                for i in range(break_duration//60, 0, -1):
                    print(f"\r{Fore.YELLOW}⏰ Break remaining: {i} minutes{Style.RESET_ALL}", end='')
                    await asyncio.sleep(60)
                print()
                
                # Reset break timer
                smart_timer.last_break = time.time()
                print_status("✅ Break completed! Resuming...", 'success')
                
                # Force refresh messages after break
                print_status("🔄 Refreshing messages after break...", 'info')
                continue  # Skip to next iteration to process messages immediately
            
            # Check if we should rotate channels
            if smart_timer.should_rotate_channel():
                new_channel = smart_timer.get_next_channel()
                if new_channel and new_channel != channel_id:
                    ui_events.add(f"Rotating channel -> {new_channel}")
                    print_status(f"🔄 Rotating to channel: {new_channel}", 'info')
                    channel_id = new_channel
                    smart_timer.current_channel = channel_id
            
            # Fetch recent messages from the channel
            messages = await fetch_channel_messages(channel_id, 20)
            
            if not messages:
                print("❌ No messages found or error occurred.")
                await asyncio.sleep(10)  # Wait 10 seconds before retrying
                continue
            
            # Clean up expired conversations
            smart_timer.cleanup_expired_conversations()
            
            # Check if we received a response from the user we replied to
            response_received = smart_timer.check_response_received(messages)
            if response_received:
                ui_events.add("User responded; resuming session")
                print_status(f"✅ Response received from user! Ready for new messages.", 'success')
            
            # Display recent messages with enhanced formatting
            print_header("Recent Messages")
            for i, msg in enumerate(messages[:20]):
                author = msg.get("author", {}).get("username", "Unknown")
                content = msg.get("content", "")
                if content:
                    truncated_content = f"{content[:50]}..." if len(content) > 50 else content
                    print(f"{Fore.GREEN}{i}.{Style.RESET_ALL} {Fore.YELLOW}{author}{Style.RESET_ALL}: {truncated_content}")
            
            # If waiting for response, show per-second countdown but do not block
            waiting = False
            remaining_wait = 0
            has_convo_reply = False
            convo_user_id = smart_timer.last_reply_to_user
            if smart_timer.waiting_for_response:
                remaining_wait = max(0, int(300 - (time.time() - smart_timer.last_reply_time)))
                if remaining_wait > 0:
                    waiting = True
                    print(f"\r{Fore.YELLOW}⏳ Waiting for conversation reply... ({remaining_wait}s left){Style.RESET_ALL}", end='')
                    bot_dashboard.set_context(channel_id, channel_id, CURRENT_MODE, CHANNEL_SLOW_MODES.get(channel_id, 5), remaining_wait)
                    # Detect if the conversation user has replied already
                    try:
                        for m in messages[:20]:
                            if m.get('author', {}).get('id') == convo_user_id:
                                ts = m.get('timestamp', '')
                                if ts:
                                    mt = datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
                                    if time.time() - mt <= 300:
                                        has_convo_reply = True
                                        break
                    except Exception:
                        has_convo_reply = False
                else:
                    smart_timer.waiting_for_response = False

            # Build two lists: active conversation messages and new user messages
            convo_msgs = []
            new_msgs = []
            for msg in messages[:20]:
                user_id = msg.get('author', {}).get('id')
                if smart_timer.can_continue_conversation(user_id):
                    convo_msgs.append(msg)
                else:
                    new_msgs.append(msg)

            # If waiting and conversation user replied, ONLY process that first
            if waiting and has_convo_reply:
                convo_msgs = [m for m in convo_msgs if m.get('author', {}).get('id') == convo_user_id]
                new_msgs = []
            # If waiting and no conversation reply yet, ignore conversation messages and only process new users
            elif waiting and not has_convo_reply:
                convo_msgs = []

            # Decide processing order based on alternating flag
            process_order = []
            if waiting:
                # Already narrowed above
                process_order = [convo_msgs, new_msgs]
            elif smart_timer.should_prefer_new_first():
                process_order = [new_msgs, convo_msgs]
            else:
                process_order = [convo_msgs, new_msgs]

            # Toggle for next cycle only if not waiting (so preference persists during wait)
            if not waiting:
                smart_timer.set_prefer_new_first(not smart_timer.should_prefer_new_first())

            # Process messages according to order
            reply_sent = False
            for bucket in process_order:
                for msg in bucket:
                    # (reuse existing checks; this block mirrors previous per-message logic)
                    author = msg.get("author", {}).get("username", "Unknown")
                    content = msg.get("content", "")
                    mentions = msg.get("mentions", [])
                    is_reply = msg.get("referenced_message") is not None
                    bot_user_id = DISCORD_TOKEN.split(".")[0] if DISCORD_TOKEN and '.' in DISCORD_TOKEN else None
                    try:
                        timestamp = msg.get('timestamp', '')
                        if not timestamp:
                            continue
                        message_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        message_timestamp = message_time.timestamp()
                        if (author == "Unknown" or 
                            time.time() - message_timestamp > 120 or
                            msg.get('author', {}).get('id') == bot_user_id):
                            continue
                    except Exception:
                        continue
                    content_lower = content.lower()
                    should_respond = False
                    message_type = 'general'
                    user_id = msg.get('author', {}).get('id')
                    username = msg.get('author', {}).get('username', 'Unknown')

                    if smart_timer.can_continue_conversation(user_id):
                        should_respond = True
                        message_type = 'conversation'
                        smart_timer.continue_conversation(user_id, username)
                    elif not should_respond:
                        referenced_message = msg.get('referenced_message')
                        if referenced_message and referenced_message.get('author', {}).get('id') != bot_user_id:
                            should_respond = True
                            message_type = 'reply'
                    elif not should_respond:
                        if ('?' in content_lower and len(content_lower) > 10) or any(q in content_lower for q in ['what is','how do','why does','when will','where can','who is','which one']):
                            should_respond = True
                            message_type = 'question'
                    elif not should_respond:
                        if any(word in content_lower for word in ['help','how','what','why','when','where','who','please','could','would']):
                            should_respond = True
                            message_type = 'help'
                    if not should_respond:
                        continue
                    if user_id and is_on_cooldown(user_id, cd_min, cd_max):
                        continue
                    if random.random() < 0.2:
                        continue

                    context = None
                    message_type = 'general'
                    content_lower = content.lower()
                    if any(mentions):
                        context = f"Someone mentioned you in their message. {author} said: {content}"
                        message_type = 'helpful'
                    elif is_reply:
                        context = f"This is a reply to a previous message. {author} replied: {content}"
                        message_type = 'thinking'
                    elif "?" in content:
                        context = f"Someone asked a question. {author} asked: {content}"
                        message_type = 'thinking'
                    elif any(word in content_lower for word in ["help","how","what","why","when","where","who","please","could","would"]):
                        context = f"Someone needs assistance. {author} said: {content}"
                        message_type = 'helpful'
                    elif any(word in content_lower for word in ["sad","sorry","worried","concerned","upset"]):
                        context = f"Someone seems concerned. {author} said: {content}"
                        message_type = 'sympathetic'
                    elif any(word in content_lower for word in ["happy","great","awesome","amazing","good"]):
                        context = f"Someone is expressing positive emotions. {author} said: {content}"
                        message_type = 'happy'
                    if context:
                        max_retries = 3
                        retry_count = 0
                        while retry_count < max_retries:
                            try:
                                detected_lang = detect_language(content)
                                prompt = f"You are a helpful Discord user. Reply to this message naturally and appropriately:\n{context}"
                                ai_response = get_gemini_response(prompt, detected_lang, message_type)
                                if ai_response and not ai_response.startswith(("AI Error", "Rate limit")):
                                    ui_events.add(f"Reply -> {author}")
                                    human_delay = random.randint(2, 8)
                                    await send_reply(channel_id, ai_response, human_delay, msg.get('id'))
                                    smart_timer.mark_reply_sent(msg.get('author', {}).get('id'))
                                    if message_type != 'conversation':
                                        smart_timer.start_conversation(msg.get('author', {}).get('id'), author)
                                    reply_sent = True
                                    print("✅ Reply sent! Waiting for response...")
                                    print_status(f"⏳ Waiting for response from {author} (5 minutes timeout)", 'info')
                                    break
                                elif ai_response.startswith("Rate limit"):
                                    ui_events.add("Rate limit hit; backing off")
                                    await asyncio.sleep(5)
                                else:
                                    ui_events.add("AI error; retrying")
                                    await asyncio.sleep(2)
                                retry_count += 1
                            except Exception:
                                await asyncio.sleep(2)
                                retry_count += 1
                        if reply_sent:
                            break
                if reply_sent:
                    break

            
            # Update dashboard with context & stats
            bot_dashboard.stats['active_conversations'] = len(smart_timer.active_conversations)
            bot_dashboard.set_context(channel_id, channel_id, CURRENT_MODE, CHANNEL_SLOW_MODES.get(channel_id, 5), CHANNEL_SLOW_MODES.get(channel_id, 5))
            bot_dashboard.display_dashboard()
            
            # Wait before next refresh
            await asyncio.sleep(CHANNEL_SLOW_MODES[channel_id])
            
            # Wait before next refresh with progress indicator
            for i in range(10, 0, -1):
                print(f"\r{Fore.CYAN}⏳ Refreshing in {i} seconds...{Style.RESET_ALL}", end='')
                await asyncio.sleep(1)
            print()  # New line after countdown
        
        except Exception as e:
            print(f"⚠ Error: {e}")
            await asyncio.sleep(10)  # Wait before retrying

asyncio.run(selfbot())
