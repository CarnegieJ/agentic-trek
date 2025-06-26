#!/usr/bin/env python3
"""
Test torpedo trajectory calculation
"""

import math
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game.combat import CombatSystem
from utils.config import Config

def test_torpedo_trajectory():
    """Test torpedo trajectory calculations."""
    
    # Create a basic config
    config = Config()
    combat = CombatSystem(config)
    
    print("Testing Torpedo Trajectory Calculations")
    print("=" * 50)
    
    # Test case: Enterprise at (4,4), Klingon at (4,5) - directly south
    enterprise_pos = (4, 4)
    klingon_pos = (4, 5)
    
    print(f"Enterprise position: {enterprise_pos}")
    print(f"Klingon position: {klingon_pos}")
    print(f"Klingon is directly SOUTH of Enterprise")
    print()
    
    # Test different courses
    test_courses = [0, 90, 180, 270]
    course_names = ["North (0°)", "East (90°)", "South (180°)", "West (270°)"]
    
    for course, name in zip(test_courses, course_names):
        print(f"Testing course {name}:")
        trajectory = combat._calculate_torpedo_trajectory(enterprise_pos, course, 1)
        print(f"  Trajectory points: {trajectory[:10]}")  # First 10 points
        
        # Check if Klingon position is in trajectory
        if klingon_pos in trajectory:
            print(f"  ✅ WOULD HIT Klingon at {klingon_pos}")
        else:
            print(f"  ❌ WOULD MISS Klingon at {klingon_pos}")
        print()
    
    # Test with wider spread
    print("Testing 180° course with spread 10:")
    trajectory_wide = combat._calculate_torpedo_trajectory(enterprise_pos, 180, 10)
    print(f"  Trajectory points (first 20): {trajectory_wide[:20]}")
    
    if klingon_pos in trajectory_wide:
        print(f"  ✅ WOULD HIT Klingon at {klingon_pos} with wide spread")
    else:
        print(f"  ❌ WOULD MISS Klingon at {klingon_pos} even with wide spread")
    
    print()
    print("Coordinate System Analysis:")
    print("Standard math: 0° = East, 90° = North, 180° = West, 270° = South")
    print("Game expectation: 180° should be South")
    
    # Manual calculation for 180°
    print()
    print("Manual calculation for 180° course:")
    course_rad = math.radians(180)
    for distance in range(1, 6):
        x = enterprise_pos[0] + distance * math.cos(course_rad)
        y = enterprise_pos[1] + distance * math.sin(course_rad)
        print(f"  Distance {distance}: ({x:.1f}, {y:.1f}) -> ({int(x)}, {int(y)})")

if __name__ == "__main__":
    test_torpedo_trajectory()
