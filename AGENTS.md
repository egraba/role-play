# AGENTS.md

This file provides guidance to AI coding assistants (GitHub Copilot, Claude Code, etc.) when working with code in this repository.

## Project Overview

**role-play** is a virtual role-playing game application built with Django. It allows people to play role-playing games remotely by following a story and performing actions like throwing dice or making choices.

The game implements Dungeons & Dragons 5th Edition rules based on the **SRD 5.2** (Systems Reference Document version 5.2.1), which includes content from the 2024 D&D core rulebooks under the Creative Commons Attribution 4.0 International License.

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

Tasks are managed with [Poe the Poet](https://poethepoet.natn.io/). Run `poe --help` to see all available tasks.

### Environment Setup (Required Before Any Command)
Before executing any command, ensure the virtual environment is created and activated:
```bash
uv sync                                       # Create/update virtualenv and install dependencies
source .venv/bin/activate                     # Activate the virtualenv (macOS/Linux)
```

### Development
```bash
doppler run -- uv run poe dev-run             # Start development server
doppler run -- uv run poe dev-worker          # Start Celery worker
uv run poe shell                              # Django shell
uv run poe clean                              # Clean generated files
```

### Testing
```bash
doppler run -- uv run poe test                # Run all tests
doppler run -- uv run poe test-verbose        # Run tests with verbose output
doppler run -- uv run poe test-cov            # Run tests with coverage
uv run poe test-cov-report                    # Generate HTML coverage report
```

### Database
```bash
doppler run -- uv run poe db-migrate          # Run migrations
doppler run -- uv run poe db-reset            # Reset database
doppler run -- uv run poe db-make-migrations  # Make migrations
doppler run -- uv run poe db-load-settings    # Load fixtures
doppler run -- uv run poe db-populate         # Populate with realistic data
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

### Frontend & CSS Guidelines

- **Browser Compatibility**: All CSS and HTML changes must be compatible with both **Chrome** and **Safari**
  - Use vendor prefixes for CSS properties: `-webkit-`, `-moz-`, `standard`
  - Include `box-sizing`, `-webkit-box-sizing`, `-moz-box-sizing`
  - Use `-webkit-appearance: none` for form elements to ensure consistent styling
  - Test visual changes in both browsers before committing
- **CSS Design System**: Uses custom `rpg-styles.css` for RPG-themed interface
  - Dark backgrounds with golden accents (`var(--color-primary)`)
  - Consistent component classes: `rpg-panel`, `rpg-btn`, `rpg-table`, `rpg-form-group`
  - Form inputs must be styled within `.rpg-form-group` containers
- **Templates**: Django templates in `templates/` subdirectories within each app
  - All extend `base.html`
  - Use emoji icons instead of images where possible

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
- **poethepoet**: Task runner (configured in pyproject.toml)
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
- Coverage omits: `manage.py`

## Rules Implementation
- Follow SRD 5.2.1 rules exactly
- Use Django models for game entities
- Write tests for all mechanics
- Keep AI logic in the ai/ app

## Common Tasks for AI Agents

### Before Starting Any Work
1. Create a new branch for your changes: `git checkout -b <type>/<descriptive-name>`
   - Use prefixes: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`
   - Example: `git checkout -b feat/add-character-inventory`
2. Never commit directly to `main` branch

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
2. Write a test that reproduces the bug (test should fail before the fix)
3. Implement the fix
4. Run specific test: `doppler run -- uv run poe test` (use pytest path syntax for single tests)
5. Verify the test passes after the fix
6. Check for related issues in error handling (`exceptions.py`)
7. Verify Django model validation rules

### When Refactoring
1. Ensure type hints are present
2. Run full test suite before and after
3. Check coverage: `doppler run -- uv run poe test-cov`
4. Format with ruff: `ruff format`
5. Run pre-commit hooks: `pre-commit run --all-files`

## Important Notes

- **Python Version**: Project requires Python 3.14
- **Secrets Management**: Uses Doppler for environment variables and API keys
- **Under Development**: This is an active project; UI and features are evolving
- **Real-time Features**: Uses WebSockets for real-time game interactions
- **AI-Enhanced**: Quest descriptions and game content can be enriched using Claude AI
- **License**: GNU Affero General Public License v3.0 (application code); CC-BY-4.0 for D&D SRD 5.2 game content

## Related Documentation
- `README.md` - Project overview and screenshots
- `CHANGELOG.md` - Version history and changes
- `LICENSE.md` - Full license text

## Deployment
- Docker support available (`Dockerfile`, `docker-compose.yml`)
- Fly.io configuration (`fly.toml`)
- Gunicorn for production WSGI
- Daphne for ASGI/WebSocket support
