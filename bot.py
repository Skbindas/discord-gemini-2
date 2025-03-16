import os
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
CHANNEL_SLOW_MODES = {}

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
                 ':smiling_face_with_heart-eyes:', ':winking_face:'],
        'thinking': [':thinking_face:', ':face_with_monocle:', ':face_with_raised_eyebrow:', 
                    ':face_with_hand_over_mouth:', ':nerd_face:'],
        'helpful': [':thumbs_up:', ':OK_hand:', ':raising_hands:', ':folded_hands:', 
                   ':sparkles:', ':light_bulb:'],
        'sympathetic': [':slightly_smiling_face:', ':hugging_face:', ':relieved_face:']
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

# Initialize rate limiter (max 30 requests per minute)
ai_rate_limiter = RateLimiter(max_requests=30, time_window=60)

# AI Reply Function with improved context handling
def get_gemini_response(prompt, detected_lang, message_type='general'):
    try:
        if not ai_rate_limiter.can_make_request():
            return "Rate limit exceeded. Please try again later."

        # Enhanced language and context instructions with emphasis on brevity
        lang_instructions = {
            'hi': 'Reply in Hindi language with 1-2 friendly sentences.',
            'en': 'Reply in English language with 1-2 friendly sentences.',
            'es': 'Reply in Spanish language with 1-2 friendly sentences.',
            'fr': 'Reply in French language with 1-2 friendly sentences.',
            'de': 'Reply in German language with 1-2 friendly sentences.'
        }
        
        # Response templates based on message type
        templates = {
            'general': ['Keep the response natural and conversational.',
                       'Add some personality to the response.',
                       'Make the response engaging but concise.'],
            'question': ['Provide a helpful and clear answer.',
                        'Be informative but keep it simple.',
                        'Answer directly with a friendly tone.'],
            'help': ['Offer assistance in a supportive way.',
                     'Be encouraging and helpful.',
                     'Provide guidance with a positive tone.'],
            'reply': ['Acknowledge the previous message naturally.',
                      'Respond in a contextually appropriate way.',
                      'Keep the conversation flowing smoothly.']
        }
        
        # Select random template based on message type
        template = random.choice(templates.get(message_type, templates['general']))
        
        full_prompt = f"{lang_instructions.get(detected_lang, 'Reply with 1-2 friendly sentences.')}\n" \
                     f"{template}\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Randomly decide emoji placement and count
        emoji_count = random.randint(1, 3)
        emojis = get_random_emojis(count=emoji_count, sentiment=message_type)
        
        # Different emoji placements
        placement = random.choice(['prefix', 'suffix', 'both'])
        if placement == 'prefix':
            return f"{emojis} {response_text}"
        elif placement == 'suffix':
            return f"{response_text} {emojis}"
        else:
            prefix_emojis = get_random_emojis(count=1, sentiment=message_type)
            suffix_emojis = get_random_emojis(count=1, sentiment=message_type)
            return f"{prefix_emojis} {response_text} {suffix_emojis}"    
    except Exception as e:
        return f"AI Error: {e}"

# Custom Timer Function
async def send_reply(channel_id, message, delay, message_id=None):
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

# Function to fetch messages from a channel
async def fetch_channel_messages(channel_id, limit=20):
    try:
        messages = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}", headers=HEADERS).json()
        return messages
    except Exception as e:
        print(f"⚠ Error fetching messages: {e}")
        return []

from colorama import init, Fore, Back, Style

# Initialize colorama for Windows
init()

# Terminal UI Enhancement Functions
def print_header(text):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{text.center(50)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}{Style.RESET_ALL}\n")

def print_status(text, status_type='info'):
    colors = {
        'success': Fore.GREEN,
        'error': Fore.RED,
        'info': Fore.BLUE,
        'warning': Fore.YELLOW
    }
    color = colors.get(status_type, Fore.WHITE)
    print(f"{color}{Style.BRIGHT}{text}{Style.RESET_ALL}")

# Selfbot Main Function
async def selfbot():
    print_header("Discord Chat Bot")
    print_status("Bot is starting...", 'info')
    
    # Ask for channel ID with validation
    while True:
        channel_id = input(f"{Fore.CYAN}👉 Enter channel ID: {Style.RESET_ALL}").strip()
        if not channel_id:
            print_status("Channel ID cannot be empty. Please try again.", 'error')
            continue
        if not channel_id.isdigit():
            print_status("Channel ID must be a numeric value. Please try again.", 'error')
            continue
        break

    # Ask for slow mode with validation
    if channel_id not in CHANNEL_SLOW_MODES:
        while True:
            slow_mode_input = input(f"{Fore.CYAN}🔄 Enter Slow Mode (seconds, default 5): {Style.RESET_ALL}").strip()
            if not slow_mode_input:  # Use default value if empty
                slow_mode = 5
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
    
    print_status("✅ Bot successfully initialized!", 'success')
    
    while True:
        try:
            # Fetch recent messages from the channel
            messages = await fetch_channel_messages(channel_id, 20)
            
            if not messages:
                print("❌ No messages found or error occurred.")
                await asyncio.sleep(10)  # Wait 10 seconds before retrying
                continue
            
            # Display recent messages with enhanced formatting
            print_header("Recent Messages")
            for i, msg in enumerate(messages[:20], 1):
                author = msg.get("author", {}).get("username", "Unknown")
                content = msg.get("content", "")
                if content:
                    truncated_content = f"{content[:50]}..." if len(content) > 50 else content
                    print(f"{Fore.GREEN}{i}.{Style.RESET_ALL} {Fore.YELLOW}{author}{Style.RESET_ALL}: {truncated_content}")
            
            # Automatically process and respond to messages
            for msg in messages[:20]:
                author = msg.get("author", {}).get("username", "Unknown")
                content = msg.get("content", "")
                mentions = msg.get("mentions", [])
                is_reply = msg.get("referenced_message") is not None
                
                # Get bot's user ID from token
                bot_user_id = DISCORD_TOKEN.split(".")[0] if DISCORD_TOKEN and '.' in DISCORD_TOKEN else None
                
                # Skip messages from the bot itself, messages older than 5 minutes, or from unknown authors
                try:
                    timestamp = msg.get('timestamp', '')
                    if not timestamp:
                        continue
                        
                    # Convert Discord's ISO timestamp to datetime object
                    message_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    message_timestamp = message_time.timestamp()
                    
                    # Skip if message is from bot itself or older than 5 minutes
                    if (author == "Unknown" or 
                        time.time() - message_timestamp > 300 or
                        msg.get('author', {}).get('id') == bot_user_id):
                        continue
                        
                except Exception as e:
                    print(f"⚠ Error parsing timestamp: {e}")
                    continue
                
                # Enhanced context analysis
                content = msg.get('content', '').lower()
                should_respond = False
                message_type = 'general'
                
                # Check if message is a reply to another message
                referenced_message = msg.get('referenced_message')
                if referenced_message:
                    # Only respond if the message is replying to someone else's message (not bot's message)
                    if referenced_message.get('author', {}).get('id') != bot_user_id:
                        should_respond = True
                        message_type = 'reply'
                
                # Check if message is a question (but not from bot)
                elif '?' in content or any(q in content for q in ['what', 'how', 'why', 'when', 'where', 'who', 'which']):
                    should_respond = True
                    message_type = 'question'
                
                # Check if message needs help or assistance (but not from bot)
                elif any(word in content for word in ['help', 'please', 'can you', 'could you']):
                    should_respond = True
                    message_type = 'help'
                
                # Only process messages that need response
                if not should_respond:
                    continue
                
                # Initialize context variable
                context = None
                message_type = 'general'
                
                # Analyze message content for sentiment and context
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
                elif any(word in content_lower for word in ["help", "how", "what", "why", "when", "where", "who", "please", "could", "would"]):
                    context = f"Someone needs assistance. {author} said: {content}"
                    message_type = 'helpful'
                elif any(word in content_lower for word in ["sad", "sorry", "worried", "concerned", "upset"]):
                    context = f"Someone seems concerned. {author} said: {content}"
                    message_type = 'sympathetic'
                elif any(word in content_lower for word in ["happy", "great", "awesome", "amazing", "good"]):
                    context = f"Someone is expressing positive emotions. {author} said: {content}"
                    message_type = 'happy'
                
                # Generate and send response if context is meaningful
                if context:
                    max_retries = 3
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            # Detect language of the message
                            detected_lang = detect_language(content)
                            
                            prompt = f"You are a helpful Discord user. Reply to this message naturally and appropriately:\n{context}"
                            ai_response = get_gemini_response(prompt, detected_lang, message_type)
                            
                            if ai_response and not ai_response.startswith(("AI Error", "Rate limit")):
                                print(f"🤖 Responding to {author} in {detected_lang}: {ai_response}")
                                await send_reply(channel_id, ai_response, CHANNEL_SLOW_MODES[channel_id] + random.randint(1, 3), msg.get('id'))
                                print("✅ Reply sent!")
                                break
                            elif ai_response.startswith("Rate limit"):
                                print("⚠ Rate limit reached, waiting before retry...")
                                await asyncio.sleep(5)
                            else:
                                print(f"⚠ AI Error occurred: {ai_response}")
                                await asyncio.sleep(2)
                            
                            retry_count += 1
                        except Exception as e:
                            print(f"⚠ Error in response generation: {e}")
                            await asyncio.sleep(2)
                            retry_count += 1
                    
                    if retry_count == max_retries:
                        print("❌ Max retries reached for this message")

            
            # Wait before next refresh
            print_status("\n⏳ Monitoring for new messages...", 'info')
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