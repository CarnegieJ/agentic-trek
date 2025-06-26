"""
Strategic AI System

This module provides strategic analysis and recommendations to enhance
gameplay through intelligent mission planning and tactical advice.
"""

import math
from typing import Dict, List, Tuple, Any, Optional
from utils.logger import get_logger


class StrategicAI:
    """
    Strategic AI that provides mission planning and tactical advice.
    
    Analyzes the current game situation and provides recommendations
    for optimal play, resource management, and strategic decisions.
    """
    
    def __init__(self, config):
        """Initialize the strategic AI system."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # AI configuration
        self.planning_depth = config.get('ai.strategic.planning_depth', 3)
        self.risk_tolerance = config.get('ai.strategic.risk_tolerance', 0.5)
        self.optimization_enabled = config.get('ai.strategic.optimization_enabled', True)
        
        # Analysis history
        self.analysis_history: List[Dict[str, Any]] = []
        
        self.logger.info("Strategic AI system initialized")
    
    def analyze_situation(self, game_state, ship, galaxy) -> Dict[str, Any]:
        """
        Analyze the current game situation and provide strategic assessment.
        
        Args:
            game_state: Current game state
            ship: Player ship object
            galaxy: Galaxy object
            
        Returns:
            Dictionary containing strategic analysis and recommendations
        """
        analysis = {
            'timestamp': game_state.stardate,
            'threat_level': self._assess_threat_level(game_state, ship, galaxy),
            'resource_status': self._analyze_resources(ship),
            'mission_progress': self._analyze_mission_progress(game_state),
            'tactical_situation': self._analyze_tactical_situation(ship, galaxy),
            'recommendations': [],
            'urgent_warning': None,
            'efficiency_rating': self._calculate_efficiency_rating(game_state, ship)
        }
        
        # Generate recommendations based on analysis
        analysis['recommendations'] = self._generate_recommendations(analysis, game_state, ship, galaxy)
        
        # Check for urgent warnings
        analysis['urgent_warning'] = self._check_urgent_warnings(analysis, game_state, ship)
        
        # Store analysis in history
        self.analysis_history.append(analysis)
        
        self.logger.debug(f"Strategic analysis: threat={analysis['threat_level']:.2f}, efficiency={analysis['efficiency_rating']:.2f}")
        
        return analysis
    
    def _assess_threat_level(self, game_state, ship, galaxy) -> float:
        """Assess overall threat level (0.0 = safe, 1.0 = extreme danger)."""
        threat_factors = []
        
        # Klingon density threat
        klingon_threat = min(1.0, game_state.klingons_remaining / 15.0)
        threat_factors.append(klingon_threat * 0.4)
        
        # Time pressure threat
        time_remaining = game_state.mission_time_limit - game_state.stardate
        time_threat = max(0.0, 1.0 - (time_remaining / 30.0))
        threat_factors.append(time_threat * 0.3)
        
        # Ship condition threat
        ship_condition = self._assess_ship_condition(ship)
        condition_threat = 1.0 - ship_condition
        threat_factors.append(condition_threat * 0.2)
        
        # Local quadrant threat
        current_quadrant = galaxy.get_quadrant_summary(ship.current_quadrant)
        local_klingons = current_quadrant[0]
        local_threat = min(1.0, local_klingons / 3.0)
        threat_factors.append(local_threat * 0.1)
        
        return sum(threat_factors)
    
    def _analyze_resources(self, ship) -> Dict[str, Any]:
        """Analyze ship resource status."""
        return {
            'energy_status': self._categorize_resource_level(ship.energy, ship.max_energy),
            'energy_percent': (ship.energy / ship.max_energy) * 100,
            'shield_status': self._categorize_resource_level(ship.shields, ship.max_shields),
            'shield_percent': (ship.shields / ship.max_shields) * 100,
            'torpedo_status': self._categorize_resource_level(ship.torpedoes, ship.max_torpedoes),
            'torpedo_count': ship.torpedoes,
            'overall_status': self._assess_overall_resource_status(ship)
        }
    
    def _analyze_mission_progress(self, game_state) -> Dict[str, Any]:
        """Analyze mission progress and timeline."""
        time_remaining = game_state.mission_time_limit - game_state.stardate
        time_percent = (time_remaining / 30.0) * 100  # Assuming 30 stardate mission
        
        klingon_progress = 1.0 - (game_state.klingons_remaining / 15.0)  # Assuming 15 initial Klingons
        
        return {
            'time_remaining': time_remaining,
            'time_percent': time_percent,
            'time_status': self._categorize_time_status(time_percent),
            'klingons_destroyed': 15 - game_state.klingons_remaining,  # Assuming 15 initial
            'klingons_remaining': game_state.klingons_remaining,
            'progress_percent': klingon_progress * 100,
            'progress_status': self._categorize_progress_status(klingon_progress),
            'pace_analysis': self._analyze_mission_pace(game_state)
        }
    
    def _analyze_tactical_situation(self, ship, galaxy) -> Dict[str, Any]:
        """Analyze current tactical situation."""
        current_quadrant = galaxy.get_quadrant_summary(ship.current_quadrant)
        klingons_here = current_quadrant[0]
        starbases_here = current_quadrant[1]
        
        # Find nearest starbase
        nearest_starbase = galaxy.get_nearest_starbase(ship.current_quadrant)
        starbase_distance = None
        if nearest_starbase:
            starbase_distance = galaxy.calculate_distance(ship.current_quadrant, nearest_starbase)
        
        return {
            'immediate_threats': klingons_here,
            'local_support': starbases_here,
            'nearest_starbase_distance': starbase_distance,
            'combat_readiness': self._assess_combat_readiness(ship),
            'tactical_advantage': self._assess_tactical_advantage(ship, klingons_here, starbases_here)
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any], game_state, ship, galaxy) -> List[str]:
        """Generate strategic recommendations based on analysis."""
        recommendations = []
        
        # Resource management recommendations
        resource_status = analysis['resource_status']
        if resource_status['energy_status'] == 'critical':
            recommendations.append("PRIORITY: Seek starbase for energy replenishment")
        elif resource_status['energy_status'] == 'low':
            recommendations.append("Consider energy conservation measures")
        
        if resource_status['torpedo_count'] <= 2:
            recommendations.append("Torpedo supplies low - prioritize starbase resupply")
        
        # Tactical recommendations
        tactical = analysis['tactical_situation']
        if tactical['immediate_threats'] > 0:
            if tactical['combat_readiness'] < 0.5:
                recommendations.append("CAUTION: Combat situation unfavorable - consider retreat")
            else:
                recommendations.append("Engage enemies with optimal weapon selection")
        
        # Mission progress recommendations
        progress = analysis['mission_progress']
        if progress['pace_analysis'] == 'behind_schedule':
            recommendations.append("Mission pace slow - increase aggressive tactics")
        elif progress['pace_analysis'] == 'ahead_of_schedule':
            recommendations.append("Good progress - maintain current strategy")
        
        # Time management recommendations
        if progress['time_percent'] < 25:
            recommendations.append("URGENT: Time critical - focus on primary objectives")
        
        # Navigation recommendations
        if tactical['nearest_starbase_distance'] and tactical['nearest_starbase_distance'] <= 2:
            if ship.has_damage() or resource_status['overall_status'] == 'poor':
                recommendations.append("Consider docking at nearby starbase")
        
        return recommendations
    
    def _check_urgent_warnings(self, analysis: Dict[str, Any], game_state, ship) -> Optional[str]:
        """Check for urgent warnings that need immediate attention."""
        # Critical energy warning
        if ship.energy < 200:
            return "CRITICAL: Energy reserves dangerously low!"
        
        # Ship destruction warning
        if ship.is_destroyed():
            return "CRITICAL: Ship systems failing!"
        
        # Time critical warning
        time_remaining = game_state.mission_time_limit - game_state.stardate
        if time_remaining < 3:
            return f"CRITICAL: Mission time expires in {time_remaining:.1f} stardates!"
        
        # High threat warning
        if analysis['threat_level'] > 0.8:
            return "WARNING: Extreme danger detected!"
        
        return None
    
    def _categorize_resource_level(self, current: int, maximum: int) -> str:
        """Categorize resource level."""
        percent = (current / maximum) * 100
        
        if percent >= 75:
            return 'excellent'
        elif percent >= 50:
            return 'good'
        elif percent >= 25:
            return 'low'
        else:
            return 'critical'
    
    def _assess_overall_resource_status(self, ship) -> str:
        """Assess overall resource status."""
        energy_ratio = ship.energy / ship.max_energy
        shield_ratio = ship.shields / ship.max_shields
        torpedo_ratio = ship.torpedoes / ship.max_torpedoes
        
        avg_ratio = (energy_ratio + shield_ratio + torpedo_ratio) / 3
        
        if avg_ratio >= 0.75:
            return 'excellent'
        elif avg_ratio >= 0.5:
            return 'good'
        elif avg_ratio >= 0.25:
            return 'fair'
        else:
            return 'poor'
    
    def _categorize_time_status(self, time_percent: float) -> str:
        """Categorize time remaining status."""
        if time_percent >= 75:
            return 'ample'
        elif time_percent >= 50:
            return 'adequate'
        elif time_percent >= 25:
            return 'limited'
        else:
            return 'critical'
    
    def _categorize_progress_status(self, progress: float) -> str:
        """Categorize mission progress status."""
        if progress >= 0.8:
            return 'excellent'
        elif progress >= 0.6:
            return 'good'
        elif progress >= 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _analyze_mission_pace(self, game_state) -> str:
        """Analyze if mission is on pace."""
        time_elapsed = game_state.stardate - 2267.0  # Assuming start at 2267
        time_total = game_state.mission_time_limit - 2267.0
        time_progress = time_elapsed / time_total
        
        klingon_progress = 1.0 - (game_state.klingons_remaining / 15.0)  # Assuming 15 initial
        
        if klingon_progress > time_progress + 0.2:
            return 'ahead_of_schedule'
        elif klingon_progress < time_progress - 0.2:
            return 'behind_schedule'
        else:
            return 'on_schedule'
    
    def _assess_ship_condition(self, ship) -> float:
        """Assess overall ship condition (0.0 = destroyed, 1.0 = perfect)."""
        if ship.is_destroyed():
            return 0.0
        
        # Factor in energy, shields, and system damage
        energy_factor = ship.energy / ship.max_energy
        shield_factor = ship.shields / ship.max_shields
        
        # System damage factor
        damage_values = list(ship.systems.to_dict().values())
        avg_damage = sum(damage_values) / len(damage_values)
        system_factor = 1.0 - avg_damage
        
        # Weighted average
        condition = (energy_factor * 0.4 + shield_factor * 0.3 + system_factor * 0.3)
        
        return max(0.0, min(1.0, condition))
    
    def _assess_combat_readiness(self, ship) -> float:
        """Assess combat readiness (0.0 = unable to fight, 1.0 = fully ready)."""
        if ship.is_destroyed():
            return 0.0
        
        # Factor in weapons, shields, and energy
        phaser_readiness = ship.get_phaser_efficiency() if ship.can_use_phasers() else 0.0
        torpedo_readiness = ship.get_torpedo_efficiency() if ship.can_use_torpedoes() else 0.0
        
        weapon_readiness = max(phaser_readiness, torpedo_readiness)
        
        energy_readiness = min(1.0, ship.energy / 1000.0)  # 1000 energy for good combat
        shield_readiness = ship.shields / ship.max_shields
        
        # Weighted combat readiness
        readiness = (weapon_readiness * 0.4 + energy_readiness * 0.4 + shield_readiness * 0.2)
        
        return max(0.0, min(1.0, readiness))
    
    def _assess_tactical_advantage(self, ship, local_klingons: int, local_starbases: int) -> float:
        """Assess tactical advantage in current situation."""
        advantage = 0.0
        
        # Starbase advantage
        if local_starbases > 0:
            advantage += 0.3
        
        # Outnumbered disadvantage
        if local_klingons > 1:
            advantage -= 0.2 * (local_klingons - 1)
        
        # Ship condition advantage/disadvantage
        ship_condition = self._assess_ship_condition(ship)
        advantage += (ship_condition - 0.5) * 0.4
        
        return max(-1.0, min(1.0, advantage))
    
    def _calculate_efficiency_rating(self, game_state, ship) -> float:
        """Calculate overall player efficiency rating."""
        # Time efficiency
        time_elapsed = game_state.stardate - 2267.0
        expected_time = 30.0  # Expected mission duration
        time_efficiency = max(0.0, 1.0 - (time_elapsed / expected_time))
        
        # Resource efficiency
        resource_usage = (game_state.total_energy_used / max(1, game_state.quadrants_visited))
        resource_efficiency = max(0.0, 1.0 - (resource_usage / 1000.0))
        
        # Combat efficiency
        if game_state.combat_encounters > 0:
            combat_efficiency = min(1.0, (15 - game_state.klingons_remaining) / game_state.combat_encounters)
        else:
            combat_efficiency = 0.5
        
        # Overall efficiency
        efficiency = (time_efficiency * 0.3 + resource_efficiency * 0.3 + combat_efficiency * 0.4)
        
        return max(0.0, min(1.0, efficiency))
    
    def get_optimal_route(self, start_quadrant: Tuple[int, int], 
                         target_quadrants: List[Tuple[int, int]], 
                         galaxy) -> List[Tuple[int, int]]:
        """Calculate optimal route through multiple target quadrants."""
        if not target_quadrants:
            return []
        
        # Simple greedy approach - visit nearest unvisited target
        route = [start_quadrant]
        current = start_quadrant
        remaining_targets = target_quadrants.copy()
        
        while remaining_targets:
            # Find nearest target
            nearest_target = None
            min_distance = float('inf')
            
            for target in remaining_targets:
                distance = galaxy.calculate_distance(current, target)
                if distance < min_distance:
                    min_distance = distance
                    nearest_target = target
            
            if nearest_target:
                route.append(nearest_target)
                current = nearest_target
                remaining_targets.remove(nearest_target)
        
        return route[1:]  # Exclude starting position
    
    def estimate_energy_needed(self, route: List[Tuple[int, int]], galaxy) -> int:
        """Estimate energy needed for a route."""
        if len(route) < 2:
            return 0
        
        total_energy = 0
        for i in range(len(route) - 1):
            distance = galaxy.calculate_distance(route[i], route[i + 1])
            energy_cost = int(distance * 8)  # Standard energy cost formula
            total_energy += energy_cost
        
        return total_energy
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get history of strategic analyses."""
        return self.analysis_history.copy()
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(self.analysis_history) < 2:
            return {'insufficient_data': True}
        
        recent = self.analysis_history[-5:]  # Last 5 analyses
        
        # Calculate trends
        threat_trend = self._calculate_trend([a['threat_level'] for a in recent])
        efficiency_trend = self._calculate_trend([a['efficiency_rating'] for a in recent])
        
        return {
            'threat_trend': threat_trend,
            'efficiency_trend': efficiency_trend,
            'analysis_count': len(self.analysis_history),
            'recent_performance': recent[-1]['efficiency_rating'] if recent else 0.0
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        difference = second_half - first_half
        
        if difference > 0.1:
            return 'improving'
        elif difference < -0.1:
            return 'declining'
        else:
            return 'stable'
