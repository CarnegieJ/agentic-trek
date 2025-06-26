#!/usr/bin/env python3
"""
Debug quadrant data structure
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.galaxy import Galaxy
from utils.config import Config

def debug_quadrant_data():
    """Debug the quadrant data structure."""
    
    config = Config()
    galaxy = Galaxy(config)
    
    print("Debugging Quadrant Data Structure")
    print("=" * 40)
    
    # Generate galaxy
    galaxy.generate()
    
    # Find a quadrant with Klingons
    for coords, quadrant in galaxy.quadrants.items():
        klingons, bases, stars = galaxy.get_quadrant_summary(coords)
        if klingons > 0:
            print(f"Found quadrant {coords} with {klingons} Klingons")
            
            # Get quadrant data
            quadrant_data = galaxy.get_quadrant_data(coords)
            print(f"Quadrant data type: {type(quadrant_data)}")
            print(f"Quadrant data: {quadrant_data}")
            
            # Check for Klingons
            klingon_positions = []
            for pos, obj_type in quadrant_data.items():
                print(f"  Position {pos}: {obj_type} (type: {type(obj_type)})")
                if obj_type == 'K':
                    klingon_positions.append(pos)
            
            print(f"Klingon positions found: {klingon_positions}")
            
            # Test the display
            ship_pos = (4, 4)  # Dummy ship position
            display = galaxy.format_quadrant_display(quadrant_data, ship_pos)
            print(f"Display format:")
            print(display)
            
            break
    else:
        print("No quadrants with Klingons found!")

if __name__ == "__main__":
    debug_quadrant_data()
