# Contributing to Agentic Trek

Thank you for your interest in contributing to Agentic Trek! This document provides guidelines and information for contributors to help maintain code quality and project consistency.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [AI Development Guidelines](#ai-development-guidelines)
- [Performance Considerations](#performance-considerations)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:

- **Be respectful**: Treat all community members with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together constructively and share knowledge
- **Be professional**: Keep discussions focused on technical matters
- **Be patient**: Remember that everyone has different skill levels and backgrounds

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git for version control
- Basic understanding of game development concepts
- Familiarity with AI/ML concepts (for AI-related contributions)

### First-Time Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/agentic-trek.git
   cd agentic-trek
   ```
3. **Set up the development environment** (see Development Setup below)
4. **Look for "good first issue" labels** in the issue tracker
5. **Join our discussions** in GitHub Discussions

## Development Setup

### Environment Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Verify installation**:
   ```bash
   python src/main.py --help
   pytest tests/ -v
   ```

### Development Dependencies

Create a `requirements-dev.txt` file with additional development tools:

```
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code Quality
black>=23.7.0
flake8>=6.0.0
mypy>=1.5.1
isort>=5.12.0

# Documentation
sphinx>=7.1.2
sphinx-rtd-theme>=1.3.0

# Development Tools
pre-commit>=3.3.0
tox>=4.6.0
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix existing issues and improve stability
- **New features**: Add new game mechanics, AI behaviors, or interfaces
- **AI improvements**: Enhance existing AI agents or create new ones
- **Performance optimizations**: Improve game performance and efficiency
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Translations**: Add support for different languages
- **Art assets**: Contribute graphics, sounds, or other media

### Contribution Workflow

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** for new features or significant changes
3. **Fork and branch**: Create a feature branch from `main`
4. **Develop**: Make your changes following our coding standards
5. **Test**: Ensure all tests pass and add new tests as needed
6. **Document**: Update documentation for your changes
7. **Submit**: Create a pull request with a clear description

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feature/add-multiplayer-support`
- `bugfix/fix-energy-calculation`
- `ai/improve-klingon-tactics`
- `docs/update-api-documentation`
- `test/add-combat-system-tests`
- `refactor/simplify-galaxy-generation`

## Code Standards

### Python Style Guide

We follow PEP 8 with some project-specific conventions:

#### Code Formatting

- **Line length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **String quotes**: Use double quotes for strings, single quotes for character literals
- **Import organization**: Use `isort` for consistent import ordering

#### Naming Conventions

```python
# Classes: PascalCase
class KlingonAI:
    pass

# Functions and variables: snake_case
def calculate_damage(weapon_power: int) -> int:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_ENERGY = 3000

# Private methods: leading underscore
def _internal_calculation(self) -> float:
    pass
```

#### Type Hints

Use type hints for all public functions and class methods:

```python
from typing import Dict, List, Optional, Tuple, Any

def process_command(command: str, parameters: List[str]) -> Dict[str, Any]:
    """Process a game command and return results."""
    pass

class Ship:
    def take_damage(self, damage: int) -> int:
        """Apply damage and return actual damage taken."""
        pass
```

#### Documentation Strings

Use Google-style docstrings:

```python
def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Calculate distance between two positions.
    
    Args:
        pos1: First position as (x, y) coordinates
        pos2: Second position as (x, y) coordinates
        
    Returns:
        Distance as a float value
        
    Raises:
        ValueError: If coordinates are invalid
        
    Example:
        >>> calculate_distance((1, 1), (4, 5))
        5.0
    """
    pass
```

### Code Quality Tools

Run these tools before submitting:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for system interactions
├── ai/            # AI-specific tests and behavior validation
├── performance/   # Performance and benchmark tests
└── fixtures/      # Test data and fixtures
```

### Writing Tests

#### Unit Tests

```python
import pytest
from src.game.ship import Ship
from src.utils.config import Config

class TestShip:
    @pytest.fixture
    def ship(self):
        config = Config()
        return Ship(config)
    
    def test_take_damage_reduces_shields_first(self, ship):
        """Test that damage is absorbed by shields before affecting energy."""
        initial_shields = ship.shields
        initial_energy = ship.energy
        
        damage_taken = ship.take_damage(100)
        
        assert damage_taken == 100
        assert ship.shields == initial_shields - 100
        assert ship.energy == initial_energy
```

#### AI Behavior Tests

```python
def test_klingon_ai_aggressive_behavior():
    """Test that aggressive Klingons prefer close combat."""
    ai = KlingonAI(config)
    klingon_pos = (3, 3)
    player_pos = (5, 5)
    
    # Set up aggressive Klingon
    ai.klingon_states[klingon_pos] = KlingonState(
        position=klingon_pos,
        personality=KlingonPersonality.AGGRESSIVE,
        # ... other parameters
    )
    
    action = ai.decide_action(klingon_pos, player_pos, mock_ship, mock_quadrant)
    
    # Aggressive Klingons should move closer or attack
    assert action['action'] in ['move', 'attack']
    if action['action'] == 'move':
        new_pos = action['new_position']
        new_distance = calculate_distance(new_pos, player_pos)
        old_distance = calculate_distance(klingon_pos, player_pos)
        assert new_distance < old_distance
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/ai/
pytest -k "test_combat"

# Run performance tests
pytest tests/performance/ --benchmark-only
```

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **API Documentation**: Auto-generated from docstrings
3. **User Documentation**: Guides and tutorials
4. **Developer Documentation**: Architecture and design decisions

### Documentation Standards

#### Docstring Requirements

- All public classes, methods, and functions must have docstrings
- Include parameter types, return types, and examples
- Document exceptions that may be raised
- Use clear, concise language

#### README Updates

When adding new features, update the README.md:

- Add new features to the feature list
- Update installation instructions if needed
- Add new command-line options
- Update screenshots or examples

#### Architecture Documentation

For significant changes, update `docs/ARCHITECTURE.md`:

- Document new components and their interactions
- Update system diagrams
- Explain design decisions and trade-offs

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `pytest tests/`
2. **Check code quality**: `pre-commit run --all-files`
3. **Update documentation**: Add or update relevant docs
4. **Test manually**: Verify your changes work as expected
5. **Rebase on main**: Ensure your branch is up to date

### Pull Request Template

Use this template for your PR description:

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] AI behavior enhancement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] AI behavior validated (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] No breaking changes (or breaking changes documented)

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information or context.
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs tests and quality checks
2. **Code review**: At least one maintainer reviews the code
3. **AI review**: For AI-related changes, an AI specialist reviews
4. **Testing**: Changes are tested in development environment
5. **Approval**: Maintainer approves and merges the PR

## Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.10.5]
- Game version: [e.g., 1.0.0]
- Interface: [ASCII/Pygame]

**Additional Context**
Add any other context about the problem here.

**Logs**
Include relevant log files or error messages.
```

### Feature Requests

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Explain why this feature would be useful.

**Proposed Implementation**
If you have ideas about how to implement this feature.

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context or screenshots about the feature request.
```

## AI Development Guidelines

### AI Agent Design Principles

1. **Modularity**: AI agents should be self-contained and interchangeable
2. **Configurability**: Behavior should be configurable through parameters
3. **Testability**: AI decisions should be deterministic when needed for testing
4. **Performance**: AI should make decisions quickly to maintain game flow
5. **Believability**: AI behavior should feel natural and engaging

### AI Implementation Standards

#### Decision Making

```python
class AIAgent:
    def decide_action(self, game_state: GameState) -> Action:
        """
        Make a decision based on current game state.
        
        This method should be deterministic for the same input
        when random seed is fixed (for testing).
        """
        # Analyze situation
        analysis = self.analyze_situation(game_state)
        
        # Generate options
        options = self.generate_options(analysis)
        
        # Evaluate and choose
        best_option = self.evaluate_options(options, analysis)
        
        return best_option
```

#### Learning and Adaptation

```python
class AdaptiveAI:
    def update_model(self, experience: Experience) -> None:
        """Update AI model based on experience."""
        # Validate experience data
        if not self.validate_experience(experience):
            return
        
        # Update learning model
        self.learning_model.update(experience)
        
        # Adjust behavior parameters
        self.adjust_parameters(experience)
        
        # Log learning progress
        self.logger.debug(f"AI updated from experience: {experience}")
```

### AI Testing Requirements

- **Behavior validation**: Test that AI behaves according to its personality
- **Performance testing**: Ensure AI decisions are made quickly
- **Learning verification**: Test that adaptive AI actually learns
- **Edge case handling**: Test AI behavior in unusual situations

## Performance Considerations

### Performance Guidelines

1. **Profiling**: Use profiling tools to identify bottlenecks
2. **Caching**: Cache expensive calculations when appropriate
3. **Lazy loading**: Load resources only when needed
4. **Memory management**: Avoid memory leaks and excessive allocation
5. **Algorithm efficiency**: Use appropriate data structures and algorithms

### Performance Testing

```python
import pytest
import time

def test_ai_decision_performance():
    """Test that AI decisions are made within acceptable time limits."""
    ai = KlingonAI(config)
    game_state = create_test_game_state()
    
    start_time = time.time()
    action = ai.decide_action(game_state)
    decision_time = time.time() - start_time
    
    # AI should make decisions in under 100ms
    assert decision_time < 0.1
    assert action is not None
```

### Benchmarking

Use pytest-benchmark for performance testing:

```python
def test_galaxy_generation_benchmark(benchmark):
    """Benchmark galaxy generation performance."""
    config = Config()
    galaxy = Galaxy(config)
    
    result = benchmark(galaxy.generate)
    
    # Ensure galaxy was generated correctly
    assert galaxy.count_klingons() > 0
    assert galaxy.count_starbases() > 0
```

## Release Process

### Version Numbers

We use Semantic Versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in a backwards compatible manner
- **PATCH**: Backwards compatible bug fixes

### Release Checklist

1. **Update version numbers** in relevant files
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite** and ensure all tests pass
4. **Update documentation** for new features
5. **Create release branch** and test thoroughly
6. **Tag release** with version number
7. **Create GitHub release** with release notes
8. **Update main branch** with release changes

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- New Klingon AI personality: Berserker
- Strategic AI route optimization
- Save/load game functionality

### Changed
- Improved combat damage calculations
- Enhanced pygame interface responsiveness

### Fixed
- Fixed energy calculation bug in navigation
- Resolved memory leak in AI decision making

### Deprecated
- Old configuration format (will be removed in 2.0.0)

## [1.1.0] - 2023-12-01
...
```

## Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and discussions
- **Code Reviews**: For technical discussions about specific changes

### Maintainer Contact

For urgent issues or questions about contributing:

- Create an issue with the "question" label
- Tag maintainers in discussions
- Follow up on existing issues if no response within a week

### Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/)
- [pygame Documentation](https://www.pygame.org/docs/)

## Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **Release notes**: Major contributions highlighted
- **GitHub**: Contributor statistics and graphs
- **Special recognition**: Outstanding contributions may receive special mention

Thank you for contributing to Agentic Trek! Your contributions help make this project better for everyone. 🚀

---

*This document is living and will be updated as the project evolves. Please suggest improvements by creating an issue or pull request.*
