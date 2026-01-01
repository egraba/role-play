# CHANGELOG

Versions follow [Semantic Versioning](https://semver.org/) (`<major>.<minor>.<patch>`).

## Unreleased

### Added
* Quest environments are now enriched using Claude 3.5 Sonnet model
* WebSocket auto-reconnect with exponential backoff when server restarts
* Added AGENTS.md with comprehensive guidance for AI coding assistants
* Added Django and Celery startup integration tests
* Complete CSS redesign with new rpg-styles.css design system
* Configured Renovate for automated dependency updates (including pre-commit hooks)
* Added poe tasks: code quality (lint, format, typecheck, check), aliases (run, migrate, worker), management commands (delete-character, delete-combats, request-saving-throw), and convenience tasks (ci, db-setup, pre-commit)
* Added `/health/` endpoint for Fly.io health checks
* Added post-deployment health check verification in CI

### Changed
* Reduce machines size on Fly.io
* Upgraded Django from 5.1 to 5.2
* Enhanced CI workflow to use Doppler for environment variable management
* Migrated to Python 3.14
* Migrated task runner from invoke to poethepoet
* Speed up test execution with pytest-xdist parallel running and optimized test settings
* Form validation errors for duplicate values now show specific field names instead of a generic message
* Updated Dockerfile with modern Doppler CLI installation method
* Improved fly.toml with proper VM configuration and Doppler integration
* Split CI workflow into separate lint and test jobs for faster feedback
* Deploy workflow now runs tests before deploying to production
* Added manual deployment trigger via workflow_dispatch
* Character creation dropdowns now show empty "---------" placeholder by default instead of pre-selecting the first option

## v0.12.0 - 2025-01-18

### Added
* Tests can now be launched from VS Code
* App errors are now monitored by Sentry in production
* Increase test coverage

### Changed
* Use `celery_session_worker` to speed up celery tasks tests
* Created `Actor` model to encapsulate `Master` and `Player` models
* Actions are now done by players and not characters
* Index page displays more relevant buttons
* Users are now invited, instead of characters
* `Player` model have now one-to-one relation with `User`
* Python 3.13 is now the only supported version
* Replace `poetry` by `uv` as package manager
* Various code and comments improvements

## v0.11.0 - 2024-12-26

### Added
* Characters' attributes are now accessible by properties
* App is now deployable on Fly.io

### Changed
* `scrypt` is now the default password hasher
* Characters are now created via a wizard form
* Improve combat inittiative task management
* Simplify settings per environment
* Migrate to Django 5.1
* Various code and comments improvements

## v0.10.0 - 2024-08-16

### Added
* DnD: Implement combat initialization
* Add `delete_combats` command
* DnD: Implement combat structure

### Changed
* Use customer User model instead of Django one
* Use `freezegun` to test times
* Improve and rename some invoke commands
* Enhance game events and their messages handling
* Make celery tasks more robust
* Refactor character app utils
* Move rolls module outside of `game.utils`
* Refactor consumers using command pattern
* Decouple character's advantages and roll functions
* Various code and comments improvements

### Fixed
* Split quest model from quest update events
* Remove end date column in game list
* Remove unnecessary `create()` calls
* Suppress `factory-boy` warnings

## v0.9.0 - 2024-06-02

### Added
* Inventory is now displayed in character's detail view
* DnD: Implement weapon settings
* DnD: Implement amor-related disadvantages
* DnD: Equipment is now properly instantiated
* DnD: Add wealth at character creation

### Changed
* Improve `delete_character` command
* Upgrade Django channels to 4.1.0
* Upgrade Celery to 5.4
* Remove `pytest-celery` package
* Migrate from `django-fsm`to `django-viewflow`

### Fixed
* Fixed background completion form display

## v0.8.0 - 2024-03-23

### Added
* DnD: Support backgrounds
* DnD: Support personality traits
* DnD: Support more languages
* DnD: Implement height and weight random setup
* DnD: Implement elves and dwarves subraces
* DnD: Add Androgynous gender

### Changed
* Upgrade pre-commit hooks

## v0.7.0 - 2024-03-02

### Added
* DnD: Implement saving throws

### Changed
* Extract choices from models
* Use `klass` name, instead of `class`for character's class
* DnD: Refactor ability checks
* Refactor character creation
* Use Ruff instead of other linters and formatters
* Split test coverage commands
* Migrate to pytest8

### Fixed
* Fix regression to display glossary page again

## v0.6.1 - 2024-02-09

### Added
* Use pylint as a linter
* Add pylint-pytest plugin to avoid pytest-related false-positives
* Test coverage is now checked in CI

### Changed
* Use relative imports inside modules
* Use functions and constants to retrieve cache keys
* Use `get_or_set()` where cache is used for better readability
* Remove errors raised by pylint

## v0.6.0 - 2024-02-03

### Added
* Document more classes, methods and functions
* Use mypy for type checking
* DnD: implement ability checks

### Changed
* Improve docstrings style
* Make clearer django migrate command in invoke tasks
* `populatedb` command is now idempotent

### Fixed
* Logout is now working (Django deprecation)

## v0.5.0 - 2024-01-20

### Added
* DnD: implement skills selection at character creation
* Glossary page

### Changed
* Refactor character-related views tests
* Refactor abilities-related models
* Rename equipment-related modules
* Arrange character detail page

### Fixed
* Cache is now properly set for character advancement

## v0.4.0 - 2024-01-10

### Added
* DnD: implement classes and their class features
* Celery is now used as task queue system
* DnD: implement races and their racial traits
* DnD: implement basic rules
* Game is more reactive, when players take actions
* Master is now able to give instruction separately from updating tale
* The game master can create background stories before starting a game

### Changed
* Various code enhancements (more Pythonic code, utils modules)
* Migrate to Django 5.0
* Pytest is now used instead of Unittest
* Various UX/UI improvements
* Upgrade project's libraries to their latest versions
* The project is more modular (character app, refactored testing, etc.)

## v0.3.0 - 2023-07-07

### Added
* Game page is refreshed dynamically when game events occur
* Poetry is now the virtualenv management tool
* Players are now notified when a tale is updated
* Use Redis as cache
* Various UX/UI improvements
* Add indexes on game, character and event models
* Upgrade project's libraries to their latest versions

## v0.2.1 - 2023-04-10

### Added
* Testing coverage is now measured on templates

### Fixed
* Password reset screens style is app's one
* Emails parameters are more relevant

## v0.2.0 - 2023-04-06

### Added
* Various tests enhancements
* Migrate to Django 4.2 and Psycopg3
* Various code enhancements (more Pythonista-like)
* Players can now create their characters
* Logged users now view the games they should view
* Password reset capabilities
* Pipenv is now the virtualenv management tool

### Fixed
* Players' pending actions buttons are now disabled when their usage is forbidden (#32)
* Players' pending actions are now visible to the master (#33)

## v0.1.0 - 2023-03-28

### Initial release
* Minimum Showable Product: contains basic playing functionalities for masters and players
