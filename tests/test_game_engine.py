"""
Unit tests for the Game Engine.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.engine import GameEngine, GameState
from utils.config import Config


class TestGameEngine:
    """Test cases for the GameEngine class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = Config()
        config.config_data = {
            'game': {
                'difficulty': 'normal',
                'mission_duration': 30.0,
                'random_seed': 12345
            },
            'galaxy': {
                'total_klingons': 5,
                'total_starbases': 2,
                'star_density': 0.3,
                'klingon_density': 0.2
            },
            'ship': {
                'max_energy': 3000,
                'max_shields': 1500,
                'max_torpedoes': 10
            },
            'ai': {
                'klingon': {
                    'base_aggression': 0.7,
                    'learning_rate': 0.1,
                    'tactical_awareness': 0.8,
                    'adaptation_enabled': True,
                    'base_health': 100,
                    'base_energy': 200
                },
                'strategic': {
                    'planning_depth': 3,
                    'risk_tolerance': 0.5,
                    'optimization_enabled': True
                }
            }
        }
        return config
    
    @pytest.fixture
    def game_engine(self, config):
        """Create a test game engine."""
        return GameEngine(config)
    
    def test_game_engine_initialization(self, game_engine):
        """Test that game engine initializes correctly."""
        assert game_engine is not None
        assert game_engine.state is not None
        assert game_engine.galaxy is not None
        assert game_engine.ship is not None
        assert game_engine.combat_system is not None
        assert not game_engine.game_over
        assert not game_engine.victory
    
    def test_game_state_initialization(self, game_engine):
        """Test that game state is initialized correctly."""
        state = game_engine.state
        assert state.stardate == 2267.0
        assert state.mission_time_limit == 2297.0  # 2267 + 30
        assert state.score == 0
        assert state.difficulty == 'normal'
        assert state.klingons_remaining > 0
        assert state.starbases_remaining > 0
    
    def test_navigation_command(self, game_engine):
        """Test navigation command processing."""
        # Test valid navigation
        result = game_engine.process_turn("nav", ["2,3"])
        assert result["success"] is True
        assert game_engine.ship.current_quadrant == (2, 3)
        
        # Test invalid navigation
        result = game_engine.process_turn("nav", ["9,9"])
        assert result["success"] is False
    
    def test_sensor_commands(self, game_engine):
        """Test sensor command processing."""
        # Short range sensors
        result = game_engine.process_turn("srs")
        assert result["success"] is True
        assert "scan_data" in result
        
        # Long range sensors
        result = game_engine.process_turn("lrs")
        assert result["success"] is True
        assert "scan_data" in result
    
    def test_shield_command(self, game_engine):
        """Test shield control command."""
        initial_energy = game_engine.ship.energy
        
        # Raise shields
        result = game_engine.process_turn("shi", ["1000"])
        assert result["success"] is True
        assert game_engine.ship.shields == 1000
        assert game_engine.ship.energy < initial_energy
        
        # Test insufficient energy
        result = game_engine.process_turn("shi", ["5000"])
        assert result["success"] is False
    
    def test_damage_report_command(self, game_engine):
        """Test damage report command."""
        result = game_engine.process_turn("dam")
        assert result["success"] is True
        assert "damage_data" in result
    
    def test_computer_command(self, game_engine):
        """Test computer functions."""
        # Distance calculation
        result = game_engine.process_turn("com", ["distance", "3,4"])
        assert result["success"] is True
        
        # Status report
        result = game_engine.process_turn("com", ["status"])
        assert result["success"] is True
        assert "status_data" in result
    
    def test_invalid_command(self, game_engine):
        """Test handling of invalid commands."""
        result = game_engine.process_turn("invalid_command")
        assert result["success"] is False
        assert "Unknown command" in result["message"]
    
    def test_game_statistics(self, game_engine):
        """Test game statistics collection."""
        stats = game_engine.get_game_statistics()
        assert "play_time_seconds" in stats
        assert "turns_played" in stats
        assert "efficiency_rating" in stats
        assert stats["turns_played"] >= 0
        assert 0.0 <= stats["efficiency_rating"] <= 1.0
    
    def test_save_load_game(self, game_engine, tmp_path):
        """Test save and load functionality."""
        # Make some changes to the game state
        game_engine.process_turn("nav", ["2,2"])
        game_engine.ship.energy = 2500
        
        # Save the game
        save_file = tmp_path / "test_save.json"
        success = game_engine.save_game(str(save_file))
        assert success
        assert save_file.exists()
        
        # Create a new game engine and load the save
        new_engine = GameEngine(game_engine.config)
        success = new_engine.load_game(str(save_file))
        assert success
        assert new_engine.ship.current_quadrant == (2, 2)
        assert new_engine.ship.energy == 2500


class TestGameState:
    """Test cases for the GameState class."""
    
    def test_game_state_creation(self):
        """Test GameState creation and serialization."""
        state = GameState(
            stardate=2267.5,
            mission_time_limit=2297.0,
            score=100,
            difficulty="normal",
            klingons_remaining=10,
            starbases_remaining=3,
            player_wins=0,
            player_losses=0,
            total_energy_used=500,
            total_torpedoes_fired=2,
            quadrants_visited=5,
            combat_encounters=3
        )
        
        # Test serialization
        state_dict = state.to_dict()
        assert state_dict["stardate"] == 2267.5
        assert state_dict["score"] == 100
        assert state_dict["difficulty"] == "normal"
        
        # Test deserialization
        new_state = GameState.from_dict(state_dict)
        assert new_state.stardate == 2267.5
        assert new_state.score == 100
        assert new_state.difficulty == "normal"


if __name__ == "__main__":
    pytest.main([__file__])
