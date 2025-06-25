"""
Configuration Management System

This module handles loading and managing configuration settings
for the Trek game from YAML files.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from .logger import get_logger


class Config:
    """
    Configuration management system.
    
    Loads configuration from YAML files and provides easy access
    to configuration values with defaults.
    """
    
    def __init__(self, config_file: str = "config/default.yaml"):
        """Initialize configuration from file."""
        self.logger = get_logger(__name__)
        self.config_data: Dict[str, Any] = {}
        self.config_file = config_file
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            config_path = Path(self.config_file)
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Configuration loaded from {config_path}")
            else:
                self.logger.warning(f"Configuration file not found: {config_path}")
                self._create_default_config()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration."""
        self.config_data = {
            'game': {
                'difficulty': 'normal',
                'mission_duration': 30.0,
                'random_seed': None
            },
            'galaxy': {
                'total_klingons': 15,
                'total_starbases': 4,
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
            },
            'interface': {
                'ascii': {
                    'use_colors': True,
                    'screen_width': 80
                },
                'pygame': {
                    'window_width': 1024,
                    'window_height': 768,
                    'fullscreen': False,
                    'fps': 60
                }
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/trek.log',
                'max_size': '10MB',
                'backup_count': 5
            }
        }
        
        self.logger.info("Using default configuration")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'game.difficulty')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting config key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        try:
            keys = key.split('.')
            config = self.config_data
            
            # Navigate to parent dictionary
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            self.logger.debug(f"Set config '{key}' = {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting config key '{key}': {e}")
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (e.g., 'game', 'ai.klingon')
            
        Returns:
            Dictionary containing section data
        """
        return self.get(section, {})
    
    def save_config(self, filename: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            filename: Optional filename, uses current config file if None
        """
        try:
            save_path = Path(filename or self.config_file)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def reload_config(self):
        """Reload configuration from file."""
        self._load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data."""
        return self.config_data.copy()
    
    def validate_config(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate required sections
            required_sections = ['game', 'galaxy', 'ship', 'ai']
            for section in required_sections:
                if section not in self.config_data:
                    self.logger.error(f"Missing required config section: {section}")
                    return False
            
            # Validate specific values
            if self.get('galaxy.total_klingons', 0) <= 0:
                self.logger.error("Invalid galaxy.total_klingons value")
                return False
            
            if self.get('ship.max_energy', 0) <= 0:
                self.logger.error("Invalid ship.max_energy value")
                return False
            
            # Add more validation as needed
            
            self.logger.info("Configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False
