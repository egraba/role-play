# CHANGELOG

Versions follow [Semantic Versioning](https://semver.org/) (`<major>.<minor>.<patch>`).

## Unreleased

### Changed
* Harmonized naming between poe tasks and Django settings files
  - Renamed `local.py` to `dev.py` to match `dev-*` task prefix
  - Renamed `production_fly.py` to `prod_fly.py` to match `prod-*` task prefix
  - Updated `.env.example` and `fly.toml` references
* Replaced AGENTS.md with CLAUDE.md for better Claude Code integration
  - More concise and scannable format
  - Essential commands and PR checklist prominently placed
  - Removed redundant content covered by README and ARCHITECTURE.md
* Comprehensive rewrite of ARCHITECTURE.md to reflect current codebase
  - Updated from outdated Celery-based architecture to synchronous service layer
  - Documented new models: Species (replaces Race), Class system with multiclassing, Spellcasting, Combat
  - Added Service Layer section (GameEventService, DiceRollService)
  - Updated technology stack (Django 6.0, HTMX, removed Celery references)
  - Documented all event types, combat system, and character creation flow

### Fixed
* Fixed deployment failure by updating Docker base image from removed `bookworm-slim` to `trixie-slim` (uv 0.9+)
* Fixed flaky tests in CI caused by parallel test execution with shared PostgreSQL database
  - CI now runs tests serially (`-n 0`) to avoid race conditions and duplicate key violations
  - Made `TestSkillModel` tests more robust by handling missing fixtures gracefully
  - Improved `conftest.py` fixture loading with better documentation for xdist compatibility

### Added
* Keyboard shortcuts for the game page:
  - `R` open dice roller, `A` open attack dialog, `S` cast spell, `E` next turn (DM)
  - `I` jump to initiative tracker, `C` open character sheet, `Esc` close modals
  - `?` or floating help button to show shortcuts reference modal
  - Shortcuts disabled when typing in inputs or when a modal is open
* Quick reference panels for D&D 5e SRD rules during gameplay:
  - Conditions panel with all 15 SRD conditions and effect summaries
  - Actions in Combat panel covering standard actions, bonus actions, reactions, and movement
  - Cover Rules panel with cover types, details, and summary table
  - Spellcasting Rules panel covering spell slots, components, concentration, and casting details
  - Draggable panels with grab-handle headers for custom positioning
  - Pin functionality to keep panels open (Escape closes unpinned panels)
  - Collapsible panels and collapsible sections within each panel
  - Click-to-expand item descriptions for compact browsing
  - Position persistence via localStorage across sessions
  - Fixed toolbar at bottom of game view for quick access
  - Responsive design with mobile-friendly sizing
* Game log panel with real-time WebSocket updates:
  - Color-coded event categories: rolls (blue), combat (red), spells (purple), chat (gray), DM (gold)
  - Expandable entry details for dice rolls, ability checks, and spell casts
  - Category and character filtering with multi-select dropdown
  - Smart auto-scroll with "N new events" indicator when scrolled up
  - REST endpoint for loading last 50 events on connect
  - Enhanced WebSocket payload with category and character metadata
  - Responsive layout: right sidebar on desktop, bottom sheet on mobile
* Monster stat block component for DM dashboard:
  - Official D&D 5e stat block format with parchment aesthetic
  - Gold-framed RPGUI container matching existing design system
  - Displays: name/type, AC, HP, speed, ability scores, saves, skills, resistances, senses, languages, CR
  - Traits, Actions, Reactions, and Legendary Actions sections
  - Quick-roll buttons for ability checks, attacks, and damage
  - Responsive design for sidebar use
* Quick-roll endpoint for dice rolls from stat blocks:
  - Accepts dice expression strings (e.g., "1d20+5", "2d6-1")
  - Returns toast-style HTML fragment with roll results
  - Highlights natural 20s and 1s on d20 rolls
  - Integrates with existing DiceRollService for WebSocket broadcast
* Location field on Character model for tracking character position in-game
* Ability score assignment interface with three generation modes:
  - Point Buy mode: 27-point budget with cost per score (8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9)
  - Standard Array mode: Drag-and-drop assignment of 15, 14, 13, 12, 10, 8 values
  - Roll mode: 4d6 drop lowest with animated dice display and reroll option
  - Racial/background bonus controls (-2 to +4) for each ability
  - Real-time modifier calculation using D&D formula: (score - 10) / 2
  - Final score display combining base score and racial bonuses
  - Tab-based mode switching with persistent racial bonus values
  - Save functionality to persist abilities to character
  - Success confirmation with final ability summary
  - Responsive design with mobile breakpoints
  - New views: AbilityAssignmentModalView, AbilityPointBuyView, AbilityStandardArrayView, AbilityRollView, AbilitySaveView
  - New URL endpoints: ability-assignment-modal, ability-point-buy, ability-standard-array, ability-roll, ability-save
  - Test coverage for all ability assignment views
* Concentration indicator system for combat:
  - Shows currently concentrated spell in action panel during player's turn
  - Concentration icon displayed in initiative tracker for all fighters (visible to DM and players)
  - Prompts for Constitution save when concentrating character takes damage
  - Concentration save modal with animated d20 roll and DC display
  - DC calculated as max(10, damage/2) per D&D 5e rules
  - Natural 20 always succeeds, natural 1 always fails
  - Auto-drops concentration if save failed
  - Auto-drops concentration when new concentration spell is cast (existing behavior)
  - Drop button to voluntarily end concentration
  - WebSocket events for real-time concentration updates across all clients
  - New event types: ConcentrationSaveRequired, ConcentrationSaveResult, ConcentrationBroken, ConcentrationStarted
  - New views: ConcentrationSaveModalView, ConcentrationSaveRollView
  - New URL endpoints: concentration-save-modal, concentration-save-roll
  - Purple-themed UI matching existing concentration styling
* Spell card modal for viewing full spell details:
  - Parchment-styled modal with dark gradient background and subtle texture overlay
  - Spell name header with ritual badge indicator when applicable
  - Level and school subtitle (e.g., "3rd-level evocation" or "Divination cantrip")
  - Metadata grid showing casting time, range, components, and duration
  - Color-coded component badges (V=blue, S=green, M=yellow) with material details
  - Animated concentration indicator with pulsing effect
  - Decorative star divider between metadata and description
  - Scrollable description area with custom parchment-style scrollbar
  - "At Higher Levels" section highlighted with gold border
  - Cast button for cantrips or level-selectable upcast buttons showing remaining slots
  - Disabled upcast buttons when no slots available at that level
  - Click spell names in spells panel to open the modal
  - Close via button, clicking outside, or Escape key
  - Responsive design with mobile breakpoints
  - New view: SpellCardModalView
  - New URL endpoint: character-spell-card
  - Test coverage for spell card modal (12 tests)
* Interactive spell management panel with HTMX for character spellcasting:
  - Visual spell slot tracker with clickable circles that fill/empty on use
  - Circles glow blue when filled (available), click to toggle used/available state
  - Pact Magic slots displayed separately with purple styling for Warlocks
  - Long Rest button to restore all spell slots at once
  - Active concentration banner with pulsing purple border and break button
  - Quick Cast section with cantrips and common 1st-level spells for one-click casting
  - Disabled state on quick-cast buttons when no slots remaining
  - Search input with 300ms debounced filtering
  - Filter by spell level (Cantrip through 9th)
  - Filter by school of magic (dropdown with all 8 schools)
  - Filter by concentration requirement (All/Yes/No toggle)
  - Prepared spells list grouped by level (for Cleric, Wizard, Druid, Paladin)
  - Known spells list grouped by level (for Bard, Sorcerer, Warlock, Ranger)
  - Always-prepared badge (star icon) for domain/subclass spells
  - Cast buttons on each spell that consume appropriate slot level
  - Casting a concentration spell automatically starts concentration tracking
  - Cast result feedback message with fade animation
  - School-of-magic color coding (Evocation=orange, Abjuration=blue, etc.)
  - Concentration and Ritual indicators on spell rows
  - Casting time display for each spell
  - Responsive design with mobile breakpoints
  - New views: SpellsPanelView, UseSpellSlotView, RestoreSpellSlotView, RestoreAllSlotsView, CastSpellView, BreakConcentrationView
  - New URL endpoints: character-spells-panel, character-use-spell-slot, character-restore-spell-slot, character-restore-all-slots, character-cast-spell, character-break-concentration
  - Loading spinner styles added to rpg-styles.css
  - Comprehensive test coverage (35+ tests) for all spell panel views
* Animated dice roller component for general-purpose dice rolling:
  - HTMX-powered modal dialog triggered from "Roll Dice" button in game view
  - Support for all D&D dice types (d4, d6, d8, d10, d12, d20)
  - Dice type selector with color-coded buttons (d4=red, d6=blue, d8=green, d10=orange, d12=purple, d20=gold)
  - Number of dice selector (1-10) with increment/decrement buttons
  - Modifier input (-20 to +20) for adding bonuses/penalties
  - Optional purpose field to label rolls (e.g., "Perception check")
  - Live roll preview showing dice notation and modifier
  - 3D CSS animated dice with staggered roll animations (0.1s delays per die)
  - Individual die results with max roll highlighting (green glow) and min roll indicator (red)
  - Roll breakdown showing formula, individual values, and total
  - WebSocket broadcasting of dice.roll events to all connected clients
  - DiceRoll event model for game history persistence
  - New views: DiceRollerModalView, DiceRollView
  - New URL endpoints: dice-roller-modal, dice-roll
  - New EventType: DICE_ROLL
  - DiceRollService for event creation and broadcasting
* Attack resolution modal for combat encounters:
  - HTMX-powered modal dialog triggered from Attack action button
  - Target selection dropdown showing all valid targets with their AC
  - Advantage/Disadvantage/Normal toggle with color-coded styling
  - Attack bonus display calculated from STR modifier + proficiency bonus
  - Animated d20 roll with 3D rotation animation
  - Critical hit detection (natural 20) with green glow and pulsing effect
  - Critical miss detection (natural 1) with red glow and shake effect
  - Second die display when rolling with advantage/disadvantage
  - Hit/miss determination with visual feedback (green for hit, red for miss)
  - Damage roll phase with individual dice display
  - Critical hits double damage dice per D&D 5e rules
  - Apply damage button that uses character's take_damage() method
  - Action consumption and event broadcasting on damage application
  - Modal dismissal via close button, clicking outside, or Escape key
  - Responsive design with mobile breakpoints
  - New views: AttackModalView, AttackRollView, DamageRollView, ApplyDamageView
  - New URL endpoints: combat-attack-modal, combat-attack-roll, combat-damage-roll, combat-apply-damage

### Removed
* Removed staging (`stg-*`) poe tasks from `poe_tasks.toml`

### Changed
* Enhanced character detail template to follow SRD 5.2 structure:
  - 3-column responsive layout with ability scores, combat stats, and skills
  - Ability scores with abbreviations and calculated modifiers in grid layout
  - Saving throws with proficiency markers and modifiers
  - Combat stats panel with HP bar, Armor Class, Initiative, Speed, and Hit Dice
  - Attacks section with attack bonus and damage
  - Full skill list with proficiency indicators, modifiers, and associated abilities
  - CSS-only tabbed interface for Features & Traits, Spells, Equipment, and Background
  - Species traits, class features, and feats with descriptions
  - Equipment tab with currency (CP, SP, GP, PP), armor, weapons, gear, packs, and tools
  - Background tab with personality trait, ideal, bond, and flaw
  - Responsive design with breakpoints for desktop, tablet, and mobile
  - Removed unused character_sheet.html template

### Added
* Dynamic HP bar component with HTMX and real-time WebSocket updates:
  - HTMX-powered HP bar partial template with automatic refresh
  - Current/max HP display with animated progress bar
  - Temporary HP indicator with blue styling and badge display
  - Death saves tracker with success/failure circles (shown when at 0 HP)
  - Visual feedback animations: flash red for damage, flash green for healing, flash blue for temp HP
  - Critical HP warning with pulsing animation below 25%
  - Status indicators for unconscious, stable, and dead states
  - Character model extended with `temp_hp`, `death_save_successes`, `death_save_failures` fields
  - HP management methods: `take_damage()`, `heal()`, `add_temp_hp()`, `remove_temp_hp()`
  - Death save methods: `add_death_save_success()`, `add_death_save_failure()`, `reset_death_saves()`
  - HTMX endpoints for damage, healing, temp HP, and death saves
  - WebSocket event broadcasting for HP changes to all players in game session
  - New event types: HP_DAMAGE, HP_HEAL, HP_TEMP, HP_DEATH_SAVE
* Interactive skills panel with HTMX for all 18 D&D 5e skills:
  - Filter buttons to show skills by ability score (STR, DEX, INT, WIS, CHA) or all
  - Proficiency indicators (filled/empty circles) with green background for proficient skills
  - Total modifier display combining ability modifier and proficiency bonus
  - Color-coded ability tags for each skill
  - Roll button for each skill that displays d20 result with breakdown
  - Natural 20 (green glow) and natural 1 (red glow) visual feedback
  - Proficiency bonus display at bottom of panel
  - Responsive design with mobile-optimized layout
* HTMX-powered initiative tracker component for combat management:
  - Turn order display sorted by initiative (dexterity check)
  - Round counter with visual badge
  - Per-combatant row with initiative score, character name, mini HP bar
  - HP bar color states: green (healthy), orange (<=50%), red pulsing (<=25% critical)
  - Condition icons from character's active conditions with tooltips
  - "(You)" indicator for current player's character
  - Ready and Delay action buttons (only visible on player's turn)
  - Current turn highlight with gold border and pulsing animation
  - Surprised state visual indicator (reduced opacity)
  - DM controls: Next Turn and End Combat buttons
  - Real-time WebSocket sync for turn changes, HP updates, and action events
  - HTMX endpoints: initiative-tracker, combat-ready, combat-delay
  - Responsive grid layout with mobile breakpoints
* Combat action panel for turn management:
  - Action buttons for all D&D 5e actions (Attack, Cast Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use Object)
  - Hover tooltips with action descriptions from SRD 5.2
  - Bonus Action and Reaction status indicators
  - Movement bar showing remaining/total feet with quick movement buttons (5ft, 10ft, All)
  - Actions log displaying actions taken during current turn
  - Visual greying out of used actions
  - Panel disabled when not player's turn
  - Auto-refresh on turn changes via HTMX and WebSocket events
  - HTMX endpoints updated: combat-take-action, combat-move return HTML for seamless updates
  - Responsive grid layout with mobile breakpoints

### Fixed
* Test settings no longer require environment variables - tests can run without ANTHROPIC_API_KEY, DJANGO_SECRET_KEY, or POSTGRES_PASSWORD being set

## v0.14.1 - 2026-01-27

### Fixed
* Enabled 24 skipped `TestMonsterModel` tests - the `game.Combat` ForeignKey issue was resolved (nullable FK works correctly)
* Fixed CI test failure caused by stale `PYTEST_PLUGINS` environment variable in Doppler injecting celery plugin

### Changed
* Upgraded to Django 6.0.1 (from 5.2.x)
* Upgraded all dependencies including:
  - anthropic 0.75.0 → 0.76.0
  - pydantic 2.23 → 3.0
  - gunicorn 23.0.0 → 24.1.1
  - sentry-sdk 2.48.0 → 2.50.0
* Updated pre-commit hooks (ruff 0.14.10 → 0.14.14)
* Updated CI workflow to use `astral-sh/setup-uv@v5` for proper dependency caching

### Added
* Responsive navigation system with persistent navbar:
  - Sticky navbar with brand logo, navigation links, and user dropdown
  - Mobile hamburger menu at 768px breakpoint with full-screen slide-in animation
  - Context processor providing `user_character` globally for "My Character" link
  - User dropdown shows character's class icon when available
  - Accessibility features: aria-expanded, escape key to close, click outside to dismiss
  - Removed redundant login/logout UI from homepage (now in navbar)
  - Removed border from page panels for cleaner appearance
* Integrated RPG icons throughout the application, replacing emoji icons with SVG icons:
  - Added icon assets from game-icons.net (CC BY 3.0) including classes, actions, conditions, damage types, and UI icons
  - Updated CSS with `.rpg-icon` classes supporting size modifiers (sm, md, lg, xl) and color variants (primary, danger, success, info, warning)
  - Updated all templates (28 files) to use the new SVG icons in section headers and UI elements
  - Character details view now displays class-specific icons dynamically based on character's primary class
* Extended test coverage with 948 lines of new tests:
  - `game/tests/test_schemas.py`: EventType, EventOrigin, EventSchema validation
  - `master/tests/test_forms.py`: CampaignCreateForm, CampaignUpdateForm
  - `game/tests/views/test_mixins.py`: GameContextMixin, GameStatusControlMixin, EventContextMixin
  - `character/tests/forms/test_wizard_forms.py`: All 7 character wizard steps
* Removed Celery and converted to synchronous execution:
  - Moved `process_roll` and `process_combat_initiative_roll` from Celery tasks to `GameEventService` static methods
  - Replaced `send_mail.delay()` calls with direct `django.core.mail.send_mail()` calls
  - Removed worker process from Fly.io deployment (eliminates worker VM costs)
  - Removed `celery` and `django-celery-beat` dependencies
* Refactored WebSocket event system for simpler architecture:
  - Added `get_event_type()` method to all Event model subclasses, replacing 55-line isinstance chain
  - Created `GameEventService` class for event creation and broadcasting (save-first-then-broadcast pattern)
  - Simplified consumer to use service layer for messages and call Celery tasks directly for rolls
  - Removed `event_enrichers.py` and `commands.py` (redundant abstraction layers)
  - Removed `store_message` Celery task (now handled synchronously by service)
  - Added missing WebSocket handler methods for combat and spell events

## v0.14.0 - 2026-01-25

### Added
* Enhanced 7-step character creation wizard with improved UX:
  - Step 1: Species selection with racial traits preview
  - Step 2: Class selection with features and proficiencies preview
  - Step 3: Ability scores with three generation methods (Standard Array, Point Buy, Roll 4d6 drop lowest)
  - Step 4: Background selection with skills, tool proficiency, and origin feat preview
  - Step 5: Class-specific skill selection
  - Step 6: Class-specific equipment selection
  - Step 7: Review and confirm with edit buttons for each section
  - Progress indicator with step icons and completion states
  - Real-time JavaScript previews for all selection steps
  - Animated transitions and visual enhancements
  - Real-time duplicate ability score validation with field highlighting
* Responsive character sheet template with RPGUI frames:
  - Header panel with character portrait, name, species, class, level, background, and XP
  - 3-column responsive grid layout (abilities, combat stats, skills)
  - Ability scores in 6-box grid with calculated modifiers
  - Combat stats panel with HP bar, AC, Initiative, Speed, and death saves
  - Full D&D 5e skills list with proficiency indicators and calculated modifiers
  - CSS-only tabbed interface for Features/Spells/Equipment/Background sections
  - Responsive breakpoints for desktop (3-col), tablet (2-col), and mobile (1-col)
  - CharacterDetailView now provides comprehensive context data:
    - Abilities with abbreviations, scores, and modifiers
    - All skills with proficiency status and calculated modifiers
    - Saving throws with proficiency and modifiers
    - Weapon attacks with calculated attack bonus and damage (handles finesse/ranged)
    - Species traits, class features, and feats with descriptions
* Enhanced character creation wizard with full D&D 5e support:
  - **Character Model**: Added `darkvision` field (range in feet, 0 for none)
  - **CharacterFeature Model**: New junction table to track class features gained by characters
  - **SpeciesBuilder**: Now applies darkvision from species to character during creation
  - **ClassBuilder**: Implemented armor and weapon proficiency assignment based on class categories:
    - Armor proficiencies use type codes (LA, MA, HA, SH)
    - Weapon proficiencies use categories (simple, martial)
    - Level 1 class features now automatically assigned to character
  - **DerivedStatsBuilder**: New builder for derived statistics (passive perception calculation)
  - **SpellcastingBuilder**: New builder for spellcasting class setup:
    - Standard spell slot creation from SpellSlotTable for prepared/known casters
    - Warlock Pact Magic support with proper slot progression
  - Wizard `done()` method now calls all builders in correct sequence
  - Comprehensive test suite for all builders (test_character_builders.py)
* Monster action template system for structured D&D 5e combat abilities:
  - MonsterActionTemplate model for structured actions with:
    - Attack properties: bonus, reach, range (normal/long), targets
    - Damage properties: dice, type, extra damage with type
    - Saving throw properties: DC, type, effect on save
    - Area of effect: shape (sphere, cube, cone, line, cylinder) and size
    - Recharge mechanics (5-6, 6, 4-6, short/long rest, daily uses)
  - MonsterMultiattack and MultiattackAction for complex attack patterns:
    - Links multiple actions with counts
    - Supports optional/grouped "or" options
  - LegendaryActionTemplate for legendary creatures:
    - Cost-based actions (1-3 actions)
    - Can link to existing action templates
  - LairActionTemplate for lair actions:
    - Saving throw support
    - Area of effect support
  - MonsterTrait for special abilities with optional uses/recharge
  - MonsterReaction for triggered abilities with conditions
  - New constants: ActionType, RechargeType, SaveType, SaveEffect, AreaShape
  - Added SLASHING and THUNDER to DamageType enum
  - Comprehensive test coverage (90+ new tests)
* Monster stat block system for D&D 5e SRD creatures:
  - MonsterSettings model with complete stat blocks:
    - Basic info: name, size, creature type, subtype, alignment
    - Combat stats: AC, HP (average and hit dice), speed (walk/fly/swim/climb/burrow)
    - Ability scores with computed modifiers (STR, DEX, CON, INT, WIS, CHA)
    - Saving throw proficiencies and skill bonuses
    - Damage resistances, immunities, and vulnerabilities
    - Condition immunities
    - Senses: darkvision, blindsight, tremorsense, truesight, passive perception
    - Languages and telepathy range
    - Challenge rating with XP lookup table
    - Proficiency bonus
    - Special traits, actions, reactions
    - Legendary actions and lair actions for legendary creatures
    - Spellcasting details for spellcasting monsters
  - Monster model for concrete combat instances with HP tracking
  - Monster constants: CreatureSize, CreatureType, Alignment, ChallengeRating, DamageType, SenseType, MovementType
  - SRD 5.2.1 monster fixtures (17 creatures across all CRs):
    - CR 0: Commoner
    - CR 1/8: Bandit
    - CR 1/4: Skeleton, Zombie, Wolf
    - CR 1/2: Orc
    - CR 1: Ghoul, Dire Wolf
    - CR 2: Ogre
    - CR 3: Owlbear, Minotaur
    - CR 5: Air Elemental
    - CR 6: Mage
    - CR 8: Assassin
    - CR 16: Iron Golem
    - CR 17: Adult Red Dragon (legendary with 3 legendary actions)
    - CR 21: Lich (legendary with lair actions and spellcasting)
  - Comprehensive test coverage (56 tests)
* Magic item framework for D&D 5e SRD items:
  - MagicItemSettings model for item definitions (rarity, type, attunement, effects)
  - MagicItem model for concrete item instances with charge tracking
  - Attunement model enforcing max 3 attunement slots per character
  - Rarity system: Common, Uncommon, Rare, Very Rare, Legendary
  - Item types: Armor, Potion, Ring, Rod, Scroll, Staff, Wand, Weapon, Wondrous
  - SRD 5.2.1 magic item fixtures (33 items):
    - +1/+2/+3 Weapons and Armor with attack/damage/AC bonuses
    - Potions of Healing (4 tiers with scaling healing)
    - Wands: Magic Missiles (7 charges), War Mage +1/+2/+3 (spell attack bonus)
    - Staffs: Healing, Power, Magi, Woodlands (with charges)
    - Rings: Protection, Spell Storing
    - Wondrous Items: Amulet of Health, Bag of Holding, Boots of Elvenkind/Speed, Bracers of Defense, Cloaks of Elvenkind/Protection, Gauntlets of Ogre Power, Headband of Intellect, Pearl of Power
  - Comprehensive test coverage (57 tests)
* Comprehensive armor fixture tests validating D&D 5e AC calculation rules:
  - Light armor (3): AC = base + full DEX modifier (Padded, Leather, Studded leather)
  - Medium armor (5): AC = base + DEX modifier (max 2) (Hide, Chain shirt, Scale mail, Breastplate, Half plate)
  - Heavy armor (4): AC = base with no DEX (Ring mail, Chain mail, Splint, Plate)
  - Shield: +2 AC bonus
  - Stealth disadvantage and strength requirement validation
* Complete SRD 5.2.1 weapon database with mastery properties:
  - All 37 SRD weapons now have mastery property assigned
  - Simple Melee (10): Club, Dagger, Greatclub, Handaxe, Javelin, Light hammer, Mace, Quarterstaff, Sickle, Spear
  - Simple Ranged (4): Light crossbow, Dart, Shortbow, Sling
  - Martial Melee (18): Battleaxe, Flail, Glaive, Greataxe, Greatsword, Halberd, Lance, Longsword, Maul, Morningstar, Pike, Rapier, Scimitar, Shortsword, Trident, War pick, Warhammer, Whip
  - Martial Ranged (5): Blowgun, Hand crossbow, Heavy crossbow, Longbow, Net
  - Corrected weapon stats per SRD 5.2.1: Lance damage (1d10), Trident damage (1d8/1d10), Greataxe weight (7 lb), Quarterstaff cost (0 gp)
  - Comprehensive test coverage for weapon fixture data
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
* Character wizard duplicate validation mixin now properly filters empty values and returns cleaned data
* Character wizard preview data (species, class, background, skills) now correctly serialized to JSON for JavaScript
* Armor disadvantage system now correctly applies penalties:
  - Fixed `_set_disadvantage()` to use `.filter().exists()` instead of `.get().exists()` (was throwing DoesNotExist)
  - Fixed ability type references to use `ability_type_id` since name is the primary key
  - Now calls `_set_disadvantage()` when adding armor (was missing)
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
* Removed Celery infrastructure: `game/tasks.py`, `role_play/celery.py`, worker process, and all Celery settings
* Removed `django_celery_beat` from INSTALLED_APPS
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
