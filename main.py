#!/usr/bin/env python3
"""
King God Castle AIO - Main Entry Point
A modern, cross-platform GUI application built with CustomTkinter
"""

import sys, os
from pathlib import Path

# Add src directory to Python path
src_path = os.getcwd()
sys.path.insert(0, str(src_path))

from src.gui.main_window import MainWindow


def main():
    """Main entry point for the application"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
