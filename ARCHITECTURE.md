# Role-Play Application Architecture

A Django-based D&D 5e role-playing game platform with real-time WebSocket communication, AI-powered content generation, and comprehensive game mechanics.

## Table of Contents

1. [Django App Structure](#django-app-structure)
2. [Character Models](#character-models)
3. [Game Models](#game-models)
4. [Game Logic](#game-logic)
5. [Master/Player Distinction](#masterplayer-distinction)
6. [Real-Time Communication](#real-time-communication)
7. [Key Technologies](#key-technologies)

---

## Django App Structure

The application is organized into 5 Django apps:

```
role_play/
├── character/    # Character creation and management
├── game/         # Core game engine and real-time communication
├── master/       # Campaign management
├── user/         # Custom user model
└── ai/           # AI-powered content generation
```

### `character/` - Character System

Manages character sheets with D&D 5e mechanics:
- Character creation via multi-step wizard
- Equipment and inventory management
- Ability scores, skills, proficiencies, and languages
- Race and class features

### `game/` - Game Engine

Core game session management:
- Games, players, masters, and events
- WebSocket support via Django Channels
- Celery tasks for async game logic
- Event-driven architecture with RPG mechanics
- Combat system with initiative tracking

### `master/` - Campaign Management

Campaign creation and configuration:
- Campaign synopsis, main conflict, objectives
- Templates for dungeon masters

### `user/` - Authentication

Custom user model extending Django's `AbstractUser`:
- Standard Django authentication integration
- Base for both masters and players

### `ai/` - Content Generation

Anthropic Claude integration:
- Quest generation and enrichment
- Uses `claude-3-5-sonnet-20241022`

---

## Character Models

Located in `character/models/`

### Core Character Model

**`Character`** - Main character entity (`character/models/character.py`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField (unique) | Character identifier |
| `user` | OneToOne → User | Owning player |
| `race` | ChoiceField | D&D race (Dwarf, Elf, Halfling, etc.) |
| `klass` | CharField | Class (Cleric, Fighter, Rogue, Wizard) |
| `level` | SmallInt | Current level (default: 1) |
| `xp` | Int | Experience points (default: 0) |
| `hp` / `max_hp` | SmallInt | Hit points |
| `ac` | SmallInt | Armor class |
| `proficiency_bonus` | SmallInt | Level-based bonus |
| `alignment` | ChoiceField | D&D alignment |
| `size` | ChoiceField | Size category |
| `speed` | SmallInt | Movement speed (feet) |
| `hit_dice` | CharField | e.g., "1d8" |
| `background` | ChoiceField | Character background |
| `personality_trait`, `ideal`, `bond`, `flaw` | TextField | RP details |

**Relationships:**
- M2M: `skills`, `abilities`, `languages`, `senses`
- OneToOne: `inventory` → Inventory

**Key Methods:**
- `strength`, `dexterity`, `constitution`, `intelligence`, `wisdom`, `charisma` - Property getters
- `increase_xp(xp)` - Handles XP gain and level progression
- `is_proficient(ability)` - Check saving throw proficiency
- `has_advantage()` / `has_disadvantage()` - Race-based modifiers

### Ability Models (`character/models/ability.py`)

**`AbilityType`** - D&D ability types
- `name` (PK): STR, DEX, CON, INT, WIS, CHA
- `description`: Ability description

**`Ability`** - Character's ability scores
- `ability_type` → AbilityType
- `score`: Raw score (3-20)
- `modifier`: Calculated modifier ((score - 10) / 2)

### Equipment & Inventory (`character/models/inventory.py`)

**`Inventory`**
- `capacity`: Weight/item capacity
- `gp`: Gold pieces

**Equipment Types** (each with Settings model for D&D specs):
- `Armor` / `ArmorSettings`
- `Weapon` / `WeaponSettings`
- `Pack` / `PackSettings`
- `Gear` / `GearSettings`
- `Tool` / `ToolSettings`

### Skills (`character/models/skill.py`)

**`Skill`**
- `name` (PK): Skill name (e.g., "Acrobatics")
- `ability_type` → AbilityType
- `description`

### Class System (`character/models/klass.py`)

**`Klass`** - TextChoices: CLERIC, FIGHTER, ROGUE, WIZARD

**`HitPoints`** - Class-specific HP mechanics

**`KlassFeature`** - Class features

**`KlassAdvancement`** - Proficiency progression by level

### Race Features (`character/models/race.py`)

**`Language`** - D&D languages with types and scripts

**`Sense`** - Racial senses/features (e.g., "Dwarven Resilience", "Fey Ancestry")

### Proficiencies (`character/models/proficiency.py`)

- `SavingThrowProficiency`
- `SkillProficiency`
- `ArmorProficiency`
- `WeaponProficiency`
- `ToolProficiency`

### Disadvantages (`character/models/disadvantage.py`)

- `AbilityCheckDisadvantage`
- `SavingThrowDisadvantage`
- `AttackRollDisadvantage`
- `SpellCastDisadvantage`

---

## Game Models

Located in `game/models/`

### Core Game Model (`game/models/game.py`)

**`Game`** - Central game session
- `name`: Game name
- `campaign` → Campaign
- `start_date`: When game started
- `state`: UNDER_PREPARATION or ONGOING
- Uses `GameFlow` FSM for state management

**`Quest`** - Game environment/scenario
- `environment`: Quest description (3000 chars)
- `game` → Game

### Actors (`game/models/game.py`)

**`Actor`** - Abstract base for game participants

**`Master`** - Dungeon Master
- `user` → User (FK)
- `game` → Game (OneToOne)
- Cannot be both Master and Player in same game

**`Player`** - Player participant
- `user` → User (OneToOne)
- `game` → Game (FK, multiple players per game)
- `character` → Character (OneToOne)

### Events (`game/models/events.py`)

Polymorphic event system using `InheritanceManager`:

**Base `Event`**
- `game` → Game
- `author` → Actor
- `date`: Auto timestamp

**Event Types:**
| Event | Description |
|-------|-------------|
| `GameStart` | Game started |
| `UserInvitation` | Player invited |
| `Message` | Chat message (100 chars) |
| `QuestUpdate` | Quest updated |
| `RollRequest` | Master requests roll |
| `RollResponse` | Player performs roll |
| `RollResult` | Roll outcome |
| `CombatInitialization` | Combat started |
| `CombatInitiativeRequest` | Initiative requested |
| `CombatInitiativeResponse` | Initiative rolled |
| `CombatInitiativeResult` | Initiative result |
| `CombatInitativeOrderSet` | Order determined |

### Combat System (`game/models/combat.py`)

**`Combat`** - Combat session
- `game` → Game
- `get_initiative_order()`: Fighters sorted by DEX check

**`Round`** - Combat round
- `combat` → Combat

**`Turn`** - Individual turn
- `player` → Player
- `round` → Round
- `move`: Movement
- `action`: CombatAction

**`Fighter`** - Character in combat
- `player` → Player
- `character` → Character
- `is_surprised`: Boolean
- `combat` → Combat
- `dexterity_check`: Initiative roll result

---

## Game Logic

### State Machine (`game/flows.py`)

**`GameFlow`** - Finite State Machine (viewflow.fsm)
```
States: UNDER_PREPARATION → ONGOING
Transition: start() [requires ≥2 players]
```

### Roll Mechanics (`game/rolls.py`)

**`perform_roll(player, request)`**
- Roll d20 + ability modifier + proficiency bonus
- Supports advantage/disadvantage
- Compares against difficulty class
- Returns (score, SUCCESS/FAILURE)

**`perform_combat_initiative_roll(fighter)`**
- d20 + DEX modifier

### Character Building (`character/character_attributes_builders.py`)

Builder pattern for character creation:

1. **`BaseBuilder`** - Initialize abilities, inventory
2. **`RaceBuilder`** - Apply racial traits
3. **`KlassBuilder`** - Apply class features
4. **`BackgroundBuilder`** - Apply background

### Background Processing (`game/tasks.py`)

Celery tasks:
- `send_mail()` - Email notifications
- `store_message()` - Save chat messages
- `process_roll()` - Handle ability checks/saving throws
- `process_combat_initiative_roll()` - Handle initiative
- `check_combat_roll_initiative_complete()` - Periodic check for combat readiness

### Command Pattern (`game/commands.py`)

WebSocket command handlers:
- `ProcessMessageCommand` - Store chat
- `AbilityCheckResponseCommand` - Respond to ability check
- `SavingThrowResponseCommand` - Respond to saving throw
- `CombatInitiativeResponseCommand` - Roll initiative

---

## Master/Player Distinction

### Database Level

| Role | Model | Relationship | Constraint |
|------|-------|--------------|------------|
| Master | `Master` | OneToOne → Game | One per game |
| Player | `Player` | FK → Game | Multiple per game |

### Permission System (`game/views/mixins.py`)

**`GameContextMixin`**:
```python
is_user_master()  # Check if user == game.master.user
is_user_player()  # Check if user in game.player_set
```

### Role Capabilities

**Masters can:**
- Create/update campaigns
- Invite players to game
- Start game (state transition)
- Create/update quests
- Request ability checks and saving throws
- Initiate combat
- Use AI to enrich quest descriptions

**Players can:**
- Create characters
- Join games (when invited)
- Send chat messages
- Respond to roll requests
- Roll initiative in combat
- View game events and quest

### Master-Only Views

Located in `game/views/master.py`:
- `UserInviteView` - Invite players
- `UserInviteConfirmView` - Confirm invitation
- `GameStartView` - Start game
- `QuestCreateView` - Create/update quest
- `AbilityCheckRequestView` - Request rolls
- `CombatCreateView` - Initialize combat

---

## Real-Time Communication

### WebSocket Consumer (`game/consumers.py`)

**`GameEventsConsumer`**
```python
connect()       # Join game channel (game_{id}_events)
disconnect()    # Leave game channel
receive_json()  # Process incoming event
```

Event handlers:
- `message()` - Chat message
- `game_start()` - Game started
- `quest_update()` - Quest updated
- `ability_check_request()` / `ability_check_response()`
- `saving_throw_request()` / `saving_throw_response()`
- `combat_*` events

### Channel Utilities (`game/utils/channels.py`)

```python
send_to_channel(game, event_type, event)  # Broadcast to group
```

### Event Enrichers (`game/event_enrichers.py`)

Transform events before broadcasting:
- `MessageEnricher` - Format with author
- `RollResponseEnricher` - Format roll result
- `CombatInitiativeResponseEnricher` - Format initiative

---

## Key Technologies

| Technology | Purpose |
|------------|---------|
| Django Channels | WebSocket support |
| Redis | Channel layer & Celery broker |
| Celery | Background task processing |
| django-celery-beat | Periodic tasks |
| Anthropic Claude | AI content generation |
| PostgreSQL | Database |
| viewflow.fsm | Game state machine |
| django-formtools | Multi-step character wizard |
| model-utils | Polymorphic Event inheritance |

### D&D Mechanics Implementation

- **Dice**: `utils/dice.py` - DiceString class ("d20", "2d6+3")
- **Modifiers**: (score - 10) / 2 (rounded down)
- **Advantage/Disadvantage**: Roll twice, take better/worse
- **Proficiency**: Standard D&D progression by level
- **Difficulty Class**: 5-30 scale

---

## Key File Locations

### Configuration
- `role_play/settings/base.py` - Django settings
- `role_play/urls.py` - URL routing
- `role_play/asgi.py` - ASGI for Channels

### Models
- `character/models/` - Character system (9 files)
- `game/models/` - Game session system (3 files)
- `master/models.py` - Campaign model
- `user/models.py` - User model

### Views
- `character/views/character.py` - Character CRUD
- `game/views/common.py` - Game display views
- `game/views/master.py` - Master control views

### Game Logic
- `game/rolls.py` - Dice roll mechanics
- `game/tasks.py` - Celery tasks
- `game/commands.py` - WebSocket commands
- `game/flows.py` - Game state machine
- `game/consumers.py` - WebSocket consumer

### Constants & Rules
- `character/constants/` - D&D rules data
- `game/constants/` - Game state constants

### Utilities
- `utils/dice.py` - Dice rolling
- `game/utils/` - Caching, channels, emails
- `character/utils/` - Equipment, cache
