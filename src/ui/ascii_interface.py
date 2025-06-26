"""
ASCII Text Interface

This module provides a text-based interface for the Trek game,
similar to the original 1970s version but with enhanced features.
"""

import os
import sys
import time
from typing import Dict, List, Optional, Any
from utils.logger import get_logger


class ASCIIInterface:
    """
    ASCII text-based interface for the Trek game.
    
    Provides a classic terminal-based experience with modern enhancements
    like colored text, improved formatting, and comprehensive help system.
    """
    
    def __init__(self, game_engine):
        """Initialize the ASCII interface."""
        self.game_engine = game_engine
        self.logger = get_logger(__name__)
        
        # Interface settings
        self.use_colors = self._check_color_support()
        self.screen_width = 80
        self.command_history = []
        self.max_history = 50
        
        # Color codes (if supported)
        self.colors = {
            'red': '\033[91m' if self.use_colors else '',
            'green': '\033[92m' if self.use_colors else '',
            'yellow': '\033[93m' if self.use_colors else '',
            'blue': '\033[94m' if self.use_colors else '',
            'magenta': '\033[95m' if self.use_colors else '',
            'cyan': '\033[96m' if self.use_colors else '',
            'white': '\033[97m' if self.use_colors else '',
            'bold': '\033[1m' if self.use_colors else '',
            'reset': '\033[0m' if self.use_colors else ''
        }
        
        self.logger.info("ASCII interface initialized")
    
    def run(self):
        """Main interface loop."""
        try:
            self._display_welcome()
            self._display_initial_status()
            
            while not self.game_engine.game_over:
                try:
                    # Display prompt and get command
                    command_input = self._get_command_input()
                    
                    if not command_input.strip():
                        continue
                    
                    # Parse command
                    parts = command_input.strip().split()
                    command = parts[0].lower()
                    parameters = parts[1:] if len(parts) > 1 else []
                    
                    # Handle special interface commands
                    if command in ['quit', 'exit', 'q']:
                        if self._confirm_quit():
                            break
                        continue
                    elif command == 'help':
                        self._display_help(parameters)
                        continue
                    elif command == 'save':
                        self._handle_save_command(parameters)
                        continue
                    elif command == 'load':
                        self._handle_load_command(parameters)
                        continue
                    elif command == 'status':
                        self._display_detailed_status()
                        continue
                    elif command == 'map':
                        self._display_galaxy_map()
                        continue
                    elif command == 'history':
                        self._display_command_history()
                        continue
                    elif command == 'clear':
                        self._clear_screen()
                        continue
                    
                    # Process game command
                    result = self.game_engine.process_turn(command, parameters)
                    
                    # Display result
                    self._display_command_result(result)
                    
                    # Add to history
                    self._add_to_history(command_input)
                    
                    # Check for game end
                    if self.game_engine.game_over:
                        self._display_game_end()
                        break
                
                except KeyboardInterrupt:
                    print("\n" + self._colorize("Use 'quit' to exit the game.", 'yellow'))
                except Exception as e:
                    self.logger.error(f"Interface error: {e}", exc_info=True)
                    print(self._colorize(f"Error: {e}", 'red'))
        
        except Exception as e:
            self.logger.error(f"Fatal interface error: {e}", exc_info=True)
            print(self._colorize(f"Fatal error: {e}", 'red'))
        
        finally:
            self._display_goodbye()
    
    def _check_color_support(self) -> bool:
        """Check if terminal supports color output."""
        return (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and 
                os.environ.get('TERM', '').lower() != 'dumb')
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are supported."""
        if not self.use_colors or color not in self.colors:
            return text
        return f"{self.colors[color]}{text}{self.colors['reset']}"
    
    def _display_welcome(self):
        """Display welcome message and game banner."""
        self._clear_screen()
        
        # Define strings with backslashes outside f-string
        ship_line1 = "                      _.-'   '-._"
        ship_line2 = "                   .-'           '-."
        ship_line3 = "                  /                 \\"
        ship_line4 = "                 |    ___     ___    |"
        ship_line5 = "                 |   (   )   (   )   |"
        ship_line6 = "                  \\   '-'     '-'   /"
        ship_line7 = "                   '-.             .-'"
        ship_line8 = "                      '-._     _.-'"
        ship_line9 = "                          '---'"
        
        banner = f"""
{self._colorize('╔══════════════════════════════════════════════════════════════╗', 'cyan')}
{self._colorize('║                    AGENTIC TREK                              ║', 'cyan')}
{self._colorize('║                                                              ║', 'cyan')}
{self._colorize('║    A Modern Recreation of the Classic Space Strategy Game    ║', 'white')}
{self._colorize('║              Enhanced with Intelligent AI Agents            ║', 'white')}
{self._colorize('║                                                              ║', 'cyan')}
{self._colorize('║                     "Live Long and Prosper"                  ║', 'yellow')}
{self._colorize('╚══════════════════════════════════════════════════════════════╝', 'cyan')}

{self._colorize('         *           .               *                    .', 'white')}
{self._colorize('              .                 .            *', 'white')}
{self._colorize('    *                    .                        .           *', 'white')}
{self._colorize('         .        *                                    .', 'white')}
{self._colorize('                      USS ENTERPRISE NCC-1701', 'green')}
{self._colorize('                           ___', 'green')}
{self._colorize(ship_line1, 'green')}
{self._colorize(ship_line2, 'green')}
{self._colorize(ship_line3, 'green')}
{self._colorize(ship_line4, 'green')}
{self._colorize(ship_line5, 'green')}
{self._colorize(ship_line6, 'green')}
{self._colorize(ship_line7, 'green')}
{self._colorize(ship_line8, 'green')}
{self._colorize(ship_line9, 'green')}

{self._colorize('Type "help" for commands or "quit" to exit.', 'yellow')}
        """
        print(banner)
        try:
            input(self._colorize("Press Enter to begin your mission...", 'cyan'))
        except (EOFError, KeyboardInterrupt):
            # Handle EOF or Ctrl+C gracefully
            print("\n" + self._colorize("Starting mission...", 'cyan'))
    
    def _display_initial_status(self):
        """Display initial game status."""
        self._clear_screen()
        status = self.game_engine._get_status_report()
        
        print(self._colorize("=" * self.screen_width, 'cyan'))
        print(self._colorize("MISSION BRIEFING", 'bold').center(self.screen_width))
        print(self._colorize("=" * self.screen_width, 'cyan'))
        print()
        
        stardate = status["stardate"]
        time_remaining = status["time_remaining"]
        klingons_remaining = status["klingons_remaining"]
        starbases_remaining = status["starbases_remaining"]
        
        print(f"STARDATE: {self._colorize(f'{stardate:.1f}', 'white')}")
        print(f"MISSION TIME LIMIT: {self._colorize(f'{time_remaining:.1f}', 'yellow')} stardates")
        print(f"KLINGONS TO DESTROY: {self._colorize(str(klingons_remaining), 'red')}")
        print(f"STARBASES AVAILABLE: {self._colorize(str(starbases_remaining), 'green')}")
        print()
        
        print(self._colorize("SHIP STATUS:", 'bold'))
        print(f"  Energy: {self._colorize(str(status['energy']), 'green')}")
        print(f"  Shields: {self._colorize(str(status['shields']), 'blue')}")
        print(f"  Torpedoes: {self._colorize(str(status['torpedoes']), 'yellow')}")
        quadrant = f"{status['quadrant'][0]},{status['quadrant'][1]}"
        print(f"  Current Quadrant: {self._colorize(quadrant, 'white')}")
        print()
        
        print(self._colorize("Your mission: Destroy all Klingon ships before time runs out!", 'yellow'))
        print(self._colorize("Good luck, Captain!", 'green'))
        print()
    
    def _get_command_input(self) -> str:
        """Get command input from user with formatted prompt."""
        # Display current status line
        status = self.game_engine._get_status_report()
        condition_color = {
            'GREEN': 'green',
            'YELLOW': 'yellow',
            'RED': 'red'
        }.get(status['condition'], 'white')
        
        status_line = (f"STARDATE: {status['stardate']:.1f}    "
                      f"CONDITION: {self._colorize(status['condition'], condition_color)}    "
                      f"QUADRANT: {status['quadrant'][0]},{status['quadrant'][1]}")
        
        energy_line = (f"ENERGY: {self._colorize(str(status['energy']), 'green')}        "
                      f"SHIELDS: {self._colorize(str(status['shields']), 'blue')}       "
                      f"TORPEDOES: {self._colorize(str(status['torpedoes']), 'yellow')}")
        
        print(status_line)
        print(energy_line)
        print()
        
        prompt = self._colorize("COMMAND: ", 'cyan')
        
        try:
            return input(prompt)
        except EOFError:
            # Handle EOF gracefully (Ctrl+D or piped input ending)
            print("\n" + self._colorize("EOF detected. Exiting game...", 'yellow'))
            return "quit"
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n" + self._colorize("Game interrupted. Exiting...", 'yellow'))
            return "quit"
    
    def _display_command_result(self, result: Dict[str, Any]):
        """Display the result of a command."""
        print()
        
        if result['success']:
            if result['message']:
                print(self._colorize(result['message'], 'green'))
            
            # Display scan data if present
            if 'scan_data' in result:
                print()
                if isinstance(result['scan_data'], str):
                    print(result['scan_data'])
                else:
                    # Format scan data
                    self._display_scan_data(result['scan_data'])
            
            # Display status data if present
            if 'status_data' in result:
                self._display_status_data(result['status_data'])
            
            # Display damage data if present
            if 'damage_data' in result:
                self._display_damage_data(result['damage_data'])
            
            # Display events
            if result.get('events'):
                print()
                print(self._colorize("EVENTS:", 'yellow'))
                for event in result['events']:
                    print(f"  • {event}")
        
        else:
            print(self._colorize(f"ERROR: {result['message']}", 'red'))
        
        print()
    
    def _display_scan_data(self, scan_data):
        """Display sensor scan data."""
        if isinstance(scan_data, dict):
            # Long range scan data
            print(self._colorize("LONG RANGE SENSORS:", 'cyan'))
            print()
            for coords, (k, b, s) in scan_data.items():
                print(f"Quadrant {coords[0]},{coords[1]}: {k} Klingons, {b} Bases, {s} Stars")
        else:
            # Short range scan data (already formatted string)
            print(scan_data)
    
    def _display_status_data(self, status_data: Dict[str, Any]):
        """Display detailed status information."""
        print()
        print(self._colorize("DETAILED STATUS REPORT:", 'cyan'))
        print(self._colorize("-" * 40, 'cyan'))
        
        for key, value in status_data.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                print(f"{formatted_key}: {value:.2f}")
            else:
                print(f"{formatted_key}: {value}")
    
    def _display_damage_data(self, damage_data):
        """Display damage report."""
        print()
        print(self._colorize("DAMAGE REPORT:", 'yellow'))
        print(self._colorize("-" * 20, 'yellow'))
        
        if isinstance(damage_data, dict):
            for system, damage in damage_data.items():
                if damage > 0:
                    color = 'red' if damage > 0.5 else 'yellow'
                    print(f"{system}: {self._colorize(f'{damage:.1f}% damaged', color)}")
                else:
                    print(f"{system}: {self._colorize('Operational', 'green')}")
        else:
            print(damage_data)
    
    def _display_help(self, parameters: List[str]):
        """Display help information."""
        if not parameters:
            self._display_general_help()
        else:
            command = parameters[0].lower()
            self._display_command_help(command)
    
    def _display_general_help(self):
        """Display general help information."""
        help_text = f"""
{self._colorize('TREK COMMAND REFERENCE', 'bold').center(self.screen_width)}
{self._colorize('=' * self.screen_width, 'cyan')}

{self._colorize('NAVIGATION COMMANDS:', 'yellow')}
  nav <x,y>     - Navigate to quadrant x,y (e.g., "nav 3,4")
  
{self._colorize('SENSOR COMMANDS:', 'yellow')}
  srs           - Short range sensors (scan current quadrant)
  lrs           - Long range sensors (scan adjacent quadrants)
  
{self._colorize('COMBAT COMMANDS:', 'yellow')}
  pha <amount>  - Fire phasers with specified energy amount
  tor <course> <spread> - Fire photon torpedo (course 0-360, spread 1-10)
  shi <amount>  - Set shield level (uses energy)
  
{self._colorize('SHIP OPERATIONS:', 'yellow')}
  dock          - Dock with starbase (must be adjacent)
  dam           - Damage report
  com <function> - Computer functions (distance, course, status)
  
{self._colorize('INTERFACE COMMANDS:', 'yellow')}
  help [command] - Show help (general or for specific command)
  status        - Detailed status report
  map           - Display galaxy map
  save [name]   - Save current game
  load [name]   - Load saved game
  history       - Show command history
  clear         - Clear screen
  quit          - Exit game

{self._colorize('EXAMPLES:', 'green')}
  nav 2,3       - Navigate to quadrant 2,3
  pha 500       - Fire phasers with 500 energy units
  tor 45 3      - Fire torpedo at 45 degrees with spread of 3
  shi 1000      - Raise shields to 1000 units
  com distance 4,5 - Calculate distance to quadrant 4,5

{self._colorize('Type "help <command>" for detailed information about a specific command.', 'cyan')}
        """
        print(help_text)
    
    def _display_command_help(self, command: str):
        """Display help for a specific command."""
        help_data = {
            'nav': """
NAVIGATION (nav)
Navigate the Enterprise to a different quadrant.

Usage: nav <x,y>
  x,y = Quadrant coordinates (1-8)

Examples:
  nav 3,4    - Navigate to quadrant 3,4
  nav 1,1    - Navigate to quadrant 1,1

Energy cost depends on distance traveled.
            """,
            'srs': """
SHORT RANGE SENSORS (srs)
Scan the current quadrant for objects.

Usage: srs

Displays:
  E = Enterprise (your ship)
  K = Klingon ship
  B = Starbase
  * = Star
  . = Empty space
            """,
            'lrs': """
LONG RANGE SENSORS (lrs)
Scan adjacent quadrants for objects.

Usage: lrs

Shows a 3x3 grid centered on current quadrant.
Format: KBS (Klingons, Bases, Stars)
Example: "203" means 2 Klingons, 0 Bases, 3 Stars
            """,
            'pha': """
PHASERS (pha)
Fire phaser weapons at enemies in current quadrant.

Usage: pha <energy_amount>
  energy_amount = Energy units to use (1-3000)

Examples:
  pha 500    - Fire phasers with 500 energy
  pha 1000   - Fire phasers with 1000 energy

More energy = more damage, but uses ship's energy.
            """,
            'tor': """
PHOTON TORPEDOES (tor)
Fire photon torpedoes at specific targets.

Usage: tor <course> <spread>
  course = Direction in degrees (0-360)
  spread = Torpedo spread pattern (1-10)

Examples:
  tor 45 1   - Fire torpedo at 45 degrees, tight spread
  tor 180 5  - Fire torpedo at 180 degrees, wide spread

Limited ammunition - use wisely!
            """
        }
        
        if command in help_data:
            print(self._colorize(help_data[command], 'white'))
        else:
            print(self._colorize(f"No help available for command: {command}", 'yellow'))
    
    def _handle_save_command(self, parameters: List[str]):
        """Handle save game command."""
        if not parameters:
            filename = f"trek_save_{int(time.time())}.json"
        else:
            filename = parameters[0]
            if not filename.endswith('.json'):
                filename += '.json'
        
        if self.game_engine.save_game(filename):
            print(self._colorize(f"Game saved as: {filename}", 'green'))
        else:
            print(self._colorize("Failed to save game", 'red'))
    
    def _handle_load_command(self, parameters: List[str]):
        """Handle load game command."""
        if not parameters:
            print(self._colorize("Please specify a filename to load", 'yellow'))
            return
        
        filename = parameters[0]
        if not filename.endswith('.json'):
            filename += '.json'
        
        if self.game_engine.load_game(filename):
            print(self._colorize(f"Game loaded from: {filename}", 'green'))
            self._display_initial_status()
        else:
            print(self._colorize("Failed to load game", 'red'))
    
    def _display_detailed_status(self):
        """Display comprehensive status information."""
        status = self.game_engine._get_status_report()
        stats = self.game_engine.get_game_statistics()
        
        print()
        print(self._colorize("COMPREHENSIVE STATUS REPORT", 'bold').center(self.screen_width))
        print(self._colorize("=" * self.screen_width, 'cyan'))
        
        # Mission status
        print(self._colorize("MISSION STATUS:", 'yellow'))
        print(f"  Stardate: {status['stardate']:.1f}")
        print(f"  Time Remaining: {status['time_remaining']:.1f} stardates")
        print(f"  Condition: {self._colorize(status['condition'], 'green' if status['condition'] == 'GREEN' else 'yellow' if status['condition'] == 'YELLOW' else 'red')}")
        print()
        
        # Ship status
        print(self._colorize("SHIP STATUS:", 'yellow'))
        print(f"  Current Quadrant: {status['quadrant'][0]},{status['quadrant'][1]}")
        print(f"  Energy: {self._colorize(str(status['energy']), 'green')}")
        print(f"  Shields: {self._colorize(str(status['shields']), 'blue')}")
        print(f"  Torpedoes: {self._colorize(str(status['torpedoes']), 'yellow')}")
        print()
        
        # Mission progress
        print(self._colorize("MISSION PROGRESS:", 'yellow'))
        print(f"  Klingons Remaining: {self._colorize(str(status['klingons_remaining']), 'red')}")
        print(f"  Starbases Available: {self._colorize(str(status['starbases_remaining']), 'green')}")
        print(f"  Quadrants Visited: {status['quadrants_visited']}/64")
        print(f"  Combat Encounters: {status['combat_encounters']}")
        print()
        
        # Performance statistics
        print(self._colorize("PERFORMANCE STATISTICS:", 'yellow'))
        print(f"  Play Time: {stats['play_time_seconds']:.0f} seconds")
        print(f"  Turns Played: {stats['turns_played']}")
        print(f"  Energy Used: {stats['total_energy_used']}")
        print(f"  Torpedoes Fired: {stats['total_torpedoes_fired']}")
        print(f"  Efficiency Rating: {stats['efficiency_rating']:.2f}")
        print()
    
    def _display_galaxy_map(self):
        """Display the galaxy map."""
        print()
        galaxy_map = self.game_engine.galaxy.get_galaxy_map_display(self.game_engine.ship.current_quadrant)
        print(galaxy_map)
        print()
    
    def _display_command_history(self):
        """Display command history."""
        print()
        print(self._colorize("COMMAND HISTORY:", 'cyan'))
        print(self._colorize("-" * 20, 'cyan'))
        
        if not self.command_history:
            print("No commands in history")
        else:
            for i, cmd in enumerate(self.command_history[-10:], 1):  # Show last 10
                print(f"{i:2d}. {cmd}")
        print()
    
    def _add_to_history(self, command: str):
        """Add command to history."""
        self.command_history.append(command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _confirm_quit(self) -> bool:
        """Confirm quit with user."""
        try:
            response = input(self._colorize("Are you sure you want to quit? (y/N): ", 'yellow'))
            return response.lower().startswith('y')
        except (EOFError, KeyboardInterrupt):
            # If EOF or interrupt, assume they want to quit
            print("\n" + self._colorize("Confirming quit...", 'yellow'))
            return True
    
    def _display_game_end(self):
        """Display game end message."""
        print()
        print(self._colorize("=" * self.screen_width, 'cyan'))
        
        if self.game_engine.victory:
            print(self._colorize("VICTORY!", 'green').center(self.screen_width))
            print()
            print(self._colorize("Congratulations, Captain!", 'green').center(self.screen_width))
            print(self._colorize("You have successfully completed your mission.", 'white').center(self.screen_width))
            print(self._colorize("All Klingon ships have been destroyed!", 'green').center(self.screen_width))
        else:
            print(self._colorize("MISSION FAILED", 'red').center(self.screen_width))
            print()
            if self.game_engine.ship.is_destroyed():
                print(self._colorize("The Enterprise has been destroyed.", 'red').center(self.screen_width))
            else:
                print(self._colorize("Time has run out for your mission.", 'red').center(self.screen_width))
            print(self._colorize("Better luck next time, Captain.", 'yellow').center(self.screen_width))
        
        print(self._colorize("=" * self.screen_width, 'cyan'))
        
        # Display final statistics
        stats = self.game_engine.get_game_statistics()
        status = self.game_engine._get_status_report()
        
        print()
        print(self._colorize("FINAL STATISTICS:", 'yellow'))
        print(f"  Final Score: {status['score']}")
        print(f"  Play Time: {stats['play_time_seconds']:.0f} seconds")
        print(f"  Turns Played: {stats['turns_played']}")
        print(f"  Quadrants Visited: {status['quadrants_visited']}/64")
        print(f"  Combat Encounters: {status['combat_encounters']}")
        print(f"  Efficiency Rating: {stats['efficiency_rating']:.2f}")
        print()
    
    def _display_goodbye(self):
        """Display goodbye message."""
        print()
        print(self._colorize("Thank you for playing Agentic Trek!", 'cyan'))
        print(self._colorize("Live long and prosper! 🖖", 'green'))
        print()
