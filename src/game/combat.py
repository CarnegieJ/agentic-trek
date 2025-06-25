"""
Combat System

This module handles all combat mechanics including weapon systems,
damage calculation, and battle resolution.
"""

import random
import math
from typing import Dict, List, Tuple, Any
from ..utils.logger import get_logger


class CombatSystem:
    """
    Combat system for handling battles between ships.
    
    Manages weapon systems, damage calculation, hit probability,
    and battle resolution with realistic physics simulation.
    """
    
    def __init__(self, config):
        """Initialize the combat system."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # Combat configuration
        self.phaser_max_range = config.get('combat.phaser_max_range', 8.0)
        self.torpedo_max_range = config.get('combat.torpedo_max_range', 10.0)
        self.phaser_accuracy_base = config.get('combat.phaser_accuracy_base', 0.8)
        self.torpedo_accuracy_base = config.get('combat.torpedo_accuracy_base', 0.6)
        self.damage_variance = config.get('combat.damage_variance', 0.2)
        self.critical_hit_chance = config.get('combat.critical_hit_chance', 0.1)
        self.critical_hit_multiplier = config.get('combat.critical_hit_multiplier', 2.0)
        
        self.logger.info("Combat system initialized")
    
    def execute_phaser_attack(self, attacking_ship, enemy_positions: List[Tuple[int, int]], 
                             energy_amount: int, quadrant_data: Dict[Tuple[int, int], str]) -> Dict[str, Any]:
        """
        Execute a phaser attack against enemies.
        
        Args:
            attacking_ship: Ship object performing the attack
            enemy_positions: List of enemy positions in quadrant
            energy_amount: Energy allocated to phaser attack
            quadrant_data: Current quadrant object layout
            
        Returns:
            Dictionary containing attack results
        """
        if not enemy_positions:
            return {
                "success": False,
                "message": "No targets in range",
                "events": []
            }
        
        # Check if phasers are functional
        phaser_efficiency = attacking_ship.get_phaser_efficiency()
        if phaser_efficiency <= 0.1:
            return {
                "success": False,
                "message": "Phasers are too damaged to fire",
                "events": []
            }
        
        results = {
            "success": True,
            "message": "",
            "events": [],
            "destroyed_enemies": [],
            "total_damage": 0
        }
        
        # Distribute energy among targets
        energy_per_target = energy_amount // len(enemy_positions)
        remaining_energy = energy_amount % len(enemy_positions)
        
        ship_pos = attacking_ship.quadrant_position
        
        for i, enemy_pos in enumerate(enemy_positions):
            # Calculate energy for this target
            target_energy = energy_per_target
            if i == 0:  # Give remainder to first target
                target_energy += remaining_energy
            
            if target_energy <= 0:
                continue
            
            # Calculate distance and hit probability
            distance = self._calculate_distance(ship_pos, enemy_pos)
            hit_probability = self._calculate_phaser_hit_probability(
                distance, target_energy, phaser_efficiency
            )
            
            # Determine if hit
            if random.random() <= hit_probability:
                # Calculate damage
                damage = self._calculate_phaser_damage(target_energy, distance, phaser_efficiency)
                
                # Check for critical hit
                if random.random() <= self.critical_hit_chance:
                    damage = int(damage * self.critical_hit_multiplier)
                    results["events"].append(f"Critical hit on enemy at {enemy_pos}!")
                
                results["total_damage"] += damage
                results["events"].append(f"Phaser hit enemy at {enemy_pos} for {damage} damage")
                
                # Determine if enemy is destroyed (simplified)
                if damage >= 50:  # Threshold for destruction
                    results["destroyed_enemies"].append(enemy_pos)
                    results["events"].append(f"Enemy at {enemy_pos} destroyed!")
            else:
                results["events"].append(f"Phaser missed enemy at {enemy_pos}")
        
        # Generate summary message
        hits = len([e for e in results["events"] if "hit" in e and "missed" not in e])
        misses = len([e for e in results["events"] if "missed" in e])
        destroyed = len(results["destroyed_enemies"])
        
        results["message"] = f"Phasers fired: {hits} hits, {misses} misses, {destroyed} destroyed"
        
        self.logger.info(f"Phaser attack: {energy_amount} energy, {hits} hits, {destroyed} destroyed")
        
        return results
    
    def execute_torpedo_attack(self, attacking_ship, course: float, spread: int, 
                              quadrant_data: Dict[Tuple[int, int], str]) -> Dict[str, Any]:
        """
        Execute a photon torpedo attack.
        
        Args:
            attacking_ship: Ship object performing the attack
            course: Firing course in degrees (0-360)
            spread: Torpedo spread pattern (1-10)
            quadrant_data: Current quadrant object layout
            
        Returns:
            Dictionary containing attack results
        """
        # Check if torpedo tubes are functional
        torpedo_efficiency = attacking_ship.get_torpedo_efficiency()
        if torpedo_efficiency <= 0.1:
            return {
                "success": False,
                "message": "Torpedo tubes are too damaged to fire",
                "events": []
            }
        
        results = {
            "success": True,
            "message": "",
            "events": [],
            "destroyed_enemies": [],
            "total_damage": 0
        }
        
        ship_pos = attacking_ship.quadrant_position
        
        # Calculate torpedo trajectory
        trajectory_points = self._calculate_torpedo_trajectory(ship_pos, course, spread)
        
        # Check for hits along trajectory
        enemies_hit = []
        for point in trajectory_points:
            if point in quadrant_data and quadrant_data[point] == 'K':
                if point not in enemies_hit:
                    enemies_hit.append(point)
        
        if not enemies_hit:
            results["events"].append("Torpedo missed all targets")
            results["message"] = "Torpedo missed"
            return results
        
        # Calculate damage for each hit
        for enemy_pos in enemies_hit:
            distance = self._calculate_distance(ship_pos, enemy_pos)
            hit_probability = self._calculate_torpedo_hit_probability(
                distance, spread, torpedo_efficiency
            )
            
            if random.random() <= hit_probability:
                damage = self._calculate_torpedo_damage(distance, torpedo_efficiency)
                
                # Check for critical hit
                if random.random() <= self.critical_hit_chance:
                    damage = int(damage * self.critical_hit_multiplier)
                    results["events"].append(f"Critical torpedo hit on enemy at {enemy_pos}!")
                
                results["total_damage"] += damage
                results["events"].append(f"Torpedo hit enemy at {enemy_pos} for {damage} damage")
                
                # Determine if enemy is destroyed
                if damage >= 75:  # Torpedoes are more powerful
                    results["destroyed_enemies"].append(enemy_pos)
                    results["events"].append(f"Enemy at {enemy_pos} destroyed by torpedo!")
            else:
                results["events"].append(f"Torpedo grazed enemy at {enemy_pos}")
        
        # Generate summary message
        hits = len([e for e in results["events"] if "hit" in e and "grazed" not in e])
        destroyed = len(results["destroyed_enemies"])
        
        results["message"] = f"Torpedo fired: {hits} hits, {destroyed} destroyed"
        
        self.logger.info(f"Torpedo attack: course {course}, {hits} hits, {destroyed} destroyed")
        
        return results
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two positions."""
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def _calculate_phaser_hit_probability(self, distance: float, energy: int, 
                                        efficiency: float) -> float:
        """Calculate probability of phaser hit."""
        # Base accuracy modified by distance, energy, and system efficiency
        base_accuracy = self.phaser_accuracy_base
        
        # Distance penalty
        distance_modifier = max(0.1, 1.0 - (distance / self.phaser_max_range) * 0.5)
        
        # Energy bonus (more energy = better targeting)
        energy_modifier = min(1.2, 1.0 + (energy / 1000.0) * 0.2)
        
        # System efficiency
        efficiency_modifier = efficiency
        
        hit_probability = base_accuracy * distance_modifier * energy_modifier * efficiency_modifier
        
        return max(0.05, min(0.95, hit_probability))
    
    def _calculate_torpedo_hit_probability(self, distance: float, spread: int, 
                                         efficiency: float) -> float:
        """Calculate probability of torpedo hit."""
        base_accuracy = self.torpedo_accuracy_base
        
        # Distance penalty
        distance_modifier = max(0.2, 1.0 - (distance / self.torpedo_max_range) * 0.3)
        
        # Spread bonus (wider spread = better hit chance but less damage)
        spread_modifier = min(1.3, 1.0 + (spread / 10.0) * 0.3)
        
        # System efficiency
        efficiency_modifier = efficiency
        
        hit_probability = base_accuracy * distance_modifier * spread_modifier * efficiency_modifier
        
        return max(0.1, min(0.9, hit_probability))
    
    def _calculate_phaser_damage(self, energy: int, distance: float, efficiency: float) -> int:
        """Calculate phaser damage."""
        # Base damage from energy
        base_damage = energy // 20  # 1 damage per 20 energy units
        
        # Distance attenuation
        distance_modifier = max(0.3, 1.0 - (distance / self.phaser_max_range) * 0.4)
        
        # System efficiency
        efficiency_modifier = efficiency
        
        # Random variance
        variance = random.uniform(1.0 - self.damage_variance, 1.0 + self.damage_variance)
        
        damage = int(base_damage * distance_modifier * efficiency_modifier * variance)
        
        return max(1, damage)
    
    def _calculate_torpedo_damage(self, distance: float, efficiency: float) -> int:
        """Calculate torpedo damage."""
        # Base torpedo damage
        base_damage = 100
        
        # Distance attenuation (less than phasers)
        distance_modifier = max(0.5, 1.0 - (distance / self.torpedo_max_range) * 0.2)
        
        # System efficiency
        efficiency_modifier = efficiency
        
        # Random variance
        variance = random.uniform(1.0 - self.damage_variance, 1.0 + self.damage_variance)
        
        damage = int(base_damage * distance_modifier * efficiency_modifier * variance)
        
        return max(10, damage)
    
    def _calculate_torpedo_trajectory(self, start_pos: Tuple[int, int], course: float, 
                                    spread: int) -> List[Tuple[int, int]]:
        """Calculate torpedo trajectory points."""
        x, y = start_pos
        trajectory = []
        
        # Convert course to radians
        course_rad = math.radians(course)
        
        # Calculate trajectory points
        max_range = int(self.torpedo_max_range)
        for distance in range(1, max_range + 1):
            # Base trajectory
            base_x = x + distance * math.cos(course_rad)
            base_y = y + distance * math.sin(course_rad)
            
            # Add spread effect
            spread_radius = spread * 0.1 * distance  # Spread increases with distance
            
            for spread_offset in range(-spread//2, spread//2 + 1):
                spread_angle = course_rad + spread_offset * 0.1
                spread_x = int(base_x + spread_radius * math.cos(spread_angle))
                spread_y = int(base_y + spread_radius * math.sin(spread_angle))
                
                # Check bounds
                if 1 <= spread_x <= 8 and 1 <= spread_y <= 8:
                    pos = (spread_x, spread_y)
                    if pos not in trajectory:
                        trajectory.append(pos)
        
        return trajectory
    
    def calculate_optimal_phaser_energy(self, target_distance: float, 
                                       available_energy: int) -> int:
        """Calculate optimal phaser energy for a target at given distance."""
        # Base energy needed for effective damage at this distance
        base_energy = int(200 * (1 + target_distance / 4))
        
        # Don't exceed available energy
        optimal_energy = min(base_energy, available_energy)
        
        # Minimum effective energy
        return max(100, optimal_energy)
    
    def calculate_optimal_torpedo_course(self, ship_pos: Tuple[int, int], 
                                       target_pos: Tuple[int, int]) -> float:
        """Calculate optimal torpedo course to hit a target."""
        x1, y1 = ship_pos
        x2, y2 = target_pos
        
        # Calculate angle in degrees
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return 0.0
        
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to 0-360 range
        if angle_deg < 0:
            angle_deg += 360
        
        return angle_deg
