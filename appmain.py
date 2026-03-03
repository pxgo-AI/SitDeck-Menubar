#!/usr/bin/env python3
"""
SitDeck Menubar — Main Entry Point
"""

import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from menubar import SitDeckMenuBarApp


def main():
    """Application entry point"""
    app = SitDeckMenuBarApp()
    app.run()


if __name__ == "__main__":
    main()