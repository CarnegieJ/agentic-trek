"""
Logging System

This module provides centralized logging functionality for the Trek game.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "trek", level: int = logging.INFO, 
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up the main logger for the application.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.error(f"Failed to create file handler: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"trek.{name}")


class GameLogger:
    """
    Specialized logger for game events and statistics.
    """
    
    def __init__(self, log_file: str = "logs/game_events.log"):
        """Initialize game logger."""
        self.logger = logging.getLogger("trek.game_events")
        
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Create log directory
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # File handler for game events
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=5*1024*1024, backupCount=3
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_game_start(self, difficulty: str, seed: Optional[int] = None):
        """Log game start event."""
        seed_info = f" (seed: {seed})" if seed else ""
        self.logger.info(f"GAME_START - Difficulty: {difficulty}{seed_info}")
    
    def log_game_end(self, victory: bool, score: int, duration: float):
        """Log game end event."""
        result = "VICTORY" if victory else "DEFEAT"
        self.logger.info(f"GAME_END - {result} - Score: {score} - Duration: {duration:.1f}s")
    
    def log_combat(self, quadrant: tuple, weapon: str, damage: int, result: str):
        """Log combat event."""
        self.logger.info(f"COMBAT - Quadrant: {quadrant} - Weapon: {weapon} - Damage: {damage} - Result: {result}")
    
    def log_navigation(self, from_quadrant: tuple, to_quadrant: tuple, energy_cost: int):
        """Log navigation event."""
        self.logger.info(f"NAVIGATION - From: {from_quadrant} - To: {to_quadrant} - Energy: {energy_cost}")
    
    def log_docking(self, quadrant: tuple):
        """Log docking event."""
        self.logger.info(f"DOCKING - Quadrant: {quadrant}")
    
    def log_ai_action(self, ai_type: str, action: str, parameters: dict):
        """Log AI action."""
        self.logger.info(f"AI_ACTION - Type: {ai_type} - Action: {action} - Params: {parameters}")
    
    def log_system_damage(self, system: str, damage_level: float):
        """Log system damage."""
        self.logger.info(f"SYSTEM_DAMAGE - System: {system} - Damage: {damage_level:.2f}")
    
    def log_performance_metric(self, metric_name: str, value: float):
        """Log performance metric."""
        self.logger.info(f"PERFORMANCE - {metric_name}: {value:.3f}")


# Global game logger instance
game_logger = GameLogger()
