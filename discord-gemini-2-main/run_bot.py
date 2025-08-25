#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Discord Bot Launcher
Automatically handles requirements and launches the bot
"""

import os
import sys
import subprocess
import time

# Ensure UTF-8 console on Windows to avoid emoji encoding errors
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
except Exception:
    pass

def run_command(command, description):
    """Run a command with description"""
    print(f"\n🚀 {description}")
    print(f"💻 Command: {command}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("\n🔧 Upgrading pip...")
    return run_command("python -m pip install --upgrade pip", "Upgrading pip")

def install_requirements():
    """Install requirements from essential file"""
    if os.path.exists("requirements-essential.txt"):
        return run_command("pip install -r requirements-essential.txt", "Installing essential requirements")
    elif os.path.exists("requirements.txt"):
        return run_command("pip install -r requirements.txt", "Installing requirements")
    else:
        print("⚠️ No requirements file found, installing core packages...")
        core_packages = [
            "discord==2.3.2",
            "requests==2.31.0", 
            "asyncio==3.4.3",
            "python-dotenv==1.0.0",
            "google-generativeai==0.3.2",
            "langdetect==1.0.9",
            "emoji==2.10.1",
            "colorama==0.4.6",
            "psutil==5.9.8",
            "schedule==1.2.1",
            "fake-useragent==1.4.0",
            "python-dateutil==2.8.2"
        ]
        
        for package in core_packages:
            if not run_command(f"pip install {package}", f"Installing {package}"):
                return False
        return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("\n⚠️ .env file not found!")
        print("📝 Creating template .env file...")
        
        env_content = """# Discord Bot Configuration
# Replace these placeholder values with your actual tokens

# Your Discord User Token (get this from Discord Developer Tools)
DISCORD_TOKEN="your_discord_token_here"

# Your Gemini API Key (get this from Google AI Studio)
GEMINI_API_KEY="your_gemini_api_key_here"
"""
        
        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print("✅ .env template created!")
            print("⚠️ Please edit .env file with your actual tokens before running the bot!")
            return False
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    print("✅ .env file found")
    return True

def launch_bot():
    """Launch the Discord bot"""
    print("\n🤖 Launching Discord Bot...")
    print("=" * 50)
    
    if os.path.exists("bot.py"):
        return run_command("python bot.py", "Starting Discord Bot")
    else:
        print("❌ bot.py file not found!")
        return False

def main():
    """Main launcher function"""
    print("🚀 Discord Bot Smart Launcher")
    print("=" * 50)
    
    # Step 1: Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Upgrade pip
    upgrade_pip()
    
    # Step 3: Install requirements
    if not install_requirements():
        print("\n❌ Failed to install requirements!")
        input("Press Enter to exit...")
        return
    
    # Step 4: Check .env file
    if not check_env_file():
        print("\n⚠️ Please configure your .env file first!")
        print("💡 Edit .env file with your Discord token and Gemini API key")
        input("Press Enter to exit...")
        return
    
    # Step 5: Launch bot
    if launch_bot():
        print("\n🎉 Bot launched successfully!")
    else:
        print("\n❌ Failed to launch bot!")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
