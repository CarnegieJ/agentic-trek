"""
Pygame Graphical Interface

This module provides a modern graphical interface using pygame
for enhanced visual gameplay experience.
"""

import pygame
import sys
from typing import Dict, List, Optional, Any, Tuple
from utils.logger import get_logger


class PygameInterface:
    """
    Pygame-based graphical interface for the Trek game.
    
    Provides a modern visual experience with mouse and keyboard controls,
    animations, and enhanced graphics while maintaining the classic gameplay.
    """
    
    def __init__(self, game_engine):
        """Initialize the pygame interface."""
        self.game_engine = game_engine
        self.logger = get_logger(__name__)
        
        # Initialize pygame
        pygame.init()
        
        # Display settings
        self.window_width = self.game_engine.config.get('interface.pygame.window_width', 1024)
        self.window_height = self.game_engine.config.get('interface.pygame.window_height', 768)
        self.fps = self.game_engine.config.get('interface.pygame.fps', 60)
        self.fullscreen = self.game_engine.config.get('interface.pygame.fullscreen', False)
        
        # Create display
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), flags)
        pygame.display.set_caption("Agentic Trek")
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Colors
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
            'dark_gray': (64, 64, 64),
            'light_gray': (192, 192, 192),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'brown': (165, 42, 42),
            'pink': (255, 192, 203),
            'lime': (0, 255, 0),
            'navy': (0, 0, 128),
            'teal': (0, 128, 128),
            'silver': (192, 192, 192),
            'gold': (255, 215, 0)
        }
        
        # Fonts
        try:
            self.font_large = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        except:
            # Fallback to default font
            self.font_large = pygame.font.SysFont('arial', 36)
            self.font_medium = pygame.font.SysFont('arial', 24)
            self.font_small = pygame.font.SysFont('arial', 18)
        
        # Game state
        self.running = True
        self.current_view = 'main_game'  # main_game, galaxy_map, help, etc.
        self.selected_quadrant = None
        self.mouse_pos = (0, 0)
        
        # UI layout
        self.setup_ui_layout()
        
        self.logger.info(f"Pygame interface initialized: {self.window_width}x{self.window_height}")
    
    def setup_ui_layout(self):
        """Set up UI layout and regions."""
        # Main game area (left side)
        self.game_area = pygame.Rect(10, 10, 600, 600)
        
        # Status panel (right side)
        self.status_panel = pygame.Rect(620, 10, 390, 300)
        
        # Command panel (bottom right)
        self.command_panel = pygame.Rect(620, 320, 390, 200)
        
        # Message log (bottom)
        self.message_log = pygame.Rect(10, 620, 1000, 140)
        
        # Button areas
        self.button_areas = {
            'nav': pygame.Rect(630, 330, 80, 30),
            'srs': pygame.Rect(720, 330, 80, 30),
            'lrs': pygame.Rect(810, 330, 80, 30),
            'pha': pygame.Rect(630, 370, 80, 30),
            'tor': pygame.Rect(720, 370, 80, 30),
            'shi': pygame.Rect(810, 370, 80, 30),
            'dock': pygame.Rect(630, 410, 80, 30),
            'dam': pygame.Rect(720, 410, 80, 30),
            'help': pygame.Rect(810, 410, 80, 30),
            'quit': pygame.Rect(900, 410, 80, 30)
        }
        
        # Message history
        self.messages = []
        self.max_messages = 8
    
    def run(self):
        """Main interface loop."""
        try:
            self.display_welcome_screen()
            
            while self.running and not self.game_engine.game_over:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(self.fps)
            
            if self.game_engine.game_over:
                self.display_game_end_screen()
        
        except Exception as e:
            self.logger.error(f"Pygame interface error: {e}", exc_info=True)
        
        finally:
            pygame.quit()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
    
    def handle_keydown(self, event):
        """Handle keyboard input."""
        if event.key == pygame.K_ESCAPE:
            self.running = False
        
        elif event.key == pygame.K_F1:
            self.current_view = 'help'
        
        elif event.key == pygame.K_F2:
            self.current_view = 'galaxy_map'
        
        elif event.key == pygame.K_F3:
            self.current_view = 'main_game'
        
        elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Ctrl+S to save
            self.save_game()
    
    def handle_mouse_click(self, event):
        """Handle mouse clicks."""
        if event.button == 1:  # Left click
            # Check button clicks
            for button_name, button_rect in self.button_areas.items():
                if button_rect.collidepoint(event.pos):
                    self.handle_button_click(button_name)
                    return
            
            # Check quadrant selection in game area
            if self.game_area.collidepoint(event.pos):
                self.handle_quadrant_click(event.pos)
    
    def handle_button_click(self, button_name: str):
        """Handle button clicks."""
        if button_name == 'quit':
            self.running = False
        
        elif button_name == 'help':
            self.current_view = 'help'
        
        elif button_name == 'srs':
            result = self.game_engine.process_turn('srs')
            self.add_message(result['message'])
        
        elif button_name == 'lrs':
            result = self.game_engine.process_turn('lrs')
            self.add_message(result['message'])
        
        elif button_name == 'dam':
            result = self.game_engine.process_turn('dam')
            self.add_message("Damage report generated")
        
        elif button_name == 'dock':
            result = self.game_engine.process_turn('dock')
            self.add_message(result['message'])
        
        # Add more button handlers as needed
        self.logger.debug(f"Button clicked: {button_name}")
    
    def handle_quadrant_click(self, pos: Tuple[int, int]):
        """Handle clicks in the game area."""
        # Convert screen coordinates to quadrant coordinates
        relative_x = pos[0] - self.game_area.x
        relative_y = pos[1] - self.game_area.y
        
        # Calculate quadrant (simplified)
        quadrant_x = int((relative_x / self.game_area.width) * 8) + 1
        quadrant_y = int((relative_y / self.game_area.height) * 8) + 1
        
        if 1 <= quadrant_x <= 8 and 1 <= quadrant_y <= 8:
            self.selected_quadrant = (quadrant_x, quadrant_y)
            
            # Navigate to selected quadrant
            result = self.game_engine.process_turn('nav', [f"{quadrant_x},{quadrant_y}"])
            self.add_message(result['message'])
    
    def update(self):
        """Update game state."""
        # Update any animations or time-based changes here
        pass
    
    def draw(self):
        """Draw the current frame."""
        self.screen.fill(self.colors['black'])
        
        if self.current_view == 'main_game':
            self.draw_main_game()
        elif self.current_view == 'galaxy_map':
            self.draw_galaxy_map()
        elif self.current_view == 'help':
            self.draw_help_screen()
        
        pygame.display.flip()
    
    def draw_main_game(self):
        """Draw the main game interface."""
        # Draw game area border
        pygame.draw.rect(self.screen, self.colors['white'], self.game_area, 2)
        
        # Draw current quadrant
        self.draw_current_quadrant()
        
        # Draw status panel
        self.draw_status_panel()
        
        # Draw command panel
        self.draw_command_panel()
        
        # Draw message log
        self.draw_message_log()
    
    def draw_current_quadrant(self):
        """Draw the current quadrant view."""
        # Get current quadrant data
        quadrant_data = self.game_engine.galaxy.get_quadrant_data(
            self.game_engine.ship.current_quadrant
        )
        
        # Draw quadrant grid
        cell_width = self.game_area.width // 8
        cell_height = self.game_area.height // 8
        
        for x in range(8):
            for y in range(8):
                cell_rect = pygame.Rect(
                    self.game_area.x + x * cell_width,
                    self.game_area.y + y * cell_height,
                    cell_width,
                    cell_height
                )
                
                # Draw cell border
                pygame.draw.rect(self.screen, self.colors['gray'], cell_rect, 1)
                
                # Draw objects in cell
                pos = (x + 1, y + 1)
                
                if pos == self.game_engine.ship.quadrant_position:
                    # Draw Enterprise
                    self.draw_enterprise(cell_rect)
                elif pos in quadrant_data:
                    obj_type = quadrant_data[pos]
                    self.draw_space_object(cell_rect, obj_type)
    
    def draw_enterprise(self, rect: pygame.Rect):
        """Draw the Enterprise."""
        center = rect.center
        pygame.draw.circle(self.screen, self.colors['green'], center, 8)
        
        # Draw simple ship shape
        points = [
            (center[0], center[1] - 10),
            (center[0] - 6, center[1] + 8),
            (center[0] + 6, center[1] + 8)
        ]
        pygame.draw.polygon(self.screen, self.colors['white'], points)
        
        # Draw "E" label
        text = self.font_small.render("E", True, self.colors['white'])
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
    
    def draw_space_object(self, rect: pygame.Rect, obj_type: str):
        """Draw a space object."""
        center = rect.center
        
        if obj_type == 'K':  # Klingon
            pygame.draw.circle(self.screen, self.colors['red'], center, 6)
            text = self.font_small.render("K", True, self.colors['white'])
        elif obj_type == 'B':  # Starbase
            pygame.draw.rect(self.screen, self.colors['blue'], 
                           (center[0] - 6, center[1] - 6, 12, 12))
            text = self.font_small.render("B", True, self.colors['white'])
        elif obj_type == '*':  # Star
            pygame.draw.circle(self.screen, self.colors['yellow'], center, 4)
            text = self.font_small.render("*", True, self.colors['black'])
        else:
            return
        
        text_rect = text.get_rect(center=center)
        self.screen.blit(text, text_rect)
    
    def draw_status_panel(self):
        """Draw the status panel."""
        pygame.draw.rect(self.screen, self.colors['dark_gray'], self.status_panel)
        pygame.draw.rect(self.screen, self.colors['white'], self.status_panel, 2)
        
        # Get status data
        status = self.game_engine._get_status_report()
        
        y_offset = self.status_panel.y + 10
        line_height = 25
        
        # Status title
        title = self.font_medium.render("SHIP STATUS", True, self.colors['white'])
        self.screen.blit(title, (self.status_panel.x + 10, y_offset))
        y_offset += line_height + 10
        
        # Status lines
        status_lines = [
            f"Stardate: {status['stardate']:.1f}",
            f"Condition: {status['condition']}",
            f"Quadrant: {status['quadrant'][0]},{status['quadrant'][1]}",
            f"Energy: {status['energy']}",
            f"Shields: {status['shields']}",
            f"Torpedoes: {status['torpedoes']}",
            f"Klingons: {status['klingons_remaining']}",
            f"Starbases: {status['starbases_remaining']}"
        ]
        
        for line in status_lines:
            # Choose color based on content
            color = self.colors['white']
            if 'Condition:' in line:
                if 'RED' in line:
                    color = self.colors['red']
                elif 'YELLOW' in line:
                    color = self.colors['yellow']
                elif 'GREEN' in line:
                    color = self.colors['green']
            
            text = self.font_small.render(line, True, color)
            self.screen.blit(text, (self.status_panel.x + 10, y_offset))
            y_offset += line_height
    
    def draw_command_panel(self):
        """Draw the command panel with buttons."""
        pygame.draw.rect(self.screen, self.colors['dark_gray'], self.command_panel)
        pygame.draw.rect(self.screen, self.colors['white'], self.command_panel, 2)
        
        # Command title
        title = self.font_medium.render("COMMANDS", True, self.colors['white'])
        self.screen.blit(title, (self.command_panel.x + 10, self.command_panel.y + 10))
        
        # Draw buttons
        for button_name, button_rect in self.button_areas.items():
            # Button background
            button_color = self.colors['gray']
            if button_rect.collidepoint(self.mouse_pos):
                button_color = self.colors['light_gray']
            
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, self.colors['white'], button_rect, 1)
            
            # Button text
            text = self.font_small.render(button_name.upper(), True, self.colors['black'])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_message_log(self):
        """Draw the message log."""
        pygame.draw.rect(self.screen, self.colors['dark_gray'], self.message_log)
        pygame.draw.rect(self.screen, self.colors['white'], self.message_log, 2)
        
        # Message title
        title = self.font_medium.render("MESSAGES", True, self.colors['white'])
        self.screen.blit(title, (self.message_log.x + 10, self.message_log.y + 10))
        
        # Draw messages
        y_offset = self.message_log.y + 35
        line_height = 16
        
        for message in self.messages[-self.max_messages:]:
            text = self.font_small.render(message, True, self.colors['white'])
            self.screen.blit(text, (self.message_log.x + 10, y_offset))
            y_offset += line_height
    
    def draw_galaxy_map(self):
        """Draw the galaxy map view."""
        # Title
        title = self.font_large.render("GALACTIC MAP", True, self.colors['white'])
        title_rect = title.get_rect(center=(self.window_width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Draw galaxy grid
        grid_size = 400
        grid_x = (self.window_width - grid_size) // 2
        grid_y = 100
        cell_size = grid_size // 8
        
        current_quadrant = self.game_engine.ship.current_quadrant
        
        for x in range(8):
            for y in range(8):
                cell_rect = pygame.Rect(
                    grid_x + x * cell_size,
                    grid_y + y * cell_size,
                    cell_size,
                    cell_size
                )
                
                quadrant_coords = (x + 1, y + 1)
                
                # Cell background
                if quadrant_coords == current_quadrant:
                    pygame.draw.rect(self.screen, self.colors['green'], cell_rect)
                else:
                    pygame.draw.rect(self.screen, self.colors['dark_gray'], cell_rect)
                
                pygame.draw.rect(self.screen, self.colors['white'], cell_rect, 1)
                
                # Quadrant contents
                k, b, s = self.game_engine.galaxy.get_quadrant_summary(quadrant_coords)
                
                # Draw indicators
                center = cell_rect.center
                if k > 0:
                    pygame.draw.circle(self.screen, self.colors['red'], 
                                     (center[0] - 10, center[1]), 3)
                if b > 0:
                    pygame.draw.rect(self.screen, self.colors['blue'],
                                   (center[0] - 3, center[1] - 10, 6, 6))
                if s > 0:
                    pygame.draw.circle(self.screen, self.colors['yellow'],
                                     (center[0] + 10, center[1]), 2)
                
                # Quadrant coordinates
                coord_text = self.font_small.render(f"{x+1},{y+1}", True, self.colors['white'])
                self.screen.blit(coord_text, (cell_rect.x + 2, cell_rect.y + 2))
        
        # Legend
        legend_y = grid_y + grid_size + 20
        legend_items = [
            ("Red circle: Klingons", self.colors['red']),
            ("Blue square: Starbases", self.colors['blue']),
            ("Yellow circle: Stars", self.colors['yellow']),
            ("Green background: Current location", self.colors['green'])
        ]
        
        for i, (text, color) in enumerate(legend_items):
            legend_text = self.font_small.render(text, True, color)
            self.screen.blit(legend_text, (grid_x, legend_y + i * 20))
        
        # Instructions
        instruction = self.font_small.render("Press F3 to return to main game", True, self.colors['white'])
        instruction_rect = instruction.get_rect(center=(self.window_width // 2, self.window_height - 30))
        self.screen.blit(instruction, instruction_rect)
    
    def draw_help_screen(self):
        """Draw the help screen."""
        # Title
        title = self.font_large.render("HELP - AGENTIC TREK", True, self.colors['white'])
        title_rect = title.get_rect(center=(self.window_width // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Help content
        help_lines = [
            "MOUSE CONTROLS:",
            "• Click quadrants to navigate",
            "• Click buttons to execute commands",
            "",
            "KEYBOARD SHORTCUTS:",
            "• ESC - Quit game",
            "• F1 - Help screen",
            "• F2 - Galaxy map",
            "• F3 - Main game",
            "• Ctrl+S - Save game",
            "",
            "GAME OBJECTIVE:",
            "• Destroy all Klingon ships",
            "• Complete mission before time runs out",
            "• Use starbases to repair and resupply",
            "",
            "COMMANDS:",
            "• NAV - Navigate to quadrant",
            "• SRS - Short range sensors",
            "• LRS - Long range sensors",
            "• PHA - Fire phasers",
            "• TOR - Fire torpedoes",
            "• SHI - Control shields",
            "• DOCK - Dock with starbase",
            "• DAM - Damage report"
        ]
        
        y_offset = 100
        line_height = 20
        
        for line in help_lines:
            if line.endswith(":"):
                color = self.colors['yellow']
                font = self.font_medium
            elif line.startswith("•"):
                color = self.colors['white']
                font = self.font_small
            else:
                color = self.colors['cyan']
                font = self.font_small
            
            text = font.render(line, True, color)
            self.screen.blit(text, (50, y_offset))
            y_offset += line_height
        
        # Instructions
        instruction = self.font_small.render("Press F3 to return to main game", True, self.colors['white'])
        instruction_rect = instruction.get_rect(center=(self.window_width // 2, self.window_height - 30))
        self.screen.blit(instruction, instruction_rect)
    
    def display_welcome_screen(self):
        """Display welcome screen."""
        welcome_shown = False
        
        while not welcome_shown:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    welcome_shown = True
            
            self.screen.fill(self.colors['black'])
            
            # Title
            title = self.font_large.render("AGENTIC TREK", True, self.colors['cyan'])
            title_rect = title.get_rect(center=(self.window_width // 2, 200))
            self.screen.blit(title, title_rect)
            
            # Subtitle
            subtitle = self.font_medium.render("A Modern Recreation of the Classic Space Strategy Game", 
                                             True, self.colors['white'])
            subtitle_rect = subtitle.get_rect(center=(self.window_width // 2, 250))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Instructions
            instruction = self.font_small.render("Press any key or click to begin your mission...", 
                                                True, self.colors['yellow'])
            instruction_rect = instruction.get_rect(center=(self.window_width // 2, 400))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def display_game_end_screen(self):
        """Display game end screen."""
        end_shown = False
        
        while not end_shown and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    end_shown = True
            
            self.screen.fill(self.colors['black'])
            
            # Result
            if self.game_engine.victory:
                result_text = "VICTORY!"
                result_color = self.colors['green']
                message = "Congratulations, Captain! Mission accomplished!"
            else:
                result_text = "MISSION FAILED"
                result_color = self.colors['red']
                message = "Better luck next time, Captain."
            
            result = self.font_large.render(result_text, True, result_color)
            result_rect = result.get_rect(center=(self.window_width // 2, 200))
            self.screen.blit(result, result_rect)
            
            msg = self.font_medium.render(message, True, self.colors['white'])
            msg_rect = msg.get_rect(center=(self.window_width // 2, 250))
            self.screen.blit(msg, msg_rect)
            
            # Statistics
            stats = self.game_engine.get_game_statistics()
            status = self.game_engine._get_status_report()
            
            stats_lines = [
                f"Final Score: {status['score']}",
                f"Play Time: {stats['play_time_seconds']:.0f} seconds",
                f"Turns Played: {stats['turns_played']}",
                f"Quadrants Visited: {status['quadrants_visited']}/64",
                f"Efficiency Rating: {stats['efficiency_rating']:.2f}"
            ]
            
            y_offset = 320
            for line in stats_lines:
                text = self.font_small.render(line, True, self.colors['white'])
                text_rect = text.get_rect(center=(self.window_width // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 25
            
            # Instructions
            instruction = self.font_small.render("Press any key to exit", True, self.colors['yellow'])
            instruction_rect = instruction.get_rect(center=(self.window_width // 2, 500))
            self.screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def add_message(self, message: str):
        """Add a message to the message log."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages * 2:
            self.messages = self.messages[-self.max_messages:]
    
    def save_game(self):
        """Save the current game."""
        import time
        filename = f"trek_save_{int(time.time())}.json"
        if self.game_engine.save_game(filename):
            self.add_message(f"Game saved as: {filename}")
        else:
            self.add_message("Failed to save game")
