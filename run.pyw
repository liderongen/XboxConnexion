"""
XboxConnexion Windowless Launcher (.pyw)
Runs XboxConnexion without opening a command prompt console window.
"""
import sys
import os

# Set current working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from src.main import main

if __name__ == "__main__":
    main()
