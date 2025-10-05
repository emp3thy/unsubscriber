#!/usr/bin/env python3
"""
Build script for creating standalone Email Unsubscriber executable.

This script uses PyInstaller to package the application into a single executable
that can run on Windows without requiring Python to be installed.
"""

import os
import subprocess
import sys

def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        return install_pyinstaller()

def install_pyinstaller():
    """Install PyInstaller."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller")
        return False

def install_requirements():
    """Install application requirements."""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        print("Failed to install requirements")
        return False

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "build.spec", "--clean"])
        return True
    except subprocess.CalledProcessError:
        print("Build failed")
        return False

def main():
    """Main build process."""
    print("Building Email Unsubscriber standalone executable...")

    if not check_pyinstaller():
        print("Cannot proceed without PyInstaller")
        return 1

    if not install_requirements():
        print("Cannot proceed without requirements")
        return 1

    if not build_executable():
        print("Build failed")
        return 1

    # Check if build succeeded
    exe_path = "dist/EmailUnsubscriber/EmailUnsubscriber.exe"
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path)
        print("Build successful!")
        print(f"Executable: {exe_path}")
        print(f"Size: {size:,}","bytes")
        print("You can now distribute this file to other Windows computers.")
    else:
        print("Build completed but executable not found")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
