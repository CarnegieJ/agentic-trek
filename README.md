# Agentic Trek - A Modern Reimagining of the Classic Space Strategy Game

<!-- ![Trek Game Banner](assets/images/trek_banner.png) -->
<!-- Banner image placeholder - see assets/images/trek_banner.png for instructions -->

## Overview

Agentic Trek is a modern recreation of the classic 1970s Trek game, enhanced with sophisticated AI agents that provide dynamic, intelligent gameplay. Originally played on VAX computers, this version brings the strategic depth of space exploration and combat into the modern era with pygame and advanced AI decision-making systems.

```
    * * * GALACTIC MAP * * *
    
    1   2   3   4   5   6   7   8
  +---+---+---+---+---+---+---+---+
1 | . | K | . | * | . | . | K | . |
  +---+---+---+---+---+---+---+---+
2 | . | . | B | . | . | K | . | . |
  +---+---+---+---+---+---+---+---+
3 | K | . | . | . | . | . | . | * |
  +---+---+---+---+---+---+---+---+
4 | . | . | . | E | . | . | . | . |
  +---+---+---+---+---+---+---+---+
5 | . | * | . | . | . | . | B | . |
  +---+---+---+---+---+---+---+---+
6 | . | . | . | . | K | . | . | . |
  +---+---+---+---+---+---+---+---+
7 | . | . | K | . | . | . | . | . |
  +---+---+---+---+---+---+---+---+
8 | B | . | . | . | . | * | . | . |
  +---+---+---+---+---+---+---+---+

Legend: E=Enterprise, K=Klingon, B=Starbase, *=Star, .=Empty
```

## Features

### Core Game Mechanics
- **Galaxy Exploration**: Navigate through an 8x8 galaxy grid with 64 quadrants
- **Strategic Combat**: Engage Klingon vessels with phasers and photon torpedoes
- **Resource Management**: Monitor energy, shields, and torpedo supplies
- **Starbase Operations**: Dock for repairs, refueling, and resupply
- **Time Pressure**: Complete missions within stardate limits

### AI Agent System
- **Adaptive Klingon AI**: Dynamic combat strategies that learn from player behavior
- **Strategic Planning Agent**: Optimal route planning and resource allocation
- **Difficulty Scaling**: AI adjusts challenge level based on player performance
- **Behavioral Analysis**: AI observes and adapts to player patterns
- **Event Generation**: Dynamic mission events based on game state

### Technical Features
- **Dual Display Modes**: ASCII terminal mode and pygame graphical interface
- **Save/Load System**: Persistent game state with multiple save slots
- **Replay System**: Record and analyze gameplay sessions
- **Performance Metrics**: Detailed statistics and performance tracking
- **Modular Architecture**: Extensible plugin system for new features

## Technology Stack

- **Platform**: Windows 11 with WSL Ubuntu 22.04
- **Language**: Python 3.10.12
- **Graphics**: pygame 2.6.1 (SDL 2.28.4)
- **AI Framework**: Custom multi-agent system with decision trees
- **Version Control**: Git with comprehensive branching strategy
- **Testing**: pytest with coverage reporting
- **Documentation**: Sphinx with automated API docs

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Game Application Layer                     │
├───────────────────────────────────────────────────────────────┤
│  UI Layer          │  Game Logic Layer    │  AI Agent Layer   │
│  ┌─────────────┐   │  ┌──────────────┐    │ ┌─────────────┐   │
│  │ ASCII UI    │   │  │ Game Engine  │    │ │ Klingon AI  │   │
│  │ pygame UI   │   │  │ Combat Sys   │    │ │ Strategy AI │   │
│  │ Input Mgr   │   │  │ Navigation   │    │ │ Adaptive AI │   │
│  └─────────────┘   │  │ Resources    │    │ └─────────────┘   │
│                    │  └──────────────┘    │                   │ 
│                    │                      │                   │
├────────────────────┼──────────────────────┼───────────────────┤
│                Data Layer                 │  AI Data Layer    │
│  ┌─────────────────────────────────────┐  │  ┌─────────────┐  │
│  │ Game State, Galaxy Map, Ship Data   │  │  │ Behavior    │  │
│  │ Save/Load, Configuration            │  │  │ Learning    │  │
│  └─────────────────────────────────────┘  │  │ Analytics   │  │
│                                           │  └─────────────┘  │
└───────────────────────────────────────────┴───────────────────┘
```

## Installation

### Prerequisites
- Windows 11 with WSL2 enabled
- Ubuntu 22.04 LTS installed in WSL
- Python 3.10.12 or higher
- Git for version control

### Setup Instructions

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/agentic-trek.git
cd agentic-trek
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the game**:
```bash
python src/main.py
```

## Game Controls

### ASCII Mode Commands
- `nav <quadrant>` - Navigate to specified quadrant (e.g., "nav 3,4")
- `srs` - Short range sensors (local quadrant scan)
- `lrs` - Long range sensors (adjacent quadrant scan)
- `pha <amount>` - Fire phasers with specified energy
- `tor <course> <spread>` - Fire photon torpedo
- `shi <amount>` - Raise/lower shields
- `dock` - Dock with starbase (when adjacent)
- `com` - Computer functions and calculations
- `dam` - Damage report
- `quit` - Exit game

### Pygame Mode Controls
- **Mouse**: Click to select targets and navigate
- **Keyboard**: Arrow keys for movement, spacebar for actions
- **ESC**: Pause menu
- **F1**: Help system

## AI Agent Behaviors

### Klingon Combat AI
- **Aggressive**: Direct attacks with maximum firepower
- **Defensive**: Evasive maneuvers and shield management
- **Tactical**: Coordinated multi-ship attacks
- **Adaptive**: Learns from player combat patterns

### Strategic Planning AI
- **Route Optimization**: Calculates efficient travel paths
- **Resource Prediction**: Anticipates supply needs
- **Threat Assessment**: Evaluates danger levels
- **Mission Planning**: Suggests optimal strategies

## Development Roadmap

### Version 1.0 - Core Game (Current)
- [x] Basic game engine and mechanics
- [x] ASCII interface implementation
- [x] Simple AI opponents
- [ ] Save/load functionality
- [ ] Basic pygame interface

### Version 1.1 - Enhanced AI
- [ ] Advanced Klingon AI behaviors
- [ ] Strategic planning agent
- [ ] Adaptive difficulty system
- [ ] Player behavior analysis

### Version 1.2 - Polish & Features
- [ ] Complete pygame interface
- [ ] Replay system
- [ ] Performance analytics
- [ ] Comprehensive help system

### Version 2.0 - Advanced Features
- [ ] Multiplayer support
- [ ] Custom scenarios
- [ ] Mod support
- [ ] Advanced AI learning

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Testing

Run the test suite:
```bash
pytest tests/ -v --coverage
```

## Performance Metrics

The game tracks various performance metrics:
- **Decision Time**: AI response times
- **Win/Loss Ratios**: Player success rates
- **Resource Efficiency**: Optimal resource usage
- **Combat Effectiveness**: Battle performance statistics

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original Trek game creators from the 1970s
- pygame community for excellent documentation
- AI research community for decision-making algorithms
- Classic computer gaming preservation efforts

## Screenshots

### ASCII Mode
```
STARDATE: 2267.3    CONDITION: GREEN    QUADRANT: 1,1
ENERGY: 3000        SHIELDS: 1500       TORPEDOES: 10

     1   2   3   4   5   6   7   8
   +---+---+---+---+---+---+---+---+
 1 | E | . | . | K | . | . | . | * |
   +---+---+---+---+---+---+---+---+
 2 | . | . | . | . | . | . | . | . |
   +---+---+---+---+---+---+---+---+

COMMAND: _
```

### Pygame Mode
<!-- ![Pygame Interface](assets/images/pygame_interface.png) -->
*Screenshot placeholder - Run `python src/main.py` to see the pygame interface*

The pygame interface features:
- **Visual Quadrant Display**: Click-to-navigate galaxy map
- **Real-time Status Panel**: Ship systems and mission progress
- **Interactive Controls**: Mouse and keyboard input
- **Multiple Views**: Main game, galaxy map (F2), help screen (F1)

## Contact

For questions, suggestions, or bug reports, please open an issue on GitHub.

---
*"Space: the final frontier. These are the voyages of the starship Enterprise..."*
