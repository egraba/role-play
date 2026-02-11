# Role-Play Application Architecture

A Django-based D&D 5e virtual tabletop with real-time WebSocket gameplay, AI-powered content generation, and comprehensive SRD 5.2.1 mechanics.

## Table of Contents

1. [Django App Structure](#django-app-structure)
2. [Character Module](#character-module)
3. [Game Module](#game-module)
4. [Service Layer](#service-layer)
5. [Real-Time Communication](#real-time-communication)
6. [Master/Player Roles](#masterplayer-roles)
7. [Key Technologies](#key-technologies)

---

## Django App Structure

```
role_play/
├── character/    # Character creation, spells, equipment, D&D mechanics
├── game/         # Game engine, combat, events, WebSocket
├── master/       # Campaign management
├── user/         # Custom user model
├── ai/           # Anthropic Claude integration
└── utils/        # Shared utilities (dice, channels)
```

### App Responsibilities

| App | Purpose |
|-----|---------|
| `character/` | Character sheets, spellcasting, equipment, skills, species, classes |
| `game/` | Game sessions, combat, events, real-time communication |
| `master/` | Campaign creation and configuration |
| `user/` | Authentication (extends Django's AbstractUser) |
| `ai/` | Quest enrichment via Claude API |

---

## Character Module

Located in `character/models/`. Implements D&D 5e SRD 5.2.1 rules.

### Core Character Model

**`Character`** (`character.py`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Unique identifier |
| `user` | OneToOne → User | Owning player |
| `species` | FK → Species | D&D 2024 species (formerly "race") |
| `level` | SmallInt | Character level (default: 1) |
| `hp`, `max_hp`, `temp_hp` | SmallInt | Hit points |
| `ac` | SmallInt | Armor class |
| `death_save_successes/failures` | SmallInt | Death save tracking |
| `background` | ChoiceField | Character background |
| `inventory` | OneToOne → Inventory | Equipment container |

**Key Properties:**
- `proficiency_bonus` = `(level - 1) // 4 + 2`
- `primary_class` / `class_level` - From CharacterClass junction
- `is_unconscious`, `is_dead`, `is_stable` - Death state checks

**HP Methods:** `take_damage()`, `heal()`, `add_temp_hp()`, `add_death_save_success/failure()`

### Class System (`classes.py`)

Supports multiclassing via junction table.

```
Class (D&D 5e class definition)
├── name: ClassName (PK)
├── hit_die, hp_first_level, hp_higher_levels
├── primary_ability: FK → AbilityType
├── saving_throws: M2M → AbilityType
├── armor_proficiencies, weapon_proficiencies: JSONField
└── features → ClassFeature (M2M)

CharacterClass (Junction - supports multiclassing)
├── character: FK → Character
├── klass: FK → Class
├── level: PositiveSmallInt
└── is_primary: Boolean
```

### Species System (`species.py`)

D&D 2024 terminology (replaces "Race").

```
Species
├── name: SpeciesName (PK) - DWARF, ELF, HALFLING, HUMAN
├── size, speed, darkvision
├── traits: M2M → SpeciesTrait
└── languages: M2M → Language
```

### Spellcasting System (`spells.py`)

Complete D&D 5e magic implementation.

```
SpellSettings (Spell definitions)
├── name (PK), level, school
├── casting_time, range, duration
├── components: JSONField (V, S, M)
├── concentration, ritual
├── description, higher_levels
└── classes: JSONField

CharacterSpellSlot (Slot tracking)
├── character, slot_level (1-9)
├── total, used
└── Methods: use_slot(), restore_slot(), restore_all()

WarlockSpellSlot (Pact Magic - short rest recovery)

Concentration (Active spell tracking)
├── character: OneToOne
├── spell: FK → SpellSettings
└── Methods: break_concentration(), start_concentration()

Spell (Known spells - spontaneous casters)
SpellPreparation (Prepared spells - prepared casters)
ClassSpellcasting (Class casting config)
```

### Equipment System (`equipment.py`)

```
Inventory
├── capacity, gp
├── weapons, armor, packs, gear, tools

WeaponSettings / Weapon
ArmorSettings / Armor
ToolSettings / Tool
GearSettings / Gear
PackSettings / Pack
```

### Additional Character Models

| Model | File | Purpose |
|-------|------|---------|
| `Ability`, `AbilityType` | `abilities.py` | STR, DEX, CON, INT, WIS, CHA |
| `Skill` | `skills.py` | All 18 D&D skills |
| `Feat`, `CharacterFeat` | `feats.py` | Feats and origin feats |
| `Condition`, `CharacterCondition` | `conditions.py` | Status conditions |
| `MagicItem`, `Attunement` | `magic_items.py` | Magic item tracking |
| `MonsterSettings`, `Monster` | `monsters.py` | Monster stat blocks |
| `SpellEffectTemplate`, `ActiveSpellEffect` | `spell_effects.py` | Spell effect tracking |

### Character Creation

Uses **Builder Pattern** in `character_attributes_builders.py`:

1. **BaseBuilder** - Initialize abilities, inventory
2. **SpeciesBuilder** - Apply species traits (size, speed, darkvision)
3. **ClassBuilder** - Class features, HP, proficiencies
4. **BackgroundBuilder** - Background traits, skills, tools, feats
5. **DerivedStatsBuilder** - AC, HP finalization
6. **SpellcastingBuilder** - Spell slots for caster classes

**SessionWizardView** (7 steps):
Species → Class → Abilities → Background → Skills → Equipment → Review

---

## Game Module

Located in `game/models/`. Manages game sessions and real-time gameplay.

### Game Model (`game.py`)

```
Game
├── name, campaign: FK → Campaign
├── state: UNDER_PREPARATION | ONGOING
└── Uses GameFlow FSM for state transitions

Master (OneToOne → Game, FK → User)
Player (FK → Game, OneToOne → User, FK → Character)
Actor (Abstract base for Master/Player)
```

### Event System

Polymorphic events using `InheritanceManager`. Event models (`events.py`) are pure data — fields and DB behavior only. Presentation and type-mapping logic are separated into dedicated modules.

**Architecture:**

| Module | Purpose |
|--------|---------|
| `models/events.py` | Event model classes (fields, DB behavior, `__str__`) |
| `constants/event_registry.py` | Maps Event subclass → `EventType` via `get_event_type(event)` |
| `presenters.py` | Maps Event subclass → display string via `format_event_message(event)` |

Both registries use lazy initialization (`_build_*()` functions with `None` sentinels) to avoid circular imports between models and constants.

**Base Event:**
- `game` → Game
- `author` → Actor
- `date`: Auto timestamp

**Event Categories:**

| Category | Event Types |
|----------|-------------|
| Core | `GameStart`, `UserInvitation`, `Message`, `QuestUpdate` |
| Rolls | `RollRequest`, `RollResponse`, `RollResult` |
| Combat Init | `CombatInitialization`, `CombatInitiativeRequest/Response/Result`, `CombatInitativeOrderSet` |
| Combat Flow | `CombatStarted`, `TurnStarted`, `TurnEnded`, `RoundEnded`, `CombatEnded`, `ActionTaken` |
| Spells | `SpellCast`, `SpellDamageDealt`, `SpellHealingReceived`, `SpellConditionApplied`, `SpellSavingThrow` |
| Concentration | `ConcentrationSaveRequired`, `ConcentrationSaveResult`, `ConcentrationBroken`, `ConcentrationStarted` |
| HP | `HPDamage`, `HPHeal`, `HPTemp`, `HPDeathSave` (raw dicts, no Event model) |
| Other | `DiceRoll` |

### Combat System (`combat.py`)

```
Combat
├── state: ROLLING_INITIATIVE | ACTIVE | ENDED
├── current_round, current_fighter, current_turn_index
├── Methods: start_combat(), advance_turn(), end_combat()

Fighter
├── player, character, combat
├── is_surprised, dexterity_check (initiative)

Turn
├── fighter, round
├── action_used, bonus_action_used, reaction_used
├── movement_used, movement_total
└── Methods: can_take_action(), remaining_movement()

TurnAction
├── turn, action_type (ACTION | BONUS_ACTION | REACTION)
├── action: CombatAction (ATTACK, CAST_SPELL, DASH, etc.)
└── target_fighter
```

---

## Service Layer

Centralized business logic in `game/services.py`.

### GameEventService

Primary service for event creation and broadcasting.

```python
class GameEventService:
    @staticmethod
    def get_author(game, user) → Master | Player

    @staticmethod
    def create_message(game, user, content, date) → Message

    @staticmethod
    def process_roll(game, player, date, roll_type) → RollResult
        # Creates RollResponse, RollResult, broadcasts to channel

    @staticmethod
    def process_combat_initiative_roll(game, player, date)
        # Rolls initiative, checks if all fighters ready
        # Starts combat immediately when ready (no Celery)
```

**Key Pattern:** Events are created and broadcast in a single transaction. No background workers - all processing is synchronous.

### DiceRollService

```python
class DiceRollService:
    @staticmethod
    def create_dice_roll(game, user, notation, rolls, total, purpose)
```

---

## Real-Time Communication

### WebSocket Consumer (`consumers.py`)

**`GameEventsConsumer`** (JsonWebsocketConsumer):

```python
connect()       # Join channel group: game_{id}_events
disconnect()    # Leave channel group
receive_json()  # Route client events to service layer
__getattr__()   # Catch-all for Django Channels event dispatch
```

Django Channels converts event type dots to underscores and calls the resulting method (e.g., `game.start` → `game_start`). Instead of defining individual handler methods for each event type, a `__getattr__` catch-all forwards all events via `send_json`.

Event routing:
- `CLIENT_SIDE` events → Save to DB via service → Broadcast
- `SERVER_SIDE` events → Forward to channel group

### Channel Utilities (`utils/channels.py`)

```python
build_event_payload(event)  # Build payload using registry + presenter
send_to_channel(event)      # Validate and broadcast to all clients
```

### Event Schema Validation (`schemas.py`)

```python
EventType (StrEnum)    # All event type constants
EventOrigin (IntFlag)  # CLIENT_SIDE | SERVER_SIDE
EventSchema (Pydantic) # Validates WebSocket messages
```

---

## Master/Player Roles

### Database Level

| Role | Model | Constraint |
|------|-------|------------|
| Master | `Master` | OneToOne → Game (one per game) |
| Player | `Player` | FK → Game (multiple per game) |

### Permissions (`game/views/mixins.py`)

```python
GameContextMixin:
    is_user_master()  # user == game.master.user
    is_user_player()  # user in game.player_set
```

### Capabilities

**Masters:**
- Create/update campaigns and quests
- Invite players, start game
- Request ability checks and saving throws
- Initiate and manage combat
- Use AI to enrich quest descriptions

**Players:**
- Create characters
- Join games when invited
- Send messages, respond to rolls
- Roll initiative, take combat actions

### Key Views

**Master Views** (`game/views/master.py`):
- `UserInviteView`, `GameStartView`, `QuestCreateView`
- `AbilityCheckRequestView`, `SavingThrowRequestView`
- `CombatCreateView`, `CombatAdvanceTurnView`, `CombatEndView`

**Player Views** (`game/views/player.py`):
- Roll responses, message sending

**Combat Views**:
- `views/action_panel.py` - Combat actions
- `views/attack.py` - Attack resolution
- `views/concentration.py` - Concentration saves
- `views/initiative.py` - Initiative tracking

**Character Views** (`character/views/`):
- `spells.py` - Spell management, casting
- `abilities.py` - Ability score assignment
- `hp.py` - HP management, death saves
- `skills.py` - Skill checks

---

## Key Technologies

| Technology | Purpose |
|------------|---------|
| Django 6.0 | Web framework |
| Django Channels | WebSocket support |
| Daphne | ASGI server |
| Redis | Channel layer backend |
| PostgreSQL | Database |
| HTMX | Dynamic UI updates |
| Pydantic | Event validation |
| django-htmx | HTMX integration |
| django-formtools | Multi-step wizard |
| viewflow.fsm | Game state machine |
| model-utils | Polymorphic inheritance |
| Anthropic Claude | AI content generation |

### D&D Mechanics

- **Dice**: `utils/dice.py` - Parsing "2d6+3" notation
- **Modifiers**: `(ability_score - 10) // 2`
- **Proficiency**: `(level - 1) // 4 + 2`
- **Advantage/Disadvantage**: Roll 2d20, take best/worst

---

## File Locations

### Configuration
- `role_play/settings/` - Django settings (base, local, ci, test, production)
- `role_play/urls.py` - URL routing
- `role_play/asgi.py` - ASGI configuration

### Models
- `character/models/` - Character system (~15 files)
- `game/models/` - Game/combat/events (3 files)
- `master/models.py` - Campaign
- `user/models.py` - User

### Business Logic
- `game/services.py` - Event and roll services
- `game/rolls.py` - Dice mechanics
- `game/flows.py` - Game state machine
- `game/presenters.py` - Event message formatting
- `game/constants/event_registry.py` - Event type mapping
- `character/character_attributes_builders.py` - Character creation

### Views
- `game/views/` - Game, combat, master, player views
- `character/views/` - Character, spell, HP, skill views

### Constants
- `character/constants/` - D&D rules data
- `game/constants/` - Event types, combat states

### Real-Time
- `game/consumers.py` - WebSocket consumer
- `game/schemas.py` - Event validation
- `utils/channels.py` - Broadcast utilities
