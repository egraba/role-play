# CLAUDE.md

This file provides context to Claude Code when working with this repository.

## Project Overview

**role-play** is a Django-based virtual tabletop for D&D 5th Edition (SRD 5.2.1) with real-time WebSocket gameplay, AI-powered content generation via Claude API, and comprehensive combat mechanics.

**Tech Stack**: Python 3.14, Django 6.0, PostgreSQL, Redis, Django Channels (WebSockets), HTMX, Anthropic Claude API

## Essential Commands

> **Critical**: This project uses [Doppler](https://www.doppler.com/) for secrets. Commands requiring API keys or DB access must be prefixed with `doppler run --`.

```bash
# Environment setup
uv sync                                  # Install dependencies
source .venv/bin/activate                # Activate virtualenv

# Development
doppler run -- uv run poe dev-run        # Start dev server
doppler run -- uv run poe test           # Run tests (REQUIRED before PR)
doppler run -- uv run poe test-cov       # Tests with coverage

# Code quality (REQUIRED before PR)
pre-commit run --all-files               # Lint, format, type check

# Database
doppler run -- uv run poe db-migrate     # Run migrations
doppler run -- uv run poe db-reset       # Reset database
```

Run `poe --help` to see all available tasks.

## Project Structure

```
character/     # Character system (abilities, classes, races, skills, equipment, spells)
game/          # Game engine (events, combat, WebSocket consumers, rolls)
master/        # Campaign management
user/          # Authentication
ai/            # Claude API integration for content generation
role_play/     # Django settings
```

Each app follows a consistent pattern: `models/`, `views/`, `forms/`, `tests/`, `constants/`, `utils/`

## Code Style

- **Imports**: stdlib → third-party → project modules (alphabetical within each group)
- **Relative imports** for internal modules, **absolute** for external
- **Type hints** required on all function signatures
- **Naming**: `PascalCase` classes, `snake_case` functions/variables, `UPPER_SNAKE_CASE` constants
- **Custom exceptions** go in `exceptions.py` files per app
- **Constants** as enum-like classes in `constants/` directories

### Frontend Guidelines

- **Browser compatibility**: Chrome AND Safari required
  - Always include vendor prefixes: `-webkit-`, `-moz-`, standard
  - Use `-webkit-appearance: none` for form elements
- **CSS**: Uses `rpg-styles.css` design system (dark theme, gold accents)
  - Components: `rpg-panel`, `rpg-btn`, `rpg-table`, `rpg-form-group`
- **Templates**: Extend `base.html`, use SVG icons (never emoji as icon substitutes)
  - SVG icons use `class="rpg-icon"` — `filter: invert(1)` makes black SVGs white on dark backgrounds
  - Color variants: `rpg-icon-primary` (gold), `rpg-icon-danger` (red), `rpg-icon-success` (green), `rpg-icon-info` (blue), `rpg-icon-warning` (yellow)

### Testing

- **Framework**: pytest with django plugin
- **Factories**: Use factory pattern (see `conftest.py`, `factories.py`)
- **Location**: `tests/` subdirectory within each app

## Git Workflow

1. **Always create a branch**: `git checkout -b <type>/<name>`
   - Prefixes: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`
2. **Never commit directly to `main`**

## PR Checklist (MANDATORY)

Before submitting any PR:

1. **Tests pass**: `doppler run -- uv run poe test`
2. **Coverage maintained**: `doppler run -- uv run poe test-cov`
3. **Pre-commit passes**: `pre-commit run --all-files`
4. **CHANGELOG.md updated** under `## Unreleased`:
   - `### Added` - new features
   - `### Changed` - modifications
   - `### Fixed` - bug fixes
   - `### Removed` - removed features
5. **Architecture changes documented** in all applicable files: `CLAUDE.md`, `ARCHITECTURE.md`, `README.md`

## Key Technical Details

- **D&D Rules**: Follow SRD 5.2.1 exactly
- **Async**: Django Channels for WebSockets, sync views otherwise (Celery was removed)
- **AI logic** stays in `ai/` app
- **License**: AGPL-3.0 (code), CC-BY-4.0 (D&D SRD content)

### Event System Architecture

- **Event models** (`game/models/events.py`): Pure data - fields and DB behavior only, no presentation or type-mapping logic
- **Event registry** (`game/constants/event_registry.py`): Maps Event subclass → `EventType` via `get_event_type(event)`
- **Presenters** (`game/presenters.py`): Maps Event subclass → display string via `format_event_message(event)`
- **Consumer** (`game/consumers.py`): Uses `__getattr__` catch-all for Django Channels dispatch instead of per-event handler methods
- **Circular import pattern**: Registries use lazy `_build_*()` functions with `None` sentinels to avoid model ↔ constants cycles

## Related Documentation

- `README.md` - Overview and screenshots
- `ARCHITECTURE.md` - Detailed system design
- `CHANGELOG.md` - Version history
