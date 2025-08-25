#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Requirements Installer for Discord Bot
Automatically installs missing packages when running the bot
"""

import subprocess
import sys
import importlib
import os

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False

def get_essential_packages():
    """Get list of essential packages"""
    return [
        "discord",
        "requests", 
        "asyncio",
        "python-dotenv",
        "google.generativeai",
        "langdetect",
        "emoji",
        "colorama",
        "psutil",
        "schedule",
        "fake-useragent",
        "python-dateutil"
    ]

def get_package_mapping():
    """Map package names to pip install names"""
    return {
        "discord": "discord==2.3.2",
        "requests": "requests==2.31.0",
        "asyncio": "asyncio==3.4.3",
        "python-dotenv": "python-dotenv==1.0.0",
        "google.generativeai": "google-generativeai==0.3.2",
        "langdetect": "langdetect==1.0.9",
        "emoji": "emoji==2.10.1",
        "colorama": "colorama==0.4.6",
        "psutil": "psutil==5.9.8",
        "schedule": "schedule==1.2.1",
        "fake-useragent": "fake-useragent==1.4.0",
        "python-dateutil": "python-dateutil==2.8.2"
    }

def auto_install_requirements():
    """Automatically install missing requirements"""
    print("🔍 Checking Discord Bot Requirements...")
    print("=" * 50)
    
    missing_packages = []
    package_mapping = get_package_mapping()
    
    # Check each essential package
    for package in get_essential_packages():
        if not check_package(package):
            missing_packages.append(package)
            print(f"❌ {package} - NOT INSTALLED")
        else:
            print(f"✅ {package} - INSTALLED")
    
    if not missing_packages:
        print("\n🎉 All requirements are already installed!")
        return True
    
    print(f"\n📦 Found {len(missing_packages)} missing packages")
    print("🚀 Starting automatic installation...")
    print("=" * 50)
    
    # Install missing packages
    failed_packages = []
    for package in missing_packages:
        pip_name = package_mapping.get(package, package)
        if not install_package(pip_name):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install {len(failed_packages)} packages:")
        for package in failed_packages:
            print(f"   - {package}")
        return False
    
    print("\n🎉 All packages installed successfully!")
    return True

def main():
    """Main function"""
    print("🤖 Discord Bot Requirements Installer")
    print("=" * 50)
    
    # Check if running as main
    if __name__ == "__main__":
        success = auto_install_requirements()
        if success:
            print("\n🚀 Ready to run Discord Bot!")
            print("💡 Run: python bot.py")
        else:
            print("\n⚠️ Some packages failed to install")
            print("💡 Try: pip install -r requirements-essential.txt")
    
    return success

if __name__ == "__main__":
    main()
