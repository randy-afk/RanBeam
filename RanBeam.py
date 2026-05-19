"""
RanBeam.py
===========
Entry point. Run with:
    python RanBeam.py
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import launch

if __name__ == "__main__":
    launch()
