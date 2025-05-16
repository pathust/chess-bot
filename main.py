#!/usr/bin/env python3
"""
Chess Application Entry Point
This is the main entry point for the chess application.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

from utils.error_handler import ErrorHandler
from utils.logger import Logger
from ui.app import ChessApp

def main():
    """Main application entry point."""
    # Initialize the logger
    logger = Logger.get_instance()
    logger.info("Starting chess application")
    
    # Install global exception handler
    ErrorHandler.install_global_except_hook()
    
    # Initialize the application
    app = ChessApp(sys.argv)
    
    # Run the application
    exit_code = app.exec_()
    
    # Log application exit
    logger.info(f"Chess application exited with code {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())