# AGENTS.md

This file provides guidance to AI coding assistants (GitHub Copilot, Claude Code, etc.) when working with code in this repository.

## Project Overview

**role-play** is a virtual role-playing game application built with Django. It allows people to play role-playing games remotely by following a story and performing actions like throwing dice or making choices.

- **Language**: Python 3.14
- **Framework**: Django 5.2
- **Architecture**: Async-capable with Channels, WebSockets, and Celery for background tasks
- **AI Integration**: Uses Anthropic's Claude API for content generation
- **Database**: PostgreSQL
- **Caching/Queue**: Redis

## Project Structure

```
role-play/
├── ai/                     # AI text generation using Anthropic API
├── character/              # Character management (abilities, classes, races, skills, etc.)
├── game/                   # Core game logic (events, combat, flows, rolls)
├── master/                 # Game master functionality
├── user/                   # User management and authentication
├── utils/                  # Shared utilities
├── role_play/              # Django project settings
├── tasks/                  # Invoke task definitions
├── media/                  # User-uploaded media files
└── docs/                   # Documentation and screenshots
```

## Key Modules

### Character Module (`character/`)
Handles all character-related functionality:
- **Models**: abilities, advancement, character, disadvantages, equipment, classes (klasses), proficiencies, races, skills
- **Forms**: Character creation and management forms
- **Views**: Character CRUD operations
- **Utils**: Character attribute builders and ability modifiers

### Game Module (`game/`)
Core game mechanics and flow:
- **Models**: game, events, combat
- **consumers.py**: WebSocket consumers for real-time game interactions
- **flows.py**: Game state machine and workflow management
- **rolls.py**: Dice rolling mechanics
- **commands.py**: Game commands processing
- **event_enrichers.py**: Event enhancement logic
- **tasks.py**: Celery background tasks

### AI Module (`ai/`)
- **generators.py**: TextGenerator class using Anthropic's Claude API
- Implements singleton pattern for API client
- Used for enriching quest descriptions and game content

## Build & Run Commands

**Important**: This project uses [Doppler](https://www.doppler.com/) for secrets management. All commands that require environment variables (like API keys) should be prefixed with `doppler run --` to inject the necessary secrets.

### Development
```bash
doppler run -- uv run invoke dev.run          # Start development server
```

### Testing
```bash
doppler run -- uv run invoke test.run         # Run all tests
doppler run -- uv run invoke test.run --test-label=path/to/test_file.py::TestClass::test_method  # Run single test
doppler run -- uv run invoke test.run --coverage && uv run invoke test.coverage-report  # Coverage report
```

### Database
```bash
doppler run -- uv run invoke db.migrate       # Run migrations
doppler run -- uv run invoke db.reset         # Reset database
```

### Code Quality
```bash
pre-commit run --all-files     # Run all pre-commit hooks
ruff check                     # Lint Python code
ruff format                    # Format code
mypy                          # Type checking
```

## Code Style Guidelines

### General Python Style
- **Imports Order**:
  1. Standard library (alphabetically)
  2. Third-party packages (alphabetically)
  3. Project modules (alphabetically)
  - Use absolute imports for external modules
  - Use relative imports for internal modules

- **Naming Conventions**:
  - `PascalCase` for classes
  - `snake_case` for functions and variables
  - `UPPER_SNAKE_CASE` for constants
  - Avoid abbreviations unless commonly understood

- **Type Hints**: Always use type hints for function parameters and return values

### Django-Specific Guidelines

- **Models**:
  - Organize by domain in subdirectories
  - Use Django's model validation
  - Constants defined as enum-like classes in `constants/` directories

- **Error Handling**:
  - Define custom exceptions in `exceptions.py` files
  - Use Django's built-in exception types when appropriate

- **Async Support**:
  - This project uses Django Channels for async capabilities
  - WebSocket consumers in `consumers.py`
  - Be aware of sync/async context when writing code

### Testing
- **Framework**: pytest with django plugin
- **Naming**: Follow `test_*.py` convention
- **Pattern**: Use factory pattern for test data (see `conftest.py` and `factories.py` files)
- **Location**: Tests in `tests/` subdirectories within each app

## Dependencies & Tools

### Core Dependencies
- **Django 5.2**: Web framework
- **Channels**: WebSocket support
- **Celery**: Background task processing
- **Anthropic**: Claude AI API client
- **Pydantic**: Data validation
- **django-viewflow**: Workflow management

### Development Tools
- **uv**: Fast Python package installer and resolver
- **invoke**: Task execution tool
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality
- **Doppler**: Secrets management (required for running commands)

## Key Patterns & Conventions

### Singleton Pattern
The `TextGenerator` class in `ai/generators.py` uses singleton pattern:
```python
class TextGenerator:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize once
        return cls._instance
```

### Domain-Driven Design
The project is organized by domain (character, game, master, user) with each having:
- `models/` - Domain models
- `views/` - HTTP views
- `forms/` - Form definitions
- `tests/` - Test suite
- `constants/` - Domain constants
- `utils/` - Domain-specific utilities

### Configuration
- Excluded from linting: `role_play/asgi.py`, `role_play/urls.py`, `role_play/settings/*`
- Coverage omits: `manage.py`, `tasks/*`

## Common Tasks for AI Agents

### When Adding New Features
1. Identify the appropriate domain module (character, game, master, user)
2. Add models in `models/` subdirectory
3. Create forms in `forms/` if needed
4. Implement views in `views/` or consumers in `consumers.py` for WebSocket
5. Add URL patterns in `urls.py`
6. Write tests in `tests/` directory
7. Add constants to `constants/` if needed

### When Fixing Bugs
1. Check existing tests in the relevant `tests/` directory
2. Run specific test: `doppler run -- uv run invoke test.run --test-label=path/to/test`
3. Check for related issues in error handling (`exceptions.py`)
4. Verify Django model validation rules

### When Refactoring
1. Ensure type hints are present
2. Run full test suite before and after
3. Check coverage: `doppler run -- uv run invoke test.run --coverage`
4. Format with ruff: `ruff format`
5. Run pre-commit hooks: `pre-commit run --all-files`

## Important Notes

- **Python Version**: Project requires Python 3.14
- **Secrets Management**: Uses Doppler for environment variables and API keys
- **Under Development**: This is an active project; UI and features are evolving
- **Real-time Features**: Uses WebSockets for real-time game interactions
- **AI-Enhanced**: Quest descriptions and game content can be enriched using Claude AI
- **License**: GNU Affero General Public License v3.0

## Related Documentation
- `README.md` - Project overview and screenshots
- `CHANGELOG.md` - Version history and changes
- `LICENSE.md` - Full license text

## Deployment
- Docker support available (`Dockerfile`, `docker-compose.yml`)
- Fly.io configuration (`fly.toml`, `fly.ephemeral.toml`)
- Gunicorn for production WSGI
- Daphne for ASGI/WebSocket support
