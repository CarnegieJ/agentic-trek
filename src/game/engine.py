"""
Game Engine - Core game logic and state management

This module contains the main game engine that manages the overall game state,
coordinates between different subsystems, and handles the main game loop logic.
"""

import random
import time
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from .galaxy import Galaxy
from .ship import Ship
from .combat import CombatSystem
from .events import EventManager
from ai.klingon_ai import KlingonAI
from ai.strategic_ai import StrategicAI
from utils.logger import get_logger


@dataclass
class GameState:
    """Represents the current state of the game."""
    stardate: float
    mission_time_limit: float
    score: int
    difficulty: str
    klingons_remaining: int
    starbases_remaining: int
    player_wins: int
    player_losses: int
    total_energy_used: int
    total_torpedoes_fired: int
    quadrants_visited: int
    combat_encounters: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """Create from dictionary for deserialization."""
        return cls(**data)


class GameEngine:
    """
    Main game engine that coordinates all game systems.
    
    This class manages the overall game state, coordinates between different
    subsystems (galaxy, ship, combat, AI), and provides the main game loop
    functionality.
    """
    
    def __init__(self, config):
        """Initialize the game engine with configuration."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize random seed if specified
        seed = config.get('game.random_seed')
        if seed:
            random.seed(seed)
            self.logger.info(f"Random seed set to: {seed}")
        
        # Initialize game state
        self.state = GameState(
            stardate=2267.0,
            mission_time_limit=2267.0 + config.get('game.mission_duration', 30.0),
            score=0,
            difficulty=config.get('game.difficulty', 'normal'),
            klingons_remaining=0,
            starbases_remaining=0,
            player_wins=0,
            player_losses=0,
            total_energy_used=0,
            total_torpedoes_fired=0,
            quadrants_visited=0,
            combat_encounters=0
        )
        
        # Initialize game systems
        self.galaxy = Galaxy(config)
        self.ship = Ship(config)
        self.combat_system = CombatSystem(config)
        self.event_manager = EventManager(config)
        
        # Initialize AI systems
        self.klingon_ai = KlingonAI(config)
        self.strategic_ai = StrategicAI(config)
        
        # Game flags
        self.game_over = False
        self.victory = False
        self.paused = False
        
        # Performance tracking
        self.start_time = time.time()
        self.turn_count = 0
        
        self.logger.info("Game engine initialized successfully")
        self._setup_new_game()
    
    def _setup_new_game(self):
        """Set up a new game with initial conditions."""
        self.logger.info("Setting up new game...")
        
        # Generate galaxy
        self.galaxy.generate()
        
        # Count initial Klingons and starbases
        self.state.klingons_remaining = self.galaxy.count_klingons()
        self.state.starbases_remaining = self.galaxy.count_starbases()
        
        # Place Enterprise in a safe starting location
        start_quadrant = self.galaxy.find_safe_starting_quadrant()
        self.ship.current_quadrant = start_quadrant
        self.ship.quadrant_position = self.galaxy.find_safe_position_in_quadrant(start_quadrant)
        
        # Initialize ship systems
        self.ship.reset_to_full_strength()
        
        # Set up initial events
        self.event_manager.initialize_mission_events()
        
        self.logger.info(f"New game setup complete:")
        self.logger.info(f"  Klingons: {self.state.klingons_remaining}")
        self.logger.info(f"  Starbases: {self.state.starbases_remaining}")
        self.logger.info(f"  Starting quadrant: {start_quadrant}")
        self.logger.info(f"  Mission time limit: {self.state.mission_time_limit}")
    
    def process_turn(self, command: str, parameters: List[str] = None) -> Dict[str, Any]:
        """
        Process a single game turn with the given command.
        
        Args:
            command: The command to execute
            parameters: Optional parameters for the command
            
        Returns:
            Dictionary containing the result of the command execution
        """
        if self.game_over or self.paused:
            return {"success": False, "message": "Game is not active"}
        
        self.turn_count += 1
        result = {"success": True, "message": "", "events": []}
        
        try:
            # Process the command
            if command.lower() == "nav":
                result = self._handle_navigation(parameters)
            elif command.lower() == "srs":
                result = self._handle_short_range_scan()
            elif command.lower() == "lrs":
                result = self._handle_long_range_scan()
            elif command.lower() == "pha":
                result = self._handle_phaser_fire(parameters)
            elif command.lower() == "tor":
                result = self._handle_torpedo_fire(parameters)
            elif command.lower() == "shi":
                result = self._handle_shields(parameters)
            elif command.lower() == "dock":
                result = self._handle_docking()
            elif command.lower() == "com":
                result = self._handle_computer(parameters)
            elif command.lower() == "dam":
                result = self._handle_damage_report()
            else:
                result = {"success": False, "message": f"Unknown command: {command}"}
            
            # Process AI turns if command was successful
            if result["success"]:
                ai_events = self._process_ai_turns()
                result["events"].extend(ai_events)
                
                # Advance time
                self._advance_time()
                
                # Check for random events
                random_events = self.event_manager.check_for_events(self.state, self.ship, self.galaxy)
                result["events"].extend(random_events)
                
                # Check win/lose conditions
                self._check_game_end_conditions()
        
        except Exception as e:
            self.logger.error(f"Error processing turn: {e}", exc_info=True)
            result = {"success": False, "message": f"Error processing command: {str(e)}"}
        
        return result
    
    def _handle_navigation(self, parameters: List[str]) -> Dict[str, Any]:
        """Handle navigation command."""
        if not parameters or len(parameters) < 1:
            return {"success": False, "message": "Navigation requires destination quadrant (e.g., 'nav 3,4')"}
        
        try:
            # Parse destination
            dest_str = parameters[0]
            if ',' in dest_str:
                x, y = map(int, dest_str.split(','))
            else:
                return {"success": False, "message": "Invalid destination format. Use 'x,y' format."}
            
            destination = (x, y)
            
            # Validate destination
            if not self.galaxy.is_valid_quadrant(destination):
                return {"success": False, "message": "Invalid quadrant coordinates"}
            
            # Calculate energy cost
            current_pos = self.ship.current_quadrant
            distance = self.galaxy.calculate_distance(current_pos, destination)
            energy_cost = int(distance * 8)  # Energy cost formula from original Trek
            
            if self.ship.energy < energy_cost:
                return {"success": False, "message": f"Insufficient energy. Need {energy_cost}, have {self.ship.energy}"}
            
            # Execute navigation
            self.ship.energy -= energy_cost
            self.ship.current_quadrant = destination
            self.ship.quadrant_position = (4, 4)  # Center of new quadrant
            self.state.total_energy_used += energy_cost
            
            # Check if this is a new quadrant
            if destination not in self.ship.visited_quadrants:
                self.ship.visited_quadrants.add(destination)
                self.state.quadrants_visited += 1
            
            return {
                "success": True,
                "message": f"Navigated to quadrant {destination}. Energy used: {energy_cost}",
                "events": [f"Entered quadrant {destination[0]},{destination[1]}"]
            }
            
        except ValueError:
            return {"success": False, "message": "Invalid quadrant coordinates"}
    
    def _handle_short_range_scan(self) -> Dict[str, Any]:
        """Handle short range sensor scan."""
        quadrant_data = self.galaxy.get_quadrant_data(self.ship.current_quadrant)
        scan_result = self.galaxy.format_quadrant_display(quadrant_data, self.ship.quadrant_position)
        
        return {
            "success": True,
            "message": "Short range sensors activated",
            "scan_data": scan_result,
            "events": []
        }
    
    def _handle_long_range_scan(self) -> Dict[str, Any]:
        """Handle long range sensor scan."""
        current_pos = self.ship.current_quadrant
        adjacent_data = self.galaxy.get_adjacent_quadrant_data(current_pos)
        
        return {
            "success": True,
            "message": "Long range sensors activated",
            "scan_data": adjacent_data,
            "events": []
        }
    
    def _handle_phaser_fire(self, parameters: List[str]) -> Dict[str, Any]:
        """Handle phaser firing."""
        if not parameters:
            return {"success": False, "message": "Phaser fire requires energy amount"}
        
        try:
            energy_amount = int(parameters[0])
            
            if energy_amount <= 0:
                return {"success": False, "message": "Invalid energy amount"}
            
            if self.ship.energy < energy_amount:
                return {"success": False, "message": f"Insufficient energy. Have {self.ship.energy}"}
            
            # Get enemies in current quadrant
            quadrant_data = self.galaxy.get_quadrant_data(self.ship.current_quadrant)
            enemies = [pos for pos, obj in quadrant_data.items() if obj == 'K']
            
            if not enemies:
                return {"success": False, "message": "No enemies in range"}
            
            # Execute combat
            combat_result = self.combat_system.execute_phaser_attack(
                self.ship, enemies, energy_amount, quadrant_data
            )
            
            self.ship.energy -= energy_amount
            self.state.total_energy_used += energy_amount
            
            # Update galaxy with combat results
            for destroyed_pos in combat_result.get("destroyed_enemies", []):
                self.galaxy.remove_object_from_quadrant(self.ship.current_quadrant, destroyed_pos)
                self.state.klingons_remaining -= 1
            
            return {
                "success": True,
                "message": combat_result["message"],
                "events": combat_result.get("events", [])
            }
            
        except ValueError:
            return {"success": False, "message": "Invalid energy amount"}
    
    def _handle_torpedo_fire(self, parameters: List[str]) -> Dict[str, Any]:
        """Handle torpedo firing."""
        if len(parameters) < 2:
            return {"success": False, "message": "Torpedo fire requires course and spread (e.g., 'tor 45 1')"}
        
        if self.ship.torpedoes <= 0:
            return {"success": False, "message": "No torpedoes remaining"}
        
        try:
            course = float(parameters[0])
            spread = int(parameters[1])
            
            if not (0 <= course <= 360):
                return {"success": False, "message": "Course must be between 0 and 360 degrees"}
            
            if spread <= 0:
                return {"success": False, "message": "Spread must be positive"}
            
            # Execute torpedo attack
            quadrant_data = self.galaxy.get_quadrant_data(self.ship.current_quadrant)
            combat_result = self.combat_system.execute_torpedo_attack(
                self.ship, course, spread, quadrant_data
            )
            
            self.ship.torpedoes -= 1
            self.state.total_torpedoes_fired += 1
            
            # Update galaxy with combat results
            for destroyed_pos in combat_result.get("destroyed_enemies", []):
                self.galaxy.remove_object_from_quadrant(self.ship.current_quadrant, destroyed_pos)
                self.state.klingons_remaining -= 1
            
            return {
                "success": True,
                "message": combat_result["message"],
                "events": combat_result.get("events", [])
            }
            
        except ValueError:
            return {"success": False, "message": "Invalid torpedo parameters"}
    
    def _handle_shields(self, parameters: List[str]) -> Dict[str, Any]:
        """Handle shield control."""
        if not parameters:
            return {
                "success": True,
                "message": f"Shield status: {self.ship.shields}/{self.ship.max_shields}",
                "events": []
            }
        
        try:
            shield_level = int(parameters[0])
            
            if shield_level < 0:
                return {"success": False, "message": "Shield level cannot be negative"}
            
            if shield_level > self.ship.max_shields:
                shield_level = self.ship.max_shields
            
            energy_needed = max(0, shield_level - self.ship.shields)
            
            if energy_needed > self.ship.energy:
                return {"success": False, "message": f"Insufficient energy. Need {energy_needed}, have {self.ship.energy}"}
            
            self.ship.energy -= energy_needed
            self.ship.shields = shield_level
            self.state.total_energy_used += energy_needed
            
            return {
                "success": True,
                "message": f"Shields set to {shield_level}",
                "events": []
            }
            
        except ValueError:
            return {"success": False, "message": "Invalid shield level"}
    
    def _handle_docking(self) -> Dict[str, Any]:
        """Handle docking with starbase."""
        quadrant_data = self.galaxy.get_quadrant_data(self.ship.current_quadrant)
        starbases = [pos for pos, obj in quadrant_data.items() if obj == 'B']
        
        if not starbases:
            return {"success": False, "message": "No starbase in this quadrant"}
        
        # Check if adjacent to a starbase
        ship_pos = self.ship.quadrant_position
        adjacent_starbase = None
        
        for base_pos in starbases:
            distance = abs(ship_pos[0] - base_pos[0]) + abs(ship_pos[1] - base_pos[1])
            if distance <= 1:
                adjacent_starbase = base_pos
                break
        
        if not adjacent_starbase:
            return {"success": False, "message": "Must be adjacent to starbase to dock"}
        
        # Perform docking - restore ship to full strength
        self.ship.energy = self.ship.max_energy
        self.ship.shields = self.ship.max_shields
        self.ship.torpedoes = self.ship.max_torpedoes
        self.ship.repair_all_damage()
        
        return {
            "success": True,
            "message": "Docked with starbase. All systems restored to full capacity.",
            "events": ["Docked with starbase", "Ship fully repaired and resupplied"]
        }
    
    def _handle_computer(self, parameters: List[str]) -> Dict[str, Any]:
        """Handle computer functions."""
        if not parameters:
            return {
                "success": True,
                "message": "Computer functions: distance, course, efficiency, status",
                "events": []
            }
        
        function = parameters[0].lower()
        
        if function == "distance":
            if len(parameters) < 2:
                return {"success": False, "message": "Distance calculation requires destination"}
            
            try:
                dest_str = parameters[1]
                x, y = map(int, dest_str.split(','))
                destination = (x, y)
                
                current_pos = self.ship.current_quadrant
                distance = self.galaxy.calculate_distance(current_pos, destination)
                energy_cost = int(distance * 8)
                
                return {
                    "success": True,
                    "message": f"Distance to {destination}: {distance:.2f} quadrants, Energy cost: {energy_cost}",
                    "events": []
                }
            except ValueError:
                return {"success": False, "message": "Invalid destination format"}
        
        elif function == "status":
            status_info = self._get_status_report()
            return {
                "success": True,
                "message": "Status report generated",
                "status_data": status_info,
                "events": []
            }
        
        else:
            return {"success": False, "message": f"Unknown computer function: {function}"}
    
    def _handle_damage_report(self) -> Dict[str, Any]:
        """Handle damage report."""
        damage_report = self.ship.get_damage_report()
        
        return {
            "success": True,
            "message": "Damage report generated",
            "damage_data": damage_report,
            "events": []
        }
    
    def _process_ai_turns(self) -> List[str]:
        """Process AI turns for all AI entities."""
        events = []
        
        # Get current quadrant data
        quadrant_data = self.galaxy.get_quadrant_data(self.ship.current_quadrant)
        klingons = [pos for pos, obj in quadrant_data.items() if obj == 'K']
        
        if klingons:
            self.state.combat_encounters += 1
            
            # Process Klingon AI actions
            for klingon_pos in klingons:
                ai_action = self.klingon_ai.decide_action(
                    klingon_pos, self.ship.quadrant_position, self.ship, quadrant_data
                )
                
                if ai_action["action"] == "attack":
                    # Klingon attacks player
                    damage = ai_action.get("damage", 0)
                    if damage > 0:
                        actual_damage = self.ship.take_damage(damage)
                        events.append(f"Klingon at {klingon_pos} attacks for {actual_damage} damage!")
                
                elif ai_action["action"] == "move":
                    # Klingon moves (update quadrant data)
                    new_pos = ai_action.get("new_position")
                    if new_pos and new_pos not in quadrant_data:
                        self.galaxy.move_object_in_quadrant(
                            self.ship.current_quadrant, klingon_pos, new_pos
                        )
                        events.append(f"Klingon moves from {klingon_pos} to {new_pos}")
        
        # Process strategic AI recommendations
        strategic_advice = self.strategic_ai.analyze_situation(self.state, self.ship, self.galaxy)
        if strategic_advice.get("urgent_warning"):
            events.append(f"Strategic Analysis: {strategic_advice['urgent_warning']}")
        
        return events
    
    def _advance_time(self):
        """Advance game time."""
        time_increment = 0.1  # Standard time increment per turn
        self.state.stardate += time_increment
    
    def _check_game_end_conditions(self):
        """Check if the game should end."""
        # Victory conditions
        if self.state.klingons_remaining <= 0:
            self.game_over = True
            self.victory = True
            self.state.player_wins += 1
            self.logger.info("Victory! All Klingons destroyed")
        
        # Defeat conditions
        elif self.ship.is_destroyed():
            self.game_over = True
            self.victory = False
            self.state.player_losses += 1
            self.logger.info("Defeat! Enterprise destroyed")
        
        elif self.state.stardate >= self.state.mission_time_limit:
            self.game_over = True
            self.victory = False
            self.state.player_losses += 1
            self.logger.info("Defeat! Mission time expired")
    
    def _get_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        return {
            "stardate": self.state.stardate,
            "time_remaining": self.state.mission_time_limit - self.state.stardate,
            "condition": self._get_ship_condition(),
            "quadrant": self.ship.current_quadrant,
            "energy": self.ship.energy,
            "shields": self.ship.shields,
            "torpedoes": self.ship.torpedoes,
            "klingons_remaining": self.state.klingons_remaining,
            "starbases_remaining": self.state.starbases_remaining,
            "score": self.state.score,
            "quadrants_visited": self.state.quadrants_visited,
            "combat_encounters": self.state.combat_encounters
        }
    
    def _get_ship_condition(self) -> str:
        """Determine ship condition based on current state."""
        if self.ship.shields <= 0 and self.ship.energy < 1000:
            return "RED"
        elif self.ship.energy < 2000 or self.ship.has_damage():
            return "YELLOW"
        else:
            return "GREEN"
    
    def save_game(self, filename: str) -> bool:
        """Save the current game state to file."""
        try:
            save_data = {
                "state": self.state.to_dict(),
                "ship": self.ship.to_dict(),
                "galaxy": self.galaxy.to_dict(),
                "turn_count": self.turn_count,
                "timestamp": time.time()
            }
            
            save_path = Path("saves") / filename
            save_path.parent.mkdir(exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            self.logger.info(f"Game saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save game: {e}")
            return False
    
    def load_game(self, filename: str) -> bool:
        """Load game state from file."""
        try:
            save_path = Path("saves") / filename
            
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            self.state = GameState.from_dict(save_data["state"])
            self.ship.from_dict(save_data["ship"])
            self.galaxy.from_dict(save_data["galaxy"])
            self.turn_count = save_data.get("turn_count", 0)
            
            self.logger.info(f"Game loaded from {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load game: {e}")
            return False
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get comprehensive game statistics."""
        current_time = time.time()
        play_time = current_time - self.start_time
        
        return {
            "play_time_seconds": play_time,
            "turns_played": self.turn_count,
            "average_turn_time": play_time / max(1, self.turn_count),
            "total_energy_used": self.state.total_energy_used,
            "total_torpedoes_fired": self.state.total_torpedoes_fired,
            "quadrants_visited": self.state.quadrants_visited,
            "combat_encounters": self.state.combat_encounters,
            "efficiency_rating": self._calculate_efficiency_rating()
        }
    
    def _calculate_efficiency_rating(self) -> float:
        """Calculate player efficiency rating."""
        if self.turn_count == 0:
            return 0.0
        
        # Base efficiency on resource usage and progress
        energy_efficiency = 1.0 - (self.state.total_energy_used / (self.turn_count * 100))
        torpedo_efficiency = 1.0 - (self.state.total_torpedoes_fired / max(1, self.state.combat_encounters))
        exploration_bonus = self.state.quadrants_visited / 64.0
        
        return max(0.0, min(1.0, (energy_efficiency + torpedo_efficiency + exploration_bonus) / 3.0))
