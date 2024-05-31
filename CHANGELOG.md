# CHANGELOG

Versions follow [Semantic Versioning](https://semver.org/) (`<major>.<minor>.<patch>`).

## Unreleased

### Added
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
