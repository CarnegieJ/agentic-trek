#!/usr/bin/env python3
"""
Debug Klingon visibility issue
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.engine import GameEngine
from utils.config import Config

def debug_klingon_issue():
    """Debug why Klingons aren't visible."""
    
    config = Config()
    engine = GameEngine(config)
    
    print("Debugging Klingon Visibility Issue")
    print("=" * 40)
    
    # Setup new game
    engine._setup_new_game()
    
    # Find quadrants with Klingons using long range scan
    print("Scanning all quadrants for Klingons...")
    
    for qx in range(1, 9):
        for qy in range(1, 9):
            coords = (qx, qy)
            klingons, bases, stars = engine.galaxy.get_quadrant_summary(coords)
            
            if klingons > 0:
                print(f"\nFound quadrant {coords} with {klingons} Klingons")
                
                # Get raw quadrant data
                quadrant_data = engine.galaxy.get_quadrant_data(coords)
                print(f"Raw quadrant data: {quadrant_data}")
                
                # Check what the display shows
                ship_pos = (4, 4)  # Dummy position
                display = engine.galaxy.format_quadrant_display(quadrant_data, ship_pos)
                print("Display output:")
                print(display)
                
                # Check if 'K' is in the data
                klingon_positions = [pos for pos, obj in quadrant_data.items() if obj == 'K']
                print(f"Klingon positions in data: {klingon_positions}")
                
                # Test combat system data
                print(f"Combat system would see: {quadrant_data}")
                
                # Only check first quadrant with Klingons
                break
    else:
        print("No quadrants with Klingons found!")

if __name__ == "__main__":
    debug_klingon_issue()
