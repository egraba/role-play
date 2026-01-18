# CHANGELOG

Versions follow [Semantic Versioning](https://semver.org/) (`<major>.<minor>.<patch>`).

## Unreleased

### Added
* Spell effect system for D&D 5e magic mechanics:
  - SpellEffectTemplate model linking spells to their mechanical effects (damage, healing, conditions, buffs/debuffs, summons)
  - ActiveSpellEffect model for tracking ongoing spell effects on characters
  - SummonedCreature model for tracking creatures summoned by spells
  - Spell effect enums: SpellEffectType, SpellTargetType, SpellSaveType, SpellSaveEffect, SpellDamageType, EffectDurationType
  - Resolution system (game/spell.py) with dataclasses: SpellSaveResult, SpellDamageResult, SpellHealingResult, SpellConditionResult, SpellBuffResult, SpellCastResult
  - Core resolution functions: get_spell_save_dc(), resolve_saving_throw(), resolve_spell_damage(), resolve_spell_healing(), resolve_spell_condition(), resolve_spell_buff(), resolve_spell()
  - Application functions: apply_spell_damage(), apply_spell_healing(), apply_spell_condition(), apply_spell_buff(), apply_spell_result()
  - Spell event types: SPELL_CAST, SPELL_DAMAGE_DEALT, SPELL_HEALING_RECEIVED, SPELL_CONDITION_APPLIED, SPELL_SAVING_THROW
  - Spell event models: SpellCast, SpellDamageDealt, SpellHealingReceived, SpellConditionApplied, SpellSavingThrow
* Spellcasting system with comprehensive D&D 5e magic support:
  - SpellSettings model for spell definitions (level, school, casting time, range, components, duration, description)
  - Spell model for spontaneous casters (Sorcerer, Bard, Warlock) tracking spells known
  - SpellPreparation model for prepared casters (Cleric, Wizard, Druid, Paladin) with always_prepared flag for domain spells
  - SpellSlotTable reference data for spell slots per class and level
  - CharacterSpellSlot for tracking spell slot usage with use_slot(), restore_slot(), and restore_all() methods
  - WarlockSpellSlot for Pact Magic (separate tracking, restores on short rest)
  - ClassSpellcasting configuration per class (spellcasting ability, caster type, cantrips, ritual casting, focus)
  - Concentration model for tracking active concentration spells with start_concentration() and break_concentration() methods
  - Spell enums: SpellSchool, SpellLevel, CastingTime, SpellRange, SpellDuration, SpellComponent, CasterType, SpellcastingAbility
  - SRD 5.2.1 spell fixtures with 14 commonly used spells:
    - Cantrips: Fire Bolt, Light, Mage Hand, Prestidigitation
    - Level 1: Cure Wounds, Magic Missile, Shield, Sleep
    - Level 2: Hold Person, Invisibility, Misty Step
    - Level 3: Counterspell, Fireball, Fly
* Attack resolution system implementing D&D 5e combat mechanics:
  - Attack roll = d20 + ability modifier + proficiency bonus (if proficient)
  - Compare attack roll to target AC for hit/miss determination
  - Damage roll = weapon damage dice + ability modifier on hit
  - Critical hits on natural 20 (double damage dice)
  - Critical misses on natural 1 (always miss)
  - Automatic ability selection: STR for melee, DEX for ranged, choice for finesse weapons
  - Weapon proficiency checking via WeaponProficiency model
  - Damage application with HP floor at 0
* Weapon mastery properties from D&D 5e SRD 5.2.1:
  - Cleave: On kill, excess damage carries to another enemy within 5 feet
  - Graze: On miss, deal ability modifier damage (minimum 0)
  - Nick: Can make extra attack with light weapon as part of Attack action
  - Push: On hit, push target 10 feet away (if Large or smaller)
  - Sap: On hit, target has disadvantage on next attack before your next turn
  - Slow: On hit, reduce target's speed by 10 feet until start of your next turn
  - Topple: On hit, target must make CON save (DC 8 + prof + mod) or be knocked prone
  - Vex: On hit, gain advantage on next attack against same target before end of turn
* Combat action system supporting D&D 5e standard actions: Attack, Cast a Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use an Object
* Action economy tracking per turn: 1 action, 1 bonus action, 1 reaction, and movement
* TurnAction model to record actions taken during combat turns
* Turn model enhanced with action economy fields (action_used, bonus_action_used, reaction_used, movement_used, movement_total)
* ActionType enum for classifying actions (Action, Bonus Action, Reaction)
* ActionTaken event model and ACTION_TAKEN event type for broadcasting combat actions
* Player views: TakeActionView for taking combat actions, TurnStateView for checking turn state, MoveView for using movement
* ActionNotAvailable and NotYourTurn exceptions for combat action validation
* Combat.start_combat() and advance_turn() now create Turn records for action tracking
* HTMX 2.0 integration for real-time UI updates without full page reloads (includes django-htmx middleware for request.htmx detection)
* Class model with hit die, primary ability, saving throw proficiencies, armor/weapon proficiencies, and starting wealth
* ClassFeature model for class features gained at each level
* CharacterClass junction model supporting multiclassing (character can have multiple classes with levels)
* Fighter class with all 17 features from D&D 2024 SRD (levels 1-20)
* All 12 SRD classes with complete data: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard
* Level 1 class features for all 12 classes (Rage, Bardic Inspiration, Spellcasting, Sneak Attack, etc.)
* ClassBuilder for applying class features to characters using the new Class model
* Character.primary_class and Character.class_level properties
* Comprehensive architecture documentation (ARCHITECTURE.md) covering Django app structure, models, game logic, and master/player distinction
* Dice system enhancements: advantage/disadvantage rolls, damage rolls with critical hits, d20 tests with natural 1/20 detection
* Condition model with all 15 SRD conditions (Blinded, Charmed, Deafened, Exhaustion, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious)
* Species model with 4 SRD species (Dwarf, Elf, Halfling, Human) following D&D 2024 rules
* SpeciesTrait model with 12 species traits (Dwarven Resilience, Dwarven Toughness, Stonecunning, Fey Ancestry, Keen Senses, Trance, Brave, Halfling Nimbleness, Lucky, Resourceful, Skillful, Versatile)
* Feat and CharacterFeat models for origin feats (D&D 2024 rules)
* Origin feats: Alert, Magic Initiate (Cleric), Magic Initiate (Wizard), Savage Attacker
* BackgroundBuilder now grants tool proficiency, origin feat, and 50 GP starting equipment
* Combat initiative tracking system with turn order management (state machine: ROLLING_INITIATIVE → ACTIVE → ENDED)
* Combat round and turn tracking (current_round, current_turn_index, current_fighter)
* Combat model methods: `start_combat()`, `advance_turn()`, `end_combat()`, `get_turn_order_display()`
* New combat events: CombatStarted, TurnStarted, TurnEnded, RoundEnded, CombatEnded
* Master views for turn advancement (CombatAdvanceTurnView) and ending combat (CombatEndView)
* EventType constants for new combat events (COMBAT_STARTED, TURN_STARTED, TURN_ENDED, ROUND_ENDED, COMBAT_ENDED)
* HTMX 2.0.4 integration for real-time UI updates without full page reloads
* django-htmx middleware for HTMX request detection (`request.htmx`)

### Fixed
* Use authenticated user instead of client-provided username in message storage and event enrichers (security fix)
* Fixed typo in CombatAction.DISENGAGE value ("disangage" → "disengage")
* Renovate configuration now supports uv lock files and PEP 735 dependency groups

### Changed
* Deploy workflow now waits for CI to pass instead of running duplicate tests (uses workflow_run trigger)
* Renamed `klasses.py` files to `classes.py` (models and constants) for consistency with model names
* CharacterCreateForm now uses ModelChoiceField for Class selection
* Split tool configurations from pyproject.toml into separate files (poe_tasks.toml, ruff.toml, pytest.ini)
* Updated project to reference D&D 5th Edition SRD 5.2 specification with CC-BY-4.0 attribution
* Ability model now auto-calculates modifier on save and validates score range (1-30)
* Proficiency bonus is now calculated from character level using D&D 5e formula: levels 1-4 = +2, 5-8 = +3, 9-12 = +4, 13-16 = +5, 17-20 = +6
* **BREAKING**: Race field replaced with Species foreign key (D&D 2024 rules - ability score increases are now player-chosen, not species-determined)
* **BREAKING**: Background system updated to D&D 2024 SRD rules - each background now provides tool proficiency, origin feat, and 50 GP
* Criminal background skill proficiencies changed from Deception/Stealth to Sleight of Hand/Stealth (D&D 2024 rules)
* Combat initiative completion check now runs immediately after each roll instead of using celery-beat periodic task (more efficient, eliminates 2-second polling delay)

### Removed
* **BREAKING**: Removed legacy class system: `Klass` enum, `KLASS_FEATURES` dictionary, `KlassBuilder`, and `Character.klass` field (replaced by Class model and ClassBuilder)
* Removed legacy models: `KlassFeature`, `HitPoints`, `KlassAdvancement` (class data now in Class/ClassFeature models)
* Redis cache usage removed from application code (Redis still required for Channels and Celery)
* Removed `dice` library dependency (replaced with built-in `random` module)
* Removed Race enum, RACIAL_TRAITS dictionary, and Sense model (replaced by Species system)
* Removed Character fields: adult_age, life_expectancy, alignment, senses (no longer in D&D 2024 rules)
* **BREAKING**: Removed Folk Hero and Noble backgrounds (not in D&D 2024 SRD 5.2)
* Removed `check_combat_roll_initiative_complete` celery-beat periodic task (replaced with immediate checking after each initiative roll)

## v0.13.0 - 2026-01-02

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
* Added tests for `check_combat_roll_initiative_complete` task
* Added tests for `AbilityCheckRequestForm` widget initialization
* Added test for server-side event handling in WebSocket consumers
* Configured pytest-cov for parallel coverage collection

### Fixed
* Combat initiation now works correctly when starting multiple combats (use `update_or_create` for Fighter, CombatInitiativeRequest, CombatInitiativeResponse, and CombatInitiativeResult)
* Combat initiative completion task now properly sets the `author` field on CombatInitativeOrderSet
* WebSocket consumer now properly handles disconnect when game not found

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
