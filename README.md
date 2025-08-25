# Discord Gemini Bot (Advanced, Anti‑Ban, Smart Conversations)

A Discord chat assistant with:
- Auto dependency install on first run
- Hot‑reloadable config.json
- Multiple Gemini API keys (from .env and/or config), automatic rotation with per‑key cooldown/backoff on 429
- Human‑like behavior, anti‑ban controls, per‑user cooldowns, and channel slowmode
- Smart conversations: waiting windows, alternating priority, 10 user cap
- Owner text commands and a live terminal dashboard with recent events

> Note: For educational purposes. Please follow Discord ToS and local laws.

## 1) Requirements
- Python 3.10+
- Discord token
- One or more Gemini API keys (free or billing‑enabled)

## 2) Quick Start

Windows (easiest):
```bat
# A) Double‑click
run_bot.bat

# B) Or from terminal
python run_bot.py
```

Cross‑platform direct run:
```bash
python bot.py
```
This auto‑installs missing packages and starts the bot.

## 3) Environment (.env)
Create a `.env` file in the project root:
```env
DISCORD_TOKEN=your_discord_token
GEMINI_API_KEY=your_primary_gemini_key
BOT_OWNER_ID=your_discord_user_id

# Optional: multiple keys (any of these formats work)
GEMINI_API_KEYS=key2,key3,key4
# or
GEMINI_API_KEYS=key2;key3;key4
# or multiline
GEMINI_API_KEYS=key2
key3
key4
```
- The bot reads keys from both `.env` (GEMINI_API_KEY + GEMINI_API_KEYS) and `config.json.gemini_api_keys`. Lists are combined and de‑duplicated.

## 4) Configuration (config.json)
`config.json` is hot‑reloaded every loop (no restart needed):
```json
{
  "default_mode": "casual",
  "cooldown_seconds": { "min": 60, "max": 120 },
  "channels": {
    "default_slowmode": 5,
    "overrides": {
      "123456789012345678": 8
    }
  },
  "response_patterns": ["casual", "professional", "funny", "helpful", "quiet"],
  "webhook_url": "",
  "owner_id": "123456789012345678",
  "gemini_api_keys": ["key5", "key6"]
}
```
- `default_mode`: quiet/casual/professional/funny/helpful.
- `cooldown_seconds`: per‑user cooldown window (randomized between min–max).
- `channels.default_slowmode`: global refresh delay (seconds).
- `channels.overrides`: per‑channel slowmode override.
- `gemini_api_keys`: optional extra keys; combined with `.env` keys.

## 5) Running
On start the bot:
1) Installs missing requirements
2) Validates tokens/connectivity (Gemini 429 shows as a warning; bot still runs)
3) Prompts for channel IDs (comma‑separated numeric IDs)
4) Prompts for slowmode (or uses config/default)
5) Shows a live dashboard with stats and recent events

## 6) Key Features (current behavior)
- Multiple Gemini keys & backoff:
  - Reads keys from `.env` and `config.json`, deduped and rotated automatically
  - On 429/quota, marks current key on cooldown using `retry_delay` seconds (if provided) and switches to the next available key
- No greeting starts:
  - Leading “hey/hi/hello …” are stripped from AI replies
- Emoji placement:
  - Never prefix; prefers inline after a relevant keyword; otherwise suffix at the end
- Anti‑ban controls:
  - Per‑user cooldown (configurable, default 60–120s randomized)
  - Channel slowmode (configurable and per‑channel overrides)
  - Random skip (20%) to avoid over‑activity
  - Breaks, channel rotation, quiet mode pattern support
- Conversations:
  - Active session window: 5 minutes per user
  - While waiting for a conversation reply, the bot shows a live countdown and replies to new users without blocking
  - If the conversation user replies, the bot prioritizes that message immediately on the next poll
  - After slowmode, bot checks conversation user first; if no new message from them, replies to new users
  - Conversation cap: max 10 users; expired (>5 minutes inactive) or oldest sessions are removed to admit new users

## 7) Owner Commands (in‑channel text)
Only `owner_id`/`BOT_OWNER_ID` can use these:
```
!pause            # pause replies
!resume           # resume replies
!mode <name>      # quiet / casual / professional / funny / helpful
!slowmode <sec>   # set channel slowmode seconds
!status           # print dashboard to console
!rotate           # rotate to next channel (if configured)
```

## 8) Dashboard
- Header line shows: channel, mode, slowmode, next refresh ETA
- Stats: processed, responses, errors, response rate, active conversations
- Recent events: replies, mode/slowmode changes, rotations, errors, rate‑limits
- Shows a per‑second countdown when waiting for a conversation reply

## 9) Tips
- To reduce 429s, add multiple keys in `.env`/`config.json`, or use a billing‑enabled key
- Keep slowmode and per‑user cooldown conservative to mimic human pace
- Use `quiet` mode during busy hours

## 10) Troubleshooting
- 429/quota warnings: normal for free‑tier; bot rotates to next key automatically and cools down the throttled key
- Unauthorized (401) from Discord: check `DISCORD_TOKEN`
- Module not found: run `python bot.py` once (auto‑installs) or `pip install -r requirements.txt`
- Unicode/emoji on Windows: use `run_bot.py` or Windows Terminal

## 11) Project Files
- `bot.py`: main app (AI, logic, dashboard)
- `config.json`: hot‑reloaded settings
- `.env`: tokens and optional GEMINI_API_KEYS
- `run_bot.py` / `run_bot.bat`: one‑click launchers
- `requirements*.txt`: dependency lists
- `install_requirements.py`: optional helper (not required)

Enjoy building responsibly! 🎯