"""
Klingon AI System

This module implements intelligent AI behavior for Klingon ships, including
combat tactics, movement strategies, and adaptive learning capabilities.
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..utils.logger import get_logger


class KlingonPersonality(Enum):
    """Different Klingon AI personality types."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    TACTICAL = "tactical"
    BERSERKER = "berserker"
    COMMANDER = "commander"


@dataclass
class KlingonState:
    """State information for a Klingon ship."""
    position: Tuple[int, int]
    health: int
    max_health: int
    energy: int
    personality: KlingonPersonality
    aggression_level: float  # 0.0 to 1.0
    fear_level: float       # 0.0 to 1.0
    last_action: str
    turns_since_damage: int
    player_hit_accuracy: float  # Learned player accuracy
    
    def is_damaged(self) -> bool:
        """Check if Klingon is damaged."""
        return self.health < self.max_health
    
    def damage_percentage(self) -> float:
        """Get damage as percentage."""
        return 1.0 - (self.health / self.max_health)


class KlingonAI:
    """
    Advanced AI system for Klingon ships with adaptive behavior.
    
    Features:
    - Multiple personality types with different combat styles
    - Adaptive learning based on player behavior
    - Tactical decision making based on battlefield conditions
    - Dynamic difficulty adjustment
    """
    
    def __init__(self, config):
        """Initialize the Klingon AI system."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # AI configuration
        self.base_aggression = config.get('ai.klingon.base_aggression', 0.7)
        self.learning_rate = config.get('ai.klingon.learning_rate', 0.1)
        self.tactical_awareness = config.get('ai.klingon.tactical_awareness', 0.8)
        self.adaptation_enabled = config.get('ai.klingon.adaptation_enabled', True)
        
        # Klingon state tracking
        self.klingon_states: Dict[Tuple[int, int], KlingonState] = {}
        
        # Player behavior analysis
        self.player_behavior = {
            'preferred_weapons': {'phasers': 0, 'torpedoes': 0},
            'combat_range_preference': 0.0,  # 0=close, 1=far
            'aggression_level': 0.5,
            'shield_usage_pattern': 0.5,
            'retreat_threshold': 0.3,
            'total_encounters': 0
        }
        
        # Combat effectiveness tracking
        self.combat_stats = {
            'total_shots_fired': 0,
            'total_hits': 0,
            'total_damage_dealt': 0,
            'total_damage_received': 0,
            'ships_destroyed': 0,
            'encounters_won': 0,
            'encounters_lost': 0
        }
        
        self.logger.info("Klingon AI system initialized")
    
    def decide_action(self, klingon_pos: Tuple[int, int], player_pos: Tuple[int, int], 
                     player_ship, quadrant_data: Dict[Tuple[int, int], str]) -> Dict[str, Any]:
        """
        Decide the best action for a Klingon ship.
        
        Args:
            klingon_pos: Position of the Klingon ship
            player_pos: Position of the player's ship
            player_ship: Player ship object with stats
            quadrant_data: Current quadrant object layout
            
        Returns:
            Dictionary containing the decided action and parameters
        """
        # Initialize or update Klingon state
        if klingon_pos not in self.klingon_states:
            self._initialize_klingon_state(klingon_pos)
        
        klingon = self.klingon_states[klingon_pos]
        
        # Analyze tactical situation
        tactical_analysis = self._analyze_tactical_situation(
            klingon_pos, player_pos, player_ship, quadrant_data
        )
        
        # Update fear and aggression based on situation
        self._update_emotional_state(klingon, tactical_analysis, player_ship)
        
        # Decide action based on personality and situation
        action = self._choose_action(klingon, tactical_analysis, player_ship)
        
        # Learn from player behavior
        if self.adaptation_enabled:
            self._update_player_behavior_model(player_ship, tactical_analysis)
        
        # Update Klingon state
        klingon.last_action = action['action']
        klingon.turns_since_damage += 1
        
        self.logger.debug(f"Klingon at {klingon_pos} decided: {action['action']}")
        
        return action
    
    def _initialize_klingon_state(self, position: Tuple[int, int]):
        """Initialize state for a new Klingon ship."""
        # Assign random personality
        personality = random.choice(list(KlingonPersonality))
        
        # Set initial stats based on difficulty and personality
        base_health = self.config.get('ai.klingon.base_health', 100)
        base_energy = self.config.get('ai.klingon.base_energy', 200)
        
        # Personality modifiers
        health_modifier = 1.0
        aggression_modifier = self.base_aggression
        
        if personality == KlingonPersonality.BERSERKER:
            health_modifier = 0.8
            aggression_modifier = 0.9
        elif personality == KlingonPersonality.DEFENSIVE:
            health_modifier = 1.2
            aggression_modifier = 0.4
        elif personality == KlingonPersonality.COMMANDER:
            health_modifier = 1.1
            aggression_modifier = 0.6
        elif personality == KlingonPersonality.TACTICAL:
            health_modifier = 1.0
            aggression_modifier = 0.7
        
        health = int(base_health * health_modifier)
        
        self.klingon_states[position] = KlingonState(
            position=position,
            health=health,
            max_health=health,
            energy=base_energy,
            personality=personality,
            aggression_level=aggression_modifier,
            fear_level=0.0,
            last_action="spawn",
            turns_since_damage=0,
            player_hit_accuracy=0.5
        )
        
        self.logger.debug(f"Initialized {personality.value} Klingon at {position}")
    
    def _analyze_tactical_situation(self, klingon_pos: Tuple[int, int], 
                                  player_pos: Tuple[int, int], player_ship,
                                  quadrant_data: Dict[Tuple[int, int], str]) -> Dict[str, Any]:
        """Analyze the current tactical situation."""
        # Calculate distance to player
        distance = self._calculate_distance(klingon_pos, player_pos)
        
        # Count allies and enemies
        klingon_count = sum(1 for obj in quadrant_data.values() if obj == 'K')
        starbase_count = sum(1 for obj in quadrant_data.values() if obj == 'B')
        
        # Analyze player threat level
        player_threat = self._assess_player_threat(player_ship)
        
        # Check for tactical advantages
        has_cover = self._check_for_cover(klingon_pos, player_pos, quadrant_data)
        flanking_opportunity = self._check_flanking_opportunity(klingon_pos, player_pos, quadrant_data)
        
        # Analyze escape routes
        escape_routes = self._find_escape_routes(klingon_pos, player_pos, quadrant_data)
        
        return {
            'distance_to_player': distance,
            'klingon_allies': klingon_count - 1,  # Exclude self
            'enemy_starbases': starbase_count,
            'player_threat_level': player_threat,
            'has_cover': has_cover,
            'flanking_opportunity': flanking_opportunity,
            'escape_routes': len(escape_routes),
            'optimal_range': self._calculate_optimal_combat_range(player_ship),
            'player_shield_status': player_ship.shields / player_ship.max_shields if player_ship.max_shields > 0 else 0
        }
    
    def _update_emotional_state(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], player_ship):
        """Update Klingon's emotional state based on situation."""
        # Base fear on damage and threat level
        damage_fear = klingon.damage_percentage() * 0.5
        threat_fear = tactical_analysis['player_threat_level'] * 0.3
        outnumbered_fear = 0.2 if tactical_analysis['klingon_allies'] == 0 else 0.0
        
        klingon.fear_level = min(1.0, damage_fear + threat_fear + outnumbered_fear)
        
        # Adjust aggression based on personality and situation
        base_aggression = klingon.aggression_level
        
        # Berserkers get more aggressive when damaged
        if klingon.personality == KlingonPersonality.BERSERKER and klingon.is_damaged():
            base_aggression += 0.2
        
        # Commanders consider tactical situation
        if klingon.personality == KlingonPersonality.COMMANDER:
            if tactical_analysis['klingon_allies'] > 0:
                base_aggression += 0.1
            if tactical_analysis['flanking_opportunity']:
                base_aggression += 0.15
        
        # Fear reduces aggression
        klingon.aggression_level = max(0.1, base_aggression - klingon.fear_level * 0.3)
    
    def _choose_action(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], 
                      player_ship) -> Dict[str, Any]:
        """Choose the best action based on AI analysis."""
        distance = tactical_analysis['distance_to_player']
        
        # Decision tree based on personality and situation
        if klingon.personality == KlingonPersonality.DEFENSIVE:
            return self._defensive_strategy(klingon, tactical_analysis, player_ship)
        elif klingon.personality == KlingonPersonality.BERSERKER:
            return self._berserker_strategy(klingon, tactical_analysis, player_ship)
        elif klingon.personality == KlingonPersonality.COMMANDER:
            return self._commander_strategy(klingon, tactical_analysis, player_ship)
        elif klingon.personality == KlingonPersonality.TACTICAL:
            return self._tactical_strategy(klingon, tactical_analysis, player_ship)
        else:  # AGGRESSIVE
            return self._aggressive_strategy(klingon, tactical_analysis, player_ship)
    
    def _defensive_strategy(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], 
                          player_ship) -> Dict[str, Any]:
        """Implement defensive combat strategy."""
        distance = tactical_analysis['distance_to_player']
        
        # Retreat if heavily damaged
        if klingon.damage_percentage() > 0.6:
            return self._retreat_action(klingon, tactical_analysis)
        
        # Maintain distance and use long-range attacks
        if distance < 3:
            return self._move_away_action(klingon, tactical_analysis)
        elif distance > 5:
            return self._move_closer_action(klingon, tactical_analysis)
        else:
            # Optimal range - attack with calculated risk
            attack_power = int(klingon.energy * 0.3)  # Conservative attack
            return {
                'action': 'attack',
                'weapon': 'phaser',
                'power': attack_power,
                'damage': self._calculate_attack_damage(attack_power, distance)
            }
    
    def _berserker_strategy(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], 
                          player_ship) -> Dict[str, Any]:
        """Implement berserker combat strategy."""
        # Always attack with maximum power
        attack_power = int(klingon.energy * 0.8)  # High power attack
        distance = tactical_analysis['distance_to_player']
        
        # Move closer if too far
        if distance > 2:
            return self._move_closer_action(klingon, tactical_analysis)
        
        return {
            'action': 'attack',
            'weapon': 'phaser',
            'power': attack_power,
            'damage': self._calculate_attack_damage(attack_power, distance)
        }
    
    def _commander_strategy(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], 
                          player_ship) -> Dict[str, Any]:
        """Implement commander combat strategy."""
        # Coordinate with allies and use tactical positioning
        distance = tactical_analysis['distance_to_player']
        
        # Use flanking if available
        if tactical_analysis['flanking_opportunity']:
            return self._flanking_attack(klingon, tactical_analysis)
        
        # Support allies or attack based on situation
        if tactical_analysis['klingon_allies'] > 0:
            # Coordinate attack
            attack_power = int(klingon.energy * 0.6)
            return {
                'action': 'attack',
                'weapon': 'phaser',
                'power': attack_power,
                'damage': self._calculate_attack_damage(attack_power, distance),
                'coordinated': True
            }
        else:
            # Fight tactically
            return self._tactical_strategy(klingon, tactical_analysis, player_ship)
    
    def _tactical_strategy(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], 
                         player_ship) -> Dict[str, Any]:
        """Implement tactical combat strategy."""
        distance = tactical_analysis['distance_to_player']
        optimal_range = tactical_analysis['optimal_range']
        
        # Position for optimal combat range
        if abs(distance - optimal_range) > 1:
            if distance < optimal_range:
                return self._move_away_action(klingon, tactical_analysis)
            else:
                return self._move_closer_action(klingon, tactical_analysis)
        
        # Attack with calculated power based on situation
        threat_multiplier = 1.0 + tactical_analysis['player_threat_level'] * 0.5
        base_power = int(klingon.energy * 0.5 * threat_multiplier)
        
        return {
            'action': 'attack',
            'weapon': 'phaser',
            'power': base_power,
            'damage': self._calculate_attack_damage(base_power, distance)
        }
    
    def _aggressive_strategy(self, klingon: KlingonState, tactical_analysis: Dict[str, Any], 
                           player_ship) -> Dict[str, Any]:
        """Implement aggressive combat strategy."""
        distance = tactical_analysis['distance_to_player']
        
        # Close distance and attack
        if distance > 3:
            return self._move_closer_action(klingon, tactical_analysis)
        
        # High-power attack
        attack_power = int(klingon.energy * 0.7)
        return {
            'action': 'attack',
            'weapon': 'phaser',
            'power': attack_power,
            'damage': self._calculate_attack_damage(attack_power, distance)
        }
    
    def _retreat_action(self, klingon: KlingonState, tactical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate retreat action."""
        return {
            'action': 'retreat',
            'direction': self._find_best_retreat_direction(klingon, tactical_analysis),
            'message': f"Klingon at {klingon.position} retreats!"
        }
    
    def _move_away_action(self, klingon: KlingonState, tactical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate move away action."""
        new_position = self._calculate_move_away_position(klingon.position, tactical_analysis)
        return {
            'action': 'move',
            'new_position': new_position,
            'message': f"Klingon moves to maintain distance"
        }
    
    def _move_closer_action(self, klingon: KlingonState, tactical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate move closer action."""
        new_position = self._calculate_move_closer_position(klingon.position, tactical_analysis)
        return {
            'action': 'move',
            'new_position': new_position,
            'message': f"Klingon closes distance"
        }
    
    def _flanking_attack(self, klingon: KlingonState, tactical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate flanking attack action."""
        attack_power = int(klingon.energy * 0.6)
        distance = tactical_analysis['distance_to_player']
        
        # Flanking attacks get bonus damage
        base_damage = self._calculate_attack_damage(attack_power, distance)
        flanking_bonus = int(base_damage * 0.25)
        
        return {
            'action': 'attack',
            'weapon': 'phaser',
            'power': attack_power,
            'damage': base_damage + flanking_bonus,
            'flanking': True,
            'message': "Klingon executes flanking attack!"
        }
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two positions."""
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def _assess_player_threat(self, player_ship) -> float:
        """Assess how threatening the player is (0.0 to 1.0)."""
        # Base threat on energy, shields, and weapons
        energy_threat = min(1.0, player_ship.energy / 3000.0)
        shield_threat = min(1.0, player_ship.shields / 1500.0)
        weapon_threat = min(1.0, player_ship.torpedoes / 10.0)
        
        # Weight factors
        total_threat = (energy_threat * 0.4 + shield_threat * 0.3 + weapon_threat * 0.3)
        
        # Adjust based on learned player behavior
        if self.player_behavior['total_encounters'] > 5:
            aggression_modifier = self.player_behavior['aggression_level']
            total_threat *= (0.5 + aggression_modifier * 0.5)
        
        return min(1.0, total_threat)
    
    def _check_for_cover(self, klingon_pos: Tuple[int, int], player_pos: Tuple[int, int], 
                        quadrant_data: Dict[Tuple[int, int], str]) -> bool:
        """Check if Klingon has cover from stars or other objects."""
        # Simple line-of-sight check
        x1, y1 = klingon_pos
        x2, y2 = player_pos
        
        # Check if there are stars between Klingon and player
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        
        if steps <= 1:
            return False
        
        for i in range(1, steps):
            check_x = x1 + int(dx * i / steps)
            check_y = y1 + int(dy * i / steps)
            check_pos = (check_x, check_y)
            
            if check_pos in quadrant_data and quadrant_data[check_pos] == '*':
                return True
        
        return False
    
    def _check_flanking_opportunity(self, klingon_pos: Tuple[int, int], player_pos: Tuple[int, int], 
                                  quadrant_data: Dict[Tuple[int, int], str]) -> bool:
        """Check if there's an opportunity for flanking attack."""
        # Look for other Klingons that could coordinate
        klingon_positions = [pos for pos, obj in quadrant_data.items() if obj == 'K' and pos != klingon_pos]
        
        if not klingon_positions:
            return False
        
        # Check if any ally is positioned for flanking
        for ally_pos in klingon_positions:
            # Simple flanking check: allies on different sides of player
            if self._are_flanking_positions(klingon_pos, ally_pos, player_pos):
                return True
        
        return False
    
    def _are_flanking_positions(self, pos1: Tuple[int, int], pos2: Tuple[int, int], 
                               target: Tuple[int, int]) -> bool:
        """Check if two positions are flanking a target."""
        x1, y1 = pos1
        x2, y2 = pos2
        tx, ty = target
        
        # Calculate vectors from target to each position
        v1x, v1y = x1 - tx, y1 - ty
        v2x, v2y = x2 - tx, y2 - ty
        
        # Check if vectors point in roughly opposite directions
        dot_product = v1x * v2x + v1y * v2y
        return dot_product < 0  # Negative dot product means opposite directions
    
    def _find_escape_routes(self, klingon_pos: Tuple[int, int], player_pos: Tuple[int, int], 
                           quadrant_data: Dict[Tuple[int, int], str]) -> List[Tuple[int, int]]:
        """Find available escape routes."""
        x, y = klingon_pos
        escape_routes = []
        
        # Check all adjacent positions
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                new_x, new_y = x + dx, y + dy
                new_pos = (new_x, new_y)
                
                # Check if position is valid and empty
                if (1 <= new_x <= 8 and 1 <= new_y <= 8 and 
                    new_pos not in quadrant_data):
                    
                    # Check if this moves away from player
                    current_distance = self._calculate_distance(klingon_pos, player_pos)
                    new_distance = self._calculate_distance(new_pos, player_pos)
                    
                    if new_distance > current_distance:
                        escape_routes.append(new_pos)
        
        return escape_routes
    
    def _calculate_optimal_combat_range(self, player_ship) -> float:
        """Calculate optimal combat range based on player ship status."""
        # Base optimal range
        optimal_range = 3.0
        
        # Adjust based on player shields
        shield_ratio = player_ship.shields / player_ship.max_shields if player_ship.max_shields > 0 else 0
        if shield_ratio > 0.7:
            optimal_range += 1.0  # Stay farther if player has strong shields
        elif shield_ratio < 0.3:
            optimal_range -= 1.0  # Move closer if player shields are weak
        
        return max(1.0, min(6.0, optimal_range))
    
    def _calculate_attack_damage(self, attack_power: int, distance: float) -> int:
        """Calculate attack damage based on power and distance."""
        # Base damage calculation
        base_damage = attack_power // 10
        
        # Distance modifier (closer = more damage)
        distance_modifier = max(0.5, 1.0 - (distance - 1) * 0.1)
        
        # Random variance
        variance = random.uniform(0.8, 1.2)
        
        final_damage = int(base_damage * distance_modifier * variance)
        return max(1, final_damage)
    
    def _find_best_retreat_direction(self, klingon: KlingonState, 
                                   tactical_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """Find the best direction to retreat."""
        # Simple implementation: move away from player
        escape_routes = tactical_analysis.get('escape_routes', [])
        if escape_routes:
            return random.choice(escape_routes)
        else:
            # Fallback: random adjacent position
            x, y = klingon.position
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            return (max(1, min(8, x + dx)), max(1, min(8, y + dy)))
    
    def _calculate_move_away_position(self, current_pos: Tuple[int, int], 
                                    tactical_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate position to move away from player."""
        # Simple implementation: move in opposite direction from player
        x, y = current_pos
        # This would need player position from tactical analysis
        # For now, return a random adjacent position
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        return (max(1, min(8, x + dx)), max(1, min(8, y + dy)))
    
    def _calculate_move_closer_position(self, current_pos: Tuple[int, int], 
                                      tactical_analysis: Dict[str, Any]) -> Tuple[int, int]:
        """Calculate position to move closer to player."""
        # Simple implementation: move toward player
        x, y = current_pos
        # This would need player position from tactical analysis
        # For now, return a random adjacent position
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        return (max(1, min(8, x + dx)), max(1, min(8, y + dy)))
    
    def _update_player_behavior_model(self, player_ship, tactical_analysis: Dict[str, Any]):
        """Update the model of player behavior for adaptive AI."""
        self.player_behavior['total_encounters'] += 1
        
        # Update weapon preferences based on player actions
        # This would be called with actual player action data
        
        # Update aggression level based on player actions
        # This is a simplified model - real implementation would track actual player decisions
        
        # Update shield usage patterns
        shield_ratio = player_ship.shields / player_ship.max_shields if player_ship.max_shields > 0 else 0
        self.player_behavior['shield_usage_pattern'] = (
            self.player_behavior['shield_usage_pattern'] * 0.9 + shield_ratio * 0.1
        )
    
    def report_combat_result(self, klingon_pos: Tuple[int, int], result: str, 
                           damage_dealt: int = 0, damage_received: int = 0):
        """Report the result of combat for learning purposes."""
        if klingon_pos in self.klingon_states:
            klingon = self.klingon_states[klingon_pos]
            
            # Update combat statistics
            self.combat_stats['total_damage_dealt'] += damage_dealt
            self.combat_stats['total_damage_received'] += damage_received
            
            if result == 'hit':
                self.combat_stats['total_hits'] += 1
            
            self.combat_stats['total_shots_fired'] += 1
            
            # Update Klingon state
            if damage_received > 0:
                klingon.health = max(0, klingon.health - damage_received)
                klingon.turns_since_damage = 0
            
            # Remove destroyed Klingons
            if klingon.health <= 0:
                self.combat_stats['ships_destroyed'] += 1
                del self.klingon_states[klingon_pos]
    
    def get_ai_statistics(self) -> Dict[str, Any]:
        """Get AI performance statistics."""
        total_shots = max(1, self.combat_stats['total_shots_fired'])
        
        return {
            'combat_accuracy': self.combat_stats['total_hits'] / total_shots,
            'average_damage_per_shot': self.combat_stats['total_damage_dealt'] / total_shots,
            'ships_active': len(self.klingon_states),
            'total_encounters': self.player_behavior['total_encounters'],
            'adaptation_data': self.player_behavior.copy(),
            'combat_effectiveness': self._calculate_combat_effectiveness()
        }
    
    def _calculate_combat_effectiveness(self) -> float:
        """Calculate overall AI combat effectiveness."""
        if self.combat_stats['total_shots_fired'] == 0:
            return 0.0
        
        accuracy = self.combat_stats['total_hits'] / self.combat_stats['total_shots_fired']
        damage_efficiency = self.combat_stats['total_damage_dealt'] / max(1, self.combat_stats['total_damage_received'])
        
        return min(1.0, (accuracy + min(1.0, damage_efficiency / 2.0)) / 2.0)
