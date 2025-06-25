#!/usr/bin/env python3
"""
Screenshot Generation Script

This script helps generate screenshots for documentation by running
the game and capturing interface images.
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import pygame
    from game.engine import GameEngine
    from ui.pygame_interface import PygameInterface
    from utils.config import Config
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Make sure you're running from the project root and have installed dependencies.")
    sys.exit(1)


def capture_pygame_interface():
    """Capture screenshots of the pygame interface."""
    print("Starting pygame interface for screenshot capture...")
    
    # Initialize game
    config = Config()
    game_engine = GameEngine(config)
    interface = PygameInterface(game_engine)
    
    # Create screenshots directory
    screenshots_dir = Path("assets/images/screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    print("Game started. Screenshots will be saved automatically.")
    print("Controls:")
    print("  F5 - Capture main game screenshot")
    print("  F6 - Capture galaxy map screenshot") 
    print("  F7 - Capture help screen screenshot")
    print("  ESC - Exit")
    
    # Add screenshot capture to the interface
    original_handle_keydown = interface.handle_keydown
    
    def enhanced_handle_keydown(event):
        if event.key == pygame.K_F5:
            # Capture main game view
            filename = screenshots_dir / "pygame_interface.png"
            pygame.image.save(interface.screen, str(filename))
            interface.add_message(f"Screenshot saved: {filename}")
            print(f"Main game screenshot saved: {filename}")
            
        elif event.key == pygame.K_F6:
            # Switch to galaxy map and capture
            interface.current_view = 'galaxy_map'
            interface.draw()
            pygame.display.flip()
            filename = screenshots_dir / "galaxy_map.png"
            pygame.image.save(interface.screen, str(filename))
            interface.add_message(f"Galaxy map screenshot saved: {filename}")
            print(f"Galaxy map screenshot saved: {filename}")
            
        elif event.key == pygame.K_F7:
            # Switch to help screen and capture
            interface.current_view = 'help'
            interface.draw()
            pygame.display.flip()
            filename = screenshots_dir / "help_screen.png"
            pygame.image.save(interface.screen, str(filename))
            interface.add_message(f"Help screen screenshot saved: {filename}")
            print(f"Help screen screenshot saved: {filename}")
            
        else:
            original_handle_keydown(event)
    
    interface.handle_keydown = enhanced_handle_keydown
    
    # Run the interface
    try:
        interface.run()
    except Exception as e:
        print(f"Error running interface: {e}")
    finally:
        pygame.quit()


def generate_ascii_banner():
    """Generate ASCII banner for documentation."""
    banner_file = Path("assets/images/trek_banner.txt")
    
    if banner_file.exists():
        print(f"ASCII banner already exists at: {banner_file}")
        with open(banner_file, 'r') as f:
            print("Current banner:")
            print(f.read())
    else:
        print("ASCII banner file not found.")


def create_placeholder_images():
    """Create placeholder image files with instructions."""
    images_dir = Path("assets/images")
    images_dir.mkdir(exist_ok=True)
    
    placeholders = {
        "pygame_interface.png": "Pygame interface screenshot - press F5 in game to capture",
        "galaxy_map.png": "Galaxy map screenshot - press F6 in game to capture", 
        "help_screen.png": "Help screen screenshot - press F7 in game to capture",
        "trek_banner.png": "Game banner image - create manually or convert from ASCII art"
    }
    
    for filename, description in placeholders.items():
        filepath = images_dir / filename
        if not filepath.exists():
            # Create a simple text file as placeholder
            with open(filepath.with_suffix('.txt'), 'w') as f:
                f.write(f"# Placeholder for {filename}\n")
                f.write(f"# {description}\n")
                f.write(f"# Replace this file with the actual image\n")
            print(f"Created placeholder: {filepath.with_suffix('.txt')}")


def main():
    """Main function."""
    print("Agentic Trek - Screenshot Generation Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/generate_screenshots.py pygame    - Capture pygame screenshots")
        print("  python scripts/generate_screenshots.py ascii     - Show ASCII banner")
        print("  python scripts/generate_screenshots.py placeholders - Create placeholder files")
        return
    
    command = sys.argv[1].lower()
    
    if command == "pygame":
        capture_pygame_interface()
    elif command == "ascii":
        generate_ascii_banner()
    elif command == "placeholders":
        create_placeholder_images()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: pygame, ascii, placeholders")


if __name__ == "__main__":
    main()
