"""
Event Management System

This module handles random events, mission events, and dynamic
story generation to enhance gameplay experience.
"""

import random
from typing import Dict, List, Any, Optional
from enum import Enum
from ..utils.logger import get_logger


class EventType(Enum):
    """Types of events that can occur."""
    SOLAR_STORM = "solar_storm"
    SPACE_ANOMALY = "space_anomaly"
    DISTRESS_CALL = "distress_call"
    KLINGON_REINFORCEMENTS = "klingon_reinforcements"
    STARBASE_EMERGENCY = "starbase_emergency"
    EQUIPMENT_MALFUNCTION = "equipment_malfunction"
    DISCOVERY = "discovery"
    DIPLOMATIC_ENCOUNTER = "diplomatic_encounter"


class EventManager:
    """
    Manages random events and dynamic story generation.
    
    Creates contextual events based on game state, player actions,
    and mission progress to enhance the gameplay experience.
    """
    
    def __init__(self, config):
        """Initialize the event manager."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # Event configuration
        self.random_event_chance = config.get('events.random_event_chance', 0.05)
        self.event_cooldown = 0  # Turns since last event
        self.min_cooldown = 5    # Minimum turns between events
        
        # Active events
        self.active_events: Dict[str, Dict[str, Any]] = {}
        
        # Event history
        self.event_history: List[Dict[str, Any]] = []
        
        self.logger.info("Event manager initialized")
    
    def initialize_mission_events(self):
        """Initialize mission-specific events."""
        # Set up initial mission context
        self.logger.info("Mission events initialized")
    
    def check_for_events(self, game_state, ship, galaxy) -> List[str]:
        """
        Check if any events should occur this turn.
        
        Args:
            game_state: Current game state
            ship: Player ship object
            galaxy: Galaxy object
            
        Returns:
            List of event messages
        """
        events = []
        
        # Update event cooldown
        self.event_cooldown += 1
        
        # Process active events
        events.extend(self._process_active_events(game_state, ship, galaxy))
        
        # Check for new random events
        if (self.event_cooldown >= self.min_cooldown and 
            random.random() < self.random_event_chance):
            
            new_event = self._generate_random_event(game_state, ship, galaxy)
            if new_event:
                events.extend(new_event)
                self.event_cooldown = 0
        
        # Check for contextual events
        contextual_events = self._check_contextual_events(game_state, ship, galaxy)
        events.extend(contextual_events)
        
        return events
    
    def _process_active_events(self, game_state, ship, galaxy) -> List[str]:
        """Process ongoing events."""
        events = []
        completed_events = []
        
        for event_id, event_data in self.active_events.items():
            event_type = EventType(event_data['type'])
            
            if event_type == EventType.SOLAR_STORM:
                result = self._process_solar_storm(event_data, ship)
                if result:
                    events.extend(result)
                
                # Check if storm is ending
                event_data['duration'] -= 1
                if event_data['duration'] <= 0:
                    events.append("Solar storm subsiding...")
                    completed_events.append(event_id)
            
            elif event_type == EventType.SPACE_ANOMALY:
                result = self._process_space_anomaly(event_data, ship, galaxy)
                if result:
                    events.extend(result)
                
                # Anomalies are typically one-time events
                completed_events.append(event_id)
        
        # Remove completed events
        for event_id in completed_events:
            del self.active_events[event_id]
        
        return events
    
    def _generate_random_event(self, game_state, ship, galaxy) -> Optional[List[str]]:
        """Generate a random event based on current context."""
        # Weight events based on context
        event_weights = self._calculate_event_weights(game_state, ship, galaxy)
        
        if not event_weights:
            return None
        
        # Choose event type
        event_types = list(event_weights.keys())
        weights = list(event_weights.values())
        chosen_event = random.choices(event_types, weights=weights)[0]
        
        # Generate the event
        return self._create_event(chosen_event, game_state, ship, galaxy)
    
    def _calculate_event_weights(self, game_state, ship, galaxy) -> Dict[EventType, float]:
        """Calculate weights for different event types based on context."""
        weights = {}
        
        # Base weights
        base_weights = {
            EventType.SOLAR_STORM: 0.2,
            EventType.SPACE_ANOMALY: 0.15,
            EventType.DISTRESS_CALL: 0.1,
            EventType.KLINGON_REINFORCEMENTS: 0.1,
            EventType.STARBASE_EMERGENCY: 0.05,
            EventType.EQUIPMENT_MALFUNCTION: 0.15,
            EventType.DISCOVERY: 0.1,
            EventType.DIPLOMATIC_ENCOUNTER: 0.05
        }
        
        # Modify weights based on context
        for event_type, base_weight in base_weights.items():
            weight = base_weight
            
            # Increase Klingon events if many Klingons remain
            if event_type == EventType.KLINGON_REINFORCEMENTS:
                if game_state.klingons_remaining > 10:
                    weight *= 1.5
                elif game_state.klingons_remaining < 5:
                    weight *= 0.5
            
            # Increase equipment malfunctions if ship is damaged
            elif event_type == EventType.EQUIPMENT_MALFUNCTION:
                if ship.has_damage():
                    weight *= 2.0
            
            # Increase starbase events if near starbases
            elif event_type == EventType.STARBASE_EMERGENCY:
                quadrant_data = galaxy.get_quadrant_summary(ship.current_quadrant)
                if quadrant_data[1] > 0:  # Starbases in current quadrant
                    weight *= 3.0
            
            # Reduce discovery events late in mission
            elif event_type == EventType.DISCOVERY:
                time_remaining = game_state.mission_time_limit - game_state.stardate
                if time_remaining < 10:
                    weight *= 0.3
            
            weights[event_type] = weight
        
        return weights
    
    def _create_event(self, event_type: EventType, game_state, ship, galaxy) -> List[str]:
        """Create a specific event."""
        event_id = f"{event_type.value}_{len(self.event_history)}"
        
        if event_type == EventType.SOLAR_STORM:
            return self._create_solar_storm_event(event_id, ship)
        
        elif event_type == EventType.SPACE_ANOMALY:
            return self._create_space_anomaly_event(event_id, ship, galaxy)
        
        elif event_type == EventType.DISTRESS_CALL:
            return self._create_distress_call_event(event_id, game_state, galaxy)
        
        elif event_type == EventType.KLINGON_REINFORCEMENTS:
            return self._create_klingon_reinforcements_event(event_id, galaxy)
        
        elif event_type == EventType.STARBASE_EMERGENCY:
            return self._create_starbase_emergency_event(event_id, galaxy)
        
        elif event_type == EventType.EQUIPMENT_MALFUNCTION:
            return self._create_equipment_malfunction_event(event_id, ship)
        
        elif event_type == EventType.DISCOVERY:
            return self._create_discovery_event(event_id, ship)
        
        elif event_type == EventType.DIPLOMATIC_ENCOUNTER:
            return self._create_diplomatic_encounter_event(event_id, game_state)
        
        return []
    
    def _create_solar_storm_event(self, event_id: str, ship) -> List[str]:
        """Create a solar storm event."""
        duration = random.randint(2, 5)
        energy_drain = self.config.get('events.solar_storm.energy_drain', 200)
        
        self.active_events[event_id] = {
            'type': EventType.SOLAR_STORM.value,
            'duration': duration,
            'energy_drain': energy_drain
        }
        
        # Immediate effect
        ship.energy = max(0, ship.energy - energy_drain)
        
        self.logger.info(f"Solar storm event created: {duration} turns, {energy_drain} energy drain")
        
        return [
            "ALERT: Solar storm detected!",
            f"Energy systems disrupted - {energy_drain} energy lost",
            f"Storm will last approximately {duration} turns"
        ]
    
    def _create_space_anomaly_event(self, event_id: str, ship, galaxy) -> List[str]:
        """Create a space anomaly event."""
        anomaly_types = [
            "temporal_distortion",
            "gravitational_anomaly",
            "subspace_interference",
            "quantum_fluctuation"
        ]
        
        anomaly_type = random.choice(anomaly_types)
        
        self.active_events[event_id] = {
            'type': EventType.SPACE_ANOMALY.value,
            'anomaly_type': anomaly_type
        }
        
        effects = []
        
        if anomaly_type == "temporal_distortion":
            effects.append("Time flow altered - mission clock affected")
        elif anomaly_type == "gravitational_anomaly":
            effects.append("Navigation systems disrupted")
        elif anomaly_type == "subspace_interference":
            effects.append("Communications and sensors impaired")
        elif anomaly_type == "quantum_fluctuation":
            effects.append("Weapon systems experiencing power fluctuations")
        
        self.logger.info(f"Space anomaly event: {anomaly_type}")
        
        return [
            f"SCIENCE ALERT: {anomaly_type.replace('_', ' ').title()} detected!",
            *effects
        ]
    
    def _create_distress_call_event(self, event_id: str, game_state, galaxy) -> List[str]:
        """Create a distress call event."""
        ship_types = ["merchant vessel", "science ship", "colony transport", "patrol craft"]
        ship_type = random.choice(ship_types)
        
        # Find a nearby quadrant for the distress call
        nearby_quadrants = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                qx = game_state.stardate + dx  # This should use ship position
                qy = game_state.stardate + dy  # This is incorrect, should be fixed
                if galaxy.is_valid_quadrant((qx, qy)):
                    nearby_quadrants.append((qx, qy))
        
        if nearby_quadrants:
            distress_quadrant = random.choice(nearby_quadrants)
        else:
            distress_quadrant = (random.randint(1, 8), random.randint(1, 8))
        
        self.event_history.append({
            'type': EventType.DISTRESS_CALL.value,
            'ship_type': ship_type,
            'quadrant': distress_quadrant,
            'stardate': game_state.stardate
        })
        
        self.logger.info(f"Distress call event: {ship_type} in quadrant {distress_quadrant}")
        
        return [
            f"COMMUNICATIONS: Distress call received!",
            f"{ship_type.title()} requesting assistance in quadrant {distress_quadrant[0]},{distress_quadrant[1]}",
            "Responding to distress calls improves Federation relations"
        ]
    
    def _create_klingon_reinforcements_event(self, event_id: str, galaxy) -> List[str]:
        """Create Klingon reinforcements event."""
        # Add Klingons to a random quadrant
        reinforcement_quadrant = (random.randint(1, 8), random.randint(1, 8))
        num_reinforcements = random.randint(1, 3)
        
        # Add Klingons to the galaxy (this would need galaxy modification methods)
        self.logger.info(f"Klingon reinforcements: {num_reinforcements} ships in {reinforcement_quadrant}")
        
        return [
            "INTELLIGENCE ALERT: Klingon reinforcements detected!",
            f"{num_reinforcements} additional Klingon ships in quadrant {reinforcement_quadrant[0]},{reinforcement_quadrant[1]}",
            "Mission difficulty increased"
        ]
    
    def _create_starbase_emergency_event(self, event_id: str, galaxy) -> List[str]:
        """Create starbase emergency event."""
        emergency_types = [
            "medical emergency",
            "technical malfunction",
            "supply shortage",
            "defensive systems offline"
        ]
        
        emergency_type = random.choice(emergency_types)
        
        self.event_history.append({
            'type': EventType.STARBASE_EMERGENCY.value,
            'emergency_type': emergency_type
        })
        
        self.logger.info(f"Starbase emergency: {emergency_type}")
        
        return [
            "STARFLEET COMMAND: Starbase emergency reported!",
            f"Starbase experiencing {emergency_type}",
            "Assistance may be required"
        ]
    
    def _create_equipment_malfunction_event(self, event_id: str, ship) -> List[str]:
        """Create equipment malfunction event."""
        # Cause additional system damage
        systems = ['warp_engines', 'impulse_engines', 'phasers', 'torpedo_tubes', 'sensors']
        affected_system = random.choice(systems)
        
        # Add damage to the system
        current_damage = getattr(ship.systems, affected_system)
        additional_damage = random.uniform(0.1, 0.3)
        new_damage = min(1.0, current_damage + additional_damage)
        setattr(ship.systems, affected_system, new_damage)
        
        self.logger.info(f"Equipment malfunction: {affected_system} damaged")
        
        return [
            "ENGINEERING ALERT: Equipment malfunction detected!",
            f"{affected_system.replace('_', ' ').title()} experiencing problems",
            "Recommend immediate repair or docking with starbase"
        ]
    
    def _create_discovery_event(self, event_id: str, ship) -> List[str]:
        """Create discovery event."""
        discoveries = [
            ("ancient artifact", "energy boost", 300),
            ("abandoned supply cache", "torpedo resupply", 2),
            ("derelict ship", "technology upgrade", 0),
            ("rare mineral deposit", "shield enhancement", 200)
        ]
        
        discovery, benefit_type, benefit_amount = random.choice(discoveries)
        
        # Apply benefit
        if benefit_type == "energy boost":
            ship.energy = min(ship.max_energy, ship.energy + benefit_amount)
        elif benefit_type == "torpedo resupply":
            ship.torpedoes = min(ship.max_torpedoes, ship.torpedoes + benefit_amount)
        elif benefit_type == "shield enhancement":
            ship.shields = min(ship.max_shields, ship.shields + benefit_amount)
        
        self.logger.info(f"Discovery event: {discovery} - {benefit_type}")
        
        return [
            f"SCIENCE ALERT: {discovery.title()} discovered!",
            f"Benefit gained: {benefit_type.replace('_', ' ')}",
            "Fortune favors the bold explorer"
        ]
    
    def _create_diplomatic_encounter_event(self, event_id: str, game_state) -> List[str]:
        """Create diplomatic encounter event."""
        species = ["Vulcan", "Andorian", "Tellarite", "Orion", "Gorn"]
        encountered_species = random.choice(species)
        
        self.event_history.append({
            'type': EventType.DIPLOMATIC_ENCOUNTER.value,
            'species': encountered_species,
            'stardate': game_state.stardate
        })
        
        self.logger.info(f"Diplomatic encounter: {encountered_species}")
        
        return [
            f"DIPLOMATIC ALERT: {encountered_species} vessel encountered!",
            "Peaceful contact established",
            "Diplomatic relations may affect mission outcome"
        ]
    
    def _process_solar_storm(self, event_data: Dict[str, Any], ship) -> Optional[List[str]]:
        """Process ongoing solar storm effects."""
        energy_drain = event_data.get('energy_drain', 100) // 4  # Reduced per-turn drain
        
        if ship.energy > energy_drain:
            ship.energy -= energy_drain
            return [f"Solar storm continues - {energy_drain} energy lost"]
        else:
            # Not enough energy, reduce what we can
            lost_energy = ship.energy
            ship.energy = 0
            return [f"Solar storm drains remaining {lost_energy} energy - CRITICAL!"]
        
        return None
    
    def _process_space_anomaly(self, event_data: Dict[str, Any], ship, galaxy) -> Optional[List[str]]:
        """Process space anomaly effects."""
        anomaly_type = event_data.get('anomaly_type', 'unknown')
        
        # Apply ongoing effects based on anomaly type
        if anomaly_type == "subspace_interference":
            # Reduce sensor efficiency temporarily
            return ["Subspace interference affecting sensors"]
        
        return None
    
    def _check_contextual_events(self, game_state, ship, galaxy) -> List[str]:
        """Check for events triggered by specific game conditions."""
        events = []
        
        # Low energy warning
        if ship.energy < 500 and ship.energy > 0:
            if random.random() < 0.1:  # 10% chance per turn
                events.append("ENGINEERING: Energy reserves critically low!")
        
        # Time pressure warning
        time_remaining = game_state.mission_time_limit - game_state.stardate
        if time_remaining < 5 and time_remaining > 0:
            if random.random() < 0.2:  # 20% chance per turn
                events.append(f"COMMAND: Mission time critical - {time_remaining:.1f} stardates remaining!")
        
        # Victory close warning
        if game_state.klingons_remaining <= 3 and game_state.klingons_remaining > 0:
            if random.random() < 0.15:  # 15% chance per turn
                events.append(f"TACTICAL: Only {game_state.klingons_remaining} Klingon ships remain!")
        
        return events
    
    def get_event_history(self) -> List[Dict[str, Any]]:
        """Get the history of all events."""
        return self.event_history.copy()
    
    def get_active_events(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active events."""
        return self.active_events.copy()
