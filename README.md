# Discord Chat Bot Guide 🤖

Iss guide mein aapko step by step bataya jayega ki Discord Chat Bot ko kaise setup aur run karna hai.

## Prerequisites (Jaruri Cheezein) 🔍

1. **Python** - Latest version install karna hoga
2. **Discord Account** - Discord account hona jaruri hai
3. **Internet Connection** - Stable internet connection
4. **Basic Knowledge** - Basic computer knowledge

## Bot Setup Kaise Karein 🛠️

### Step 1: Discord Token Setup

Discord token prapt karne ke liye: a. Discord web ya app mein login karein b. Browser ke Developer Tools ko kholein (F12 ya Ctrl+Shift+I) c. Network tab par click karein d. Kisi bhi Discord channel ya message par click karein e. Network tab mein requests dikhenge f. Kisi bhi Discord request par click karein g. Headers section mein scroll karke 'Authentication' dhoondhein h. Wahan jo token dikhega, wahi aapka Discord token hai

### Step 2: Gemini API Key Setup

1. [Google AI Studio](https://aistudio.google.com/app/apikey) pe jaiye
2. Sign in karein apne Google account se
3. "Create API Key" pe click karein
4. API key copy karke save karein

### Step 3: Bot Installation 📥

1. Iss repository ko download karein ya clone karein
2. Command prompt ya terminal kholein
3. Bot ke folder mein jaiye:
   ```
   cd path/to/Discord_Chat_Bot
   ```
4. Requirements install karein:
   ```
   pip install -r requirements.txt
   ```

### Step 4: Environment Setup ⚙️

1. `.env` file banaye (ya existing file edit karein)
2. Usme ye information dale:
   ```
   DISCORD_TOKEN="aapka_discord_token"
   GEMINI_API_KEY="aapka_gemini_api_key"
   ```
3. Dono tokens ko apne saved tokens se replace karein

## Bot Ko Run Kaise Karein 🚀

1. Command prompt ya terminal mein bot ke folder mein jaiye
2. Bot start karne ke liye ye command run karein:
   ```
   python bot.py
   ```
3. Bot start hone ke baad, aapse channel ID pucha jayega
4. Slow mode time set karein (default 5 seconds)

## Bot Features 🌟

- Multiple languages support (Hindi, English, Spanish, French, German)
- Smart context understanding
- Emoji responses
- Question answering
- Help and assistance
- Natural conversations

## Important Notes 📝

- Bot ko 24/7 chalane ke liye aapko computer on rakhna hoga
- Channel ID sahi honi chahiye
- Internet connection stable hona chahiye
- Token aur API keys private rakhein, kisi ke saath share na karein

## Troubleshooting 🔧

Agar bot run nahi ho raha hai to ye check karein:

1. Tokens sahi hai ya nahi
2. Internet connection stable hai ya nahi
3. Requirements sahi se install hui hai ya nahi
4. Channel ID sahi hai ya nahi

Agar phir bhi problem hai, to error message check karein aur internet pe search karein ya help ke liye puche.

## Safety Tips 🔒

1. Apne tokens kabhi public ya share na karein
2. Bot ko sirf trusted servers mein add karein
3. Regular updates check karte rahein
4. Backup rakhein important settings ka

Enjoy using your Discord Chat Bot! 🎉