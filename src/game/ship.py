"""
Ship Management System

This module handles the Enterprise's systems, damage, and capabilities.
"""

import random
from typing import Dict, Tuple, Set, Any
from dataclasses import dataclass, asdict
from src.utils.logger import get_logger


@dataclass
class ShipSystems:
    """Ship system damage tracking."""
    warp_engines: float = 0.0
    impulse_engines: float = 0.0
    phasers: float = 0.0
    torpedo_tubes: float = 0.0
    shields: float = 0.0
    sensors: float = 0.0
    computer: float = 0.0
    life_support: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)


class Ship:
    """
    Enterprise ship management system.
    
    Handles all ship systems, damage, resources, and capabilities.
    """
    
    def __init__(self, config):
        """Initialize the ship."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # Ship specifications
        self.max_energy = config.get('ship.max_energy', 3000)
        self.max_shields = config.get('ship.max_shields', 1500)
        self.max_torpedoes = config.get('ship.max_torpedoes', 10)
        
        # Current status
        self.energy = self.max_energy
        self.shields = self.max_shields
        self.torpedoes = self.max_torpedoes
        
        # Position tracking
        self.current_quadrant: Tuple[int, int] = (1, 1)
        self.quadrant_position: Tuple[int, int] = (4, 4)
        self.visited_quadrants: Set[Tuple[int, int]] = set()
        
        # System damage (0.0 = no damage, 1.0 = completely destroyed)
        self.systems = ShipSystems()
        
        # Ship condition
        self.docked = False
        self.destroyed = False
        
        self.logger.info("Ship systems initialized")
    
    def reset_to_full_strength(self):
        """Reset ship to full operational status."""
        self.energy = self.max_energy
        self.shields = self.max_shields
        self.torpedoes = self.max_torpedoes
        self.systems = ShipSystems()
        self.docked = False
        self.destroyed = False
        self.logger.info("Ship reset to full strength")
    
    def take_damage(self, damage_amount: int) -> int:
        """
        Apply damage to the ship.
        
        Args:
            damage_amount: Amount of damage to apply
            
        Returns:
            Actual damage taken after shields
        """
        if damage_amount <= 0:
            return 0
        
        # Shields absorb damage first
        if self.shields > 0:
            shield_absorption = min(self.shields, damage_amount)
            self.shields -= shield_absorption
            damage_amount -= shield_absorption
            
            self.logger.debug(f"Shields absorbed {shield_absorption} damage, {self.shields} remaining")
        
        # Remaining damage affects ship systems and energy
        if damage_amount > 0:
            # Energy takes damage
            energy_damage = min(self.energy, damage_amount)
            self.energy -= energy_damage
            
            # Random system damage
            self._apply_system_damage(damage_amount)
            
            self.logger.info(f"Ship took {damage_amount} damage, energy now {self.energy}")
        
        # Check if ship is destroyed
        if self.energy <= 0:
            self.destroyed = True
            self.logger.warning("Ship destroyed!")
        
        return damage_amount
    
    def _apply_system_damage(self, damage_amount: int):
        """Apply random system damage based on damage amount."""
        # Probability of system damage increases with damage amount
        damage_chance = min(0.8, damage_amount / 100.0)
        
        if random.random() < damage_chance:
            # Choose random system to damage
            systems = [
                'warp_engines', 'impulse_engines', 'phasers', 'torpedo_tubes',
                'shields', 'sensors', 'computer', 'life_support'
            ]
            
            damaged_system = random.choice(systems)
            damage_severity = random.uniform(0.1, 0.5)
            
            current_damage = getattr(self.systems, damaged_system)
            new_damage = min(1.0, current_damage + damage_severity)
            setattr(self.systems, damaged_system, new_damage)
            
            self.logger.info(f"{damaged_system} damaged: {new_damage:.2f}")
    
    def repair_system(self, system_name: str, repair_amount: float = 0.1):
        """Repair a specific system."""
        if hasattr(self.systems, system_name):
            current_damage = getattr(self.systems, system_name)
            new_damage = max(0.0, current_damage - repair_amount)
            setattr(self.systems, system_name, new_damage)
            
            self.logger.info(f"Repaired {system_name}: {new_damage:.2f} damage remaining")
    
    def repair_all_damage(self):
        """Repair all system damage (used when docking)."""
        self.systems = ShipSystems()
        self.logger.info("All systems repaired")
    
    def has_damage(self) -> bool:
        """Check if ship has any system damage."""
        return any(damage > 0 for damage in self.systems.to_dict().values())
    
    def is_destroyed(self) -> bool:
        """Check if ship is destroyed."""
        return self.destroyed or self.energy <= 0
    
    def get_system_efficiency(self, system_name: str) -> float:
        """Get efficiency of a system (1.0 = perfect, 0.0 = destroyed)."""
        if hasattr(self.systems, system_name):
            damage = getattr(self.systems, system_name)
            return max(0.0, 1.0 - damage)
        return 1.0
    
    def can_use_warp(self) -> bool:
        """Check if warp engines are functional."""
        return self.get_system_efficiency('warp_engines') > 0.1 and self.energy > 100
    
    def can_use_phasers(self) -> bool:
        """Check if phasers are functional."""
        return self.get_system_efficiency('phasers') > 0.1 and self.energy > 50
    
    def can_use_torpedoes(self) -> bool:
        """Check if torpedo tubes are functional."""
        return (self.get_system_efficiency('torpedo_tubes') > 0.1 and 
                self.torpedoes > 0)
    
    def can_use_sensors(self) -> bool:
        """Check if sensors are functional."""
        return self.get_system_efficiency('sensors') > 0.1
    
    def get_phaser_efficiency(self) -> float:
        """Get phaser system efficiency."""
        return self.get_system_efficiency('phasers')
    
    def get_torpedo_efficiency(self) -> float:
        """Get torpedo system efficiency."""
        return self.get_system_efficiency('torpedo_tubes')
    
    def get_sensor_efficiency(self) -> float:
        """Get sensor system efficiency."""
        return self.get_system_efficiency('sensors')
    
    def get_damage_report(self) -> Dict[str, Any]:
        """Get comprehensive damage report."""
        systems_status = {}
        
        for system_name, damage in self.systems.to_dict().items():
            if damage > 0:
                if damage < 0.2:
                    status = "Minor damage"
                elif damage < 0.5:
                    status = "Moderate damage"
                elif damage < 0.8:
                    status = "Major damage"
                else:
                    status = "Critical damage"
                
                systems_status[system_name.replace('_', ' ').title()] = {
                    'damage_level': damage,
                    'status': status,
                    'efficiency': self.get_system_efficiency(system_name)
                }
            else:
                systems_status[system_name.replace('_', ' ').title()] = {
                    'damage_level': 0.0,
                    'status': "Operational",
                    'efficiency': 1.0
                }
        
        return {
            'systems': systems_status,
            'overall_condition': self._get_overall_condition(),
            'repair_priority': self._get_repair_priority()
        }
    
    def _get_overall_condition(self) -> str:
        """Get overall ship condition."""
        if self.destroyed:
            return "DESTROYED"
        
        total_damage = sum(self.systems.to_dict().values())
        avg_damage = total_damage / 8  # 8 systems
        
        if avg_damage < 0.1:
            return "EXCELLENT"
        elif avg_damage < 0.3:
            return "GOOD"
        elif avg_damage < 0.6:
            return "FAIR"
        elif avg_damage < 0.8:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _get_repair_priority(self) -> list:
        """Get list of systems in order of repair priority."""
        systems_damage = self.systems.to_dict()
        
        # Priority order (most critical first)
        priority_order = [
            'life_support', 'warp_engines', 'shields', 'phasers',
            'torpedo_tubes', 'sensors', 'impulse_engines', 'computer'
        ]
        
        repair_list = []
        for system in priority_order:
            if systems_damage[system] > 0:
                repair_list.append({
                    'system': system.replace('_', ' ').title(),
                    'damage': systems_damage[system],
                    'priority': 'CRITICAL' if systems_damage[system] > 0.8 else
                               'HIGH' if systems_damage[system] > 0.5 else
                               'MEDIUM' if systems_damage[system] > 0.2 else 'LOW'
                })
        
        return repair_list
    
    def dock_with_starbase(self):
        """Dock with starbase and restore ship."""
        self.docked = True
        self.energy = self.max_energy
        self.shields = self.max_shields
        self.torpedoes = self.max_torpedoes
        self.repair_all_damage()
        self.logger.info("Docked with starbase - ship fully restored")
    
    def undock(self):
        """Undock from starbase."""
        self.docked = False
        self.logger.info("Undocked from starbase")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of ship status."""
        return {
            'energy': self.energy,
            'max_energy': self.max_energy,
            'energy_percent': (self.energy / self.max_energy) * 100,
            'shields': self.shields,
            'max_shields': self.max_shields,
            'shield_percent': (self.shields / self.max_shields) * 100,
            'torpedoes': self.torpedoes,
            'max_torpedoes': self.max_torpedoes,
            'current_quadrant': self.current_quadrant,
            'quadrant_position': self.quadrant_position,
            'docked': self.docked,
            'destroyed': self.destroyed,
            'has_damage': self.has_damage(),
            'overall_condition': self._get_overall_condition(),
            'quadrants_visited': len(self.visited_quadrants)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ship to dictionary for serialization."""
        return {
            'energy': self.energy,
            'shields': self.shields,
            'torpedoes': self.torpedoes,
            'current_quadrant': self.current_quadrant,
            'quadrant_position': self.quadrant_position,
            'visited_quadrants': list(self.visited_quadrants),
            'systems': self.systems.to_dict(),
            'docked': self.docked,
            'destroyed': self.destroyed,
            'max_energy': self.max_energy,
            'max_shields': self.max_shields,
            'max_torpedoes': self.max_torpedoes
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load ship from dictionary for deserialization."""
        self.energy = data.get('energy', self.max_energy)
        self.shields = data.get('shields', self.max_shields)
        self.torpedoes = data.get('torpedoes', self.max_torpedoes)
        self.current_quadrant = tuple(data.get('current_quadrant', (1, 1)))
        self.quadrant_position = tuple(data.get('quadrant_position', (4, 4)))
        self.visited_quadrants = set(tuple(q) for q in data.get('visited_quadrants', []))
        self.docked = data.get('docked', False)
        self.destroyed = data.get('destroyed', False)
        
        # Load system damage
        systems_data = data.get('systems', {})
        for system_name, damage in systems_data.items():
            if hasattr(self.systems, system_name):
                setattr(self.systems, system_name, damage)
        
        # Update max values if they were saved
        self.max_energy = data.get('max_energy', self.max_energy)
        self.max_shields = data.get('max_shields', self.max_shields)
        self.max_torpedoes = data.get('max_torpedoes', self.max_torpedoes)
