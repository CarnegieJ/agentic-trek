"""
Galaxy Management System

This module handles the generation and management of the galaxy map,
including quadrant data, object placement, and spatial calculations.
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from ..utils.logger import get_logger


@dataclass
class QuadrantData:
    """Data structure for a single quadrant."""
    coordinates: Tuple[int, int]
    klingons: int
    starbases: int
    stars: int
    objects: Dict[Tuple[int, int], str]  # Position -> Object type mapping
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'QuadrantData':
        """Create from dictionary for deserialization."""
        # Convert string keys back to tuples for objects dict
        if 'objects' in data and isinstance(data['objects'], dict):
            objects = {}
            for key, value in data['objects'].items():
                if isinstance(key, str) and ',' in key:
                    # Convert string key back to tuple
                    coords = tuple(map(int, key.strip('()').split(', ')))
                    objects[coords] = value
                else:
                    objects[key] = value
            data['objects'] = objects
        
        return cls(**data)


class Galaxy:
    """
    Galaxy management system for the Trek game.
    
    Manages an 8x8 grid of quadrants, each containing various space objects
    including Klingon ships, starbases, and stars. Provides methods for
    navigation, scanning, and spatial calculations.
    """
    
    GALAXY_SIZE = 8
    QUADRANT_SIZE = 8
    
    # Object type constants
    EMPTY = '.'
    ENTERPRISE = 'E'
    KLINGON = 'K'
    STARBASE = 'B'
    STAR = '*'
    
    def __init__(self, config):
        """Initialize the galaxy system."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # Galaxy grid - 8x8 quadrants
        self.quadrants: Dict[Tuple[int, int], QuadrantData] = {}
        
        # Configuration parameters
        self.total_klingons = config.get('galaxy.total_klingons', 15)
        self.total_starbases = config.get('galaxy.total_starbases', 4)
        self.star_density = config.get('galaxy.star_density', 0.3)
        self.klingon_density = config.get('galaxy.klingon_density', 0.2)
        
        self.logger.info("Galaxy system initialized")
    
    def generate(self):
        """Generate a new galaxy with random distribution of objects."""
        self.logger.info("Generating new galaxy...")
        
        # Initialize empty quadrants
        for x in range(1, self.GALAXY_SIZE + 1):
            for y in range(1, self.GALAXY_SIZE + 1):
                coords = (x, y)
                self.quadrants[coords] = QuadrantData(
                    coordinates=coords,
                    klingons=0,
                    starbases=0,
                    stars=0,
                    objects={}
                )
        
        # Distribute Klingons
        self._distribute_klingons()
        
        # Distribute starbases
        self._distribute_starbases()
        
        # Distribute stars
        self._distribute_stars()
        
        # Generate detailed quadrant contents
        for quadrant in self.quadrants.values():
            self._generate_quadrant_objects(quadrant)
        
        self.logger.info(f"Galaxy generated with {self.total_klingons} Klingons and {self.total_starbases} starbases")
    
    def _distribute_klingons(self):
        """Distribute Klingons across the galaxy."""
        klingons_placed = 0
        max_per_quadrant = 3
        
        while klingons_placed < self.total_klingons:
            # Choose random quadrant
            x = random.randint(1, self.GALAXY_SIZE)
            y = random.randint(1, self.GALAXY_SIZE)
            quadrant = self.quadrants[(x, y)]
            
            # Add Klingon if quadrant isn't full
            if quadrant.klingons < max_per_quadrant:
                quadrant.klingons += 1
                klingons_placed += 1
    
    def _distribute_starbases(self):
        """Distribute starbases across the galaxy."""
        starbases_placed = 0
        
        while starbases_placed < self.total_starbases:
            # Choose random quadrant
            x = random.randint(1, self.GALAXY_SIZE)
            y = random.randint(1, self.GALAXY_SIZE)
            quadrant = self.quadrants[(x, y)]
            
            # Add starbase if quadrant doesn't have one
            if quadrant.starbases == 0:
                quadrant.starbases = 1
                starbases_placed += 1
    
    def _distribute_stars(self):
        """Distribute stars across the galaxy."""
        for quadrant in self.quadrants.values():
            # Each quadrant gets 1-8 stars based on density
            max_stars = int(self.QUADRANT_SIZE * self.star_density)
            quadrant.stars = random.randint(1, max(1, max_stars))
    
    def _generate_quadrant_objects(self, quadrant: QuadrantData):
        """Generate the specific positions of objects within a quadrant."""
        available_positions = set()
        
        # Generate all possible positions in quadrant
        for x in range(1, self.QUADRANT_SIZE + 1):
            for y in range(1, self.QUADRANT_SIZE + 1):
                available_positions.add((x, y))
        
        # Place Klingons
        for _ in range(quadrant.klingons):
            if available_positions:
                pos = random.choice(list(available_positions))
                available_positions.remove(pos)
                quadrant.objects[pos] = self.KLINGON
        
        # Place starbases
        for _ in range(quadrant.starbases):
            if available_positions:
                pos = random.choice(list(available_positions))
                available_positions.remove(pos)
                quadrant.objects[pos] = self.STARBASE
        
        # Place stars
        for _ in range(quadrant.stars):
            if available_positions:
                pos = random.choice(list(available_positions))
                available_positions.remove(pos)
                quadrant.objects[pos] = self.STAR
    
    def get_quadrant_data(self, coordinates: Tuple[int, int]) -> Dict[Tuple[int, int], str]:
        """Get the object layout for a specific quadrant."""
        if coordinates not in self.quadrants:
            return {}
        
        return self.quadrants[coordinates].objects.copy()
    
    def get_quadrant_summary(self, coordinates: Tuple[int, int]) -> Tuple[int, int, int]:
        """Get summary counts for a quadrant (klingons, starbases, stars)."""
        if coordinates not in self.quadrants:
            return (0, 0, 0)
        
        quadrant = self.quadrants[coordinates]
        return (quadrant.klingons, quadrant.starbases, quadrant.stars)
    
    def format_quadrant_display(self, quadrant_objects: Dict[Tuple[int, int], str], 
                               enterprise_pos: Tuple[int, int]) -> str:
        """Format a quadrant for display with ASCII graphics."""
        display_lines = []
        
        # Header
        display_lines.append("     1   2   3   4   5   6   7   8")
        display_lines.append("   +---+---+---+---+---+---+---+---+")
        
        # Grid rows
        for y in range(1, self.QUADRANT_SIZE + 1):
            row_line = f" {y} |"
            
            for x in range(1, self.QUADRANT_SIZE + 1):
                pos = (x, y)
                
                if pos == enterprise_pos:
                    cell_content = f" {self.ENTERPRISE} "
                elif pos in quadrant_objects:
                    cell_content = f" {quadrant_objects[pos]} "
                else:
                    cell_content = f" {self.EMPTY} "
                
                row_line += cell_content + "|"
            
            display_lines.append(row_line)
            display_lines.append("   +---+---+---+---+---+---+---+---+")
        
        return "\n".join(display_lines)
    
    def get_adjacent_quadrant_data(self, center: Tuple[int, int]) -> Dict[Tuple[int, int], Tuple[int, int, int]]:
        """Get summary data for quadrants adjacent to the center quadrant."""
        adjacent_data = {}
        cx, cy = center
        
        # Check 3x3 grid centered on current position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                qx, qy = cx + dx, cy + dy
                
                if self.is_valid_quadrant((qx, qy)):
                    adjacent_data[(qx, qy)] = self.get_quadrant_summary((qx, qy))
        
        return adjacent_data
    
    def format_long_range_display(self, adjacent_data: Dict[Tuple[int, int], Tuple[int, int, int]], 
                                 center: Tuple[int, int]) -> str:
        """Format long range sensor data for display."""
        display_lines = []
        display_lines.append("LONG RANGE SENSORS:")
        display_lines.append("")
        
        cx, cy = center
        
        # Display 3x3 grid
        for dy in range(-1, 2):
            row_line = ""
            for dx in range(-1, 2):
                qx, qy = cx + dx, cy + dy
                
                if (qx, qy) in adjacent_data:
                    k, b, s = adjacent_data[(qx, qy)]
                    cell = f"{k}{b}{s}"
                else:
                    cell = "***"  # Out of bounds
                
                if dx == 0 and dy == 0:
                    row_line += f"[{cell}] "  # Current quadrant
                else:
                    row_line += f" {cell}  "
            
            display_lines.append(row_line)
        
        display_lines.append("")
        display_lines.append("Format: KBS (Klingons, Bases, Stars)")
        
        return "\n".join(display_lines)
    
    def is_valid_quadrant(self, coordinates: Tuple[int, int]) -> bool:
        """Check if quadrant coordinates are valid."""
        x, y = coordinates
        return 1 <= x <= self.GALAXY_SIZE and 1 <= y <= self.GALAXY_SIZE
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if position within quadrant is valid."""
        x, y = position
        return 1 <= x <= self.QUADRANT_SIZE and 1 <= y <= self.QUADRANT_SIZE
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two quadrants."""
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def calculate_course(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        """Calculate course (in degrees) from one position to another."""
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return 0.0
        
        # Calculate angle in radians, then convert to degrees
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360 range
        if angle_deg < 0:
            angle_deg += 360
        
        return angle_deg
    
    def find_safe_starting_quadrant(self) -> Tuple[int, int]:
        """Find a safe quadrant for the Enterprise to start in."""
        safe_quadrants = []
        
        for coords, quadrant in self.quadrants.items():
            # Prefer quadrants with no Klingons and at least one starbase nearby
            if quadrant.klingons == 0:
                # Check if there's a starbase in this or adjacent quadrants
                has_nearby_starbase = quadrant.starbases > 0
                
                if not has_nearby_starbase:
                    # Check adjacent quadrants for starbases
                    adjacent_data = self.get_adjacent_quadrant_data(coords)
                    for adj_coords, (k, b, s) in adjacent_data.items():
                        if b > 0:
                            has_nearby_starbase = True
                            break
                
                if has_nearby_starbase:
                    safe_quadrants.append(coords)
        
        if safe_quadrants:
            return random.choice(safe_quadrants)
        else:
            # Fallback: find any quadrant with no Klingons
            no_klingon_quadrants = [coords for coords, q in self.quadrants.items() if q.klingons == 0]
            if no_klingon_quadrants:
                return random.choice(no_klingon_quadrants)
            else:
                # Last resort: random quadrant
                return (random.randint(1, self.GALAXY_SIZE), random.randint(1, self.GALAXY_SIZE))
    
    def find_safe_position_in_quadrant(self, quadrant_coords: Tuple[int, int]) -> Tuple[int, int]:
        """Find a safe position within a quadrant for the Enterprise."""
        if quadrant_coords not in self.quadrants:
            return (4, 4)  # Center position as fallback
        
        quadrant = self.quadrants[quadrant_coords]
        occupied_positions = set(quadrant.objects.keys())
        
        # Try to find an empty position
        for _ in range(20):  # Max attempts
            x = random.randint(1, self.QUADRANT_SIZE)
            y = random.randint(1, self.QUADRANT_SIZE)
            pos = (x, y)
            
            if pos not in occupied_positions:
                return pos
        
        # Fallback: return center position (may overlap, but game will handle it)
        return (4, 4)
    
    def remove_object_from_quadrant(self, quadrant_coords: Tuple[int, int], position: Tuple[int, int]):
        """Remove an object from a specific position in a quadrant."""
        if quadrant_coords in self.quadrants:
            quadrant = self.quadrants[quadrant_coords]
            
            if position in quadrant.objects:
                obj_type = quadrant.objects[position]
                del quadrant.objects[position]
                
                # Update counts
                if obj_type == self.KLINGON:
                    quadrant.klingons = max(0, quadrant.klingons - 1)
                elif obj_type == self.STARBASE:
                    quadrant.starbases = max(0, quadrant.starbases - 1)
                elif obj_type == self.STAR:
                    quadrant.stars = max(0, quadrant.stars - 1)
    
    def add_object_to_quadrant(self, quadrant_coords: Tuple[int, int], 
                              position: Tuple[int, int], obj_type: str):
        """Add an object to a specific position in a quadrant."""
        if quadrant_coords in self.quadrants and self.is_valid_position(position):
            quadrant = self.quadrants[quadrant_coords]
            
            # Remove existing object if present
            if position in quadrant.objects:
                self.remove_object_from_quadrant(quadrant_coords, position)
            
            # Add new object
            quadrant.objects[position] = obj_type
            
            # Update counts
            if obj_type == self.KLINGON:
                quadrant.klingons += 1
            elif obj_type == self.STARBASE:
                quadrant.starbases += 1
            elif obj_type == self.STAR:
                quadrant.stars += 1
    
    def move_object_in_quadrant(self, quadrant_coords: Tuple[int, int], 
                               from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        """Move an object from one position to another within a quadrant."""
        if quadrant_coords in self.quadrants:
            quadrant = self.quadrants[quadrant_coords]
            
            if from_pos in quadrant.objects and to_pos not in quadrant.objects:
                obj_type = quadrant.objects[from_pos]
                del quadrant.objects[from_pos]
                quadrant.objects[to_pos] = obj_type
    
    def count_klingons(self) -> int:
        """Count total Klingons in the galaxy."""
        return sum(quadrant.klingons for quadrant in self.quadrants.values())
    
    def count_starbases(self) -> int:
        """Count total starbases in the galaxy."""
        return sum(quadrant.starbases for quadrant in self.quadrants.values())
    
    def get_nearest_starbase(self, from_quadrant: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find the nearest starbase to the given quadrant."""
        starbase_quadrants = []
        
        for coords, quadrant in self.quadrants.items():
            if quadrant.starbases > 0:
                starbase_quadrants.append(coords)
        
        if not starbase_quadrants:
            return None
        
        # Find closest starbase
        min_distance = float('inf')
        nearest_base = None
        
        for base_coords in starbase_quadrants:
            distance = self.calculate_distance(from_quadrant, base_coords)
            if distance < min_distance:
                min_distance = distance
                nearest_base = base_coords
        
        return nearest_base
    
    def get_galaxy_map_display(self, current_quadrant: Tuple[int, int]) -> str:
        """Generate ASCII display of the entire galaxy map."""
        display_lines = []
        display_lines.append("    * * * GALACTIC MAP * * *")
        display_lines.append("")
        display_lines.append("    1   2   3   4   5   6   7   8")
        display_lines.append("  +---+---+---+---+---+---+---+---+")
        
        for y in range(1, self.GALAXY_SIZE + 1):
            row_line = f"{y} |"
            
            for x in range(1, self.GALAXY_SIZE + 1):
                coords = (x, y)
                
                if coords == current_quadrant:
                    cell_content = " E "  # Enterprise location
                elif coords in self.quadrants:
                    k, b, s = self.get_quadrant_summary(coords)
                    if k > 0:
                        cell_content = " K "  # Klingons present
                    elif b > 0:
                        cell_content = " B "  # Starbase present
                    elif s > 0:
                        cell_content = " * "  # Stars only
                    else:
                        cell_content = " . "  # Empty
                else:
                    cell_content = " ? "  # Unknown
                
                row_line += cell_content + "|"
            
            display_lines.append(row_line)
            display_lines.append("  +---+---+---+---+---+---+---+---+")
        
        display_lines.append("")
        display_lines.append("Legend: E=Enterprise, K=Klingon, B=Starbase, *=Star, .=Empty")
        
        return "\n".join(display_lines)
    
    def to_dict(self) -> Dict:
        """Convert galaxy to dictionary for serialization."""
        quadrants_dict = {}
        for coords, quadrant in self.quadrants.items():
            # Convert tuple keys to strings for JSON serialization
            key = f"{coords[0]},{coords[1]}"
            quadrants_dict[key] = quadrant.to_dict()
        
        return {
            "quadrants": quadrants_dict,
            "total_klingons": self.total_klingons,
            "total_starbases": self.total_starbases,
            "star_density": self.star_density,
            "klingon_density": self.klingon_density
        }
    
    def from_dict(self, data: Dict):
        """Load galaxy from dictionary for deserialization."""
        self.total_klingons = data.get("total_klingons", 15)
        self.total_starbases = data.get("total_starbases", 4)
        self.star_density = data.get("star_density", 0.3)
        self.klingon_density = data.get("klingon_density", 0.2)
        
        self.quadrants = {}
        quadrants_data = data.get("quadrants", {})
        
        for key, quadrant_data in quadrants_data.items():
            # Convert string key back to tuple
            coords = tuple(map(int, key.split(',')))
            self.quadrants[coords] = QuadrantData.from_dict(quadrant_data)
