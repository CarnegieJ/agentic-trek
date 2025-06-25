#!/usr/bin/env python3
"""
Agentic Trek - Main Entry Point

A modern recreation of the classic Trek game with intelligent AI agents.
This is the main entry point that initializes the game engine and starts
the appropriate interface (ASCII or pygame).

Author: Python Developer
Date: 2025
License: MIT
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from game.engine import GameEngine
from ui.ascii_interface import ASCIIInterface
from ui.pygame_interface import PygameInterface
from utils.config import Config
from utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Agentic Trek - Classic Space Strategy Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start with default pygame interface
  python main.py --ascii            # Start with ASCII interface
  python main.py --debug            # Enable debug logging
  python main.py --config custom.yaml  # Use custom configuration
        """
    )
    
    parser.add_argument(
        '--ascii', 
        action='store_true',
        help='Use ASCII text interface instead of pygame graphics'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/default.yaml',
        help='Configuration file path (default: config/default.yaml)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducible games'
    )
    
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'normal', 'hard', 'expert'],
        default='normal',
        help='Game difficulty level (default: normal)'
    )
    
    parser.add_argument(
        '--load',
        type=str,
        help='Load saved game file'
    )
    
    return parser.parse_args()


def display_banner():
    """Display the game banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    AGENTIC TREK                              ║
    ║                                                              ║
    ║    A Modern Recreation of the Classic Space Strategy Game    ║
    ║              Enhanced with Intelligent AI Agents            ║
    ║                                                              ║
    ║                     "Live Long and Prosper"                  ║
    ╚══════════════════════════════════════════════════════════════╝
    
         *           .               *                    .
              .                 .            *
    *                    .                        .           *
         .        *                                    .
                      USS ENTERPRISE NCC-1701
                           ___
                      _.-'   '-._
                   .-'           '-.
                  /                 \\
                 |    ___     ___    |
                 |   (   )   (   )   |
                  \\   '-'     '-'   /
                   '-.             .-'
                      '-._     _.-'
                          '---'
    
    """
    print(banner)


def main():
    """Main entry point for the Agentic Trek game."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging
        log_level = logging.DEBUG if args.debug else logging.INFO
        logger = setup_logger(level=log_level)
        
        logger.info("Starting Agentic Trek")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Arguments: {vars(args)}")
        
        # Display banner
        if not args.ascii:
            display_banner()
        
        # Load configuration
        config = Config(args.config)
        logger.info(f"Loaded configuration from: {args.config}")
        
        # Override config with command line arguments
        if args.difficulty:
            config.set('game.difficulty', args.difficulty)
        if args.seed:
            config.set('game.random_seed', args.seed)
        
        # Initialize game engine
        logger.info("Initializing game engine...")
        game_engine = GameEngine(config)
        
        # Load saved game if specified
        if args.load:
            logger.info(f"Loading saved game: {args.load}")
            game_engine.load_game(args.load)
        
        # Initialize appropriate interface
        if args.ascii:
            logger.info("Starting ASCII interface...")
            interface = ASCIIInterface(game_engine)
        else:
            logger.info("Starting pygame interface...")
            try:
                import pygame
                interface = PygameInterface(game_engine)
            except ImportError:
                logger.warning("pygame not available, falling back to ASCII interface")
                interface = ASCIIInterface(game_engine)
        
        # Start the game
        logger.info("Starting game loop...")
        interface.run()
        
        logger.info("Game ended normally")
        
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        print("\nGame interrupted. Live long and prosper!")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error occurred: {e}")
        print("Check the log files for detailed error information.")
        sys.exit(1)
    
    finally:
        # Cleanup
        logger.info("Performing cleanup...")
        # Any cleanup code would go here


if __name__ == "__main__":
    main()
