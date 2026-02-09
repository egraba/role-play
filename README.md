# role-play

**A modern web-based platform for playing tabletop RPGs with friends — anywhere, anytime.**

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![CI status](https://github.com/egraba/role-play/actions/workflows/ci.yml/badge.svg)](https://github.com/egraba/role-play/actions)
[![codecov](https://codecov.io/gh/egraba/role-play/graph/badge.svg?token=Z3E788461G)](https://codecov.io/gh/egraba/role-play)
[![Fly Deploy](https://github.com/egraba/role-play/actions/workflows/fly-deploy.yml/badge.svg)](https://github.com/egraba/role-play/actions/workflows/fly-deploy.yml)

---

## Why role-play?

Tired of coordinating schedules, hauling books, and losing character sheets? **role-play** brings your tabletop adventures online with real-time gameplay, so you can focus on what matters: epic stories and unforgettable moments with your party.

## Features

- **Character Management** — Create and customize characters with abilities, classes, races, skills, and equipment
- **Real-time Combat** — Seamless turn-based combat with initiative tracking and dice rolls
- **Integrated Dice Rolling** — Roll dice directly in the game with automatic modifiers
- **Game Master Tools** — Powerful tools to run your campaigns, manage events, and guide the story
- **AI-Enhanced Narratives** — Enrich your quests with AI-generated descriptions powered by Claude
- **Live Updates** — WebSocket-powered real-time interactions between players and the Game Master

> **Note:** This project is under active development. New features are being added regularly!

## How It Works

### Roles

**Game Master (DM)**
- Creates and manages campaigns with synopsis, conflicts, and objectives
- Invites players to join games
- Controls game flow: starts the game, updates quests, initiates combat
- Requests ability checks and saving throws from players
- Uses AI to generate rich quest descriptions

**Players**
- Create characters with race, class, background, and equipment
- Join games when invited by the Game Master
- Respond to ability checks, saving throws, and initiative rolls
- Participate in real-time chat and combat

### Game Flow

1. **Campaign Setup** — Game Master creates a campaign and game session
2. **Character Creation** — Players create characters via a guided wizard
3. **Invitations** — Game Master invites players (minimum 2 required to start)
4. **Gameplay** — Real-time quests, rolls, and combat via WebSocket
5. **Combat** — Initiative-based turn system with D&D 5e mechanics

## D&D Rules Reference

This project implements tabletop RPG gameplay based on the **Dungeons & Dragons 5th Edition System Reference Document (SRD) version 5.2**, available under the Creative Commons Attribution 4.0 International License (CC-BY-4.0) by Wizards of the Coast.

The SRD 5.2 includes content from the 2024 D&D core rulebooks:
- Updated class rules and progression
- New species (Goliaths and Orcs)
- Enhanced feats and backgrounds
- Weapon Mastery mechanics
- Updated monster statistics

**Reference:** [D&D Systems Reference Document 5.2](https://media.dndbeyond.com/compendium-images/srd/5.2/SRD_CC_v5.2.1.pdf)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.14, Django 5.2 |
| Real-time | Django Channels, WebSockets |
| Background Tasks | Celery with Redis |
| AI | Anthropic Claude API |
| Database | PostgreSQL |
| Task Runner | [Poe the Poet](https://github.com/nat-n/poethepoet) |

## Project Structure

```
role_play/
├── character/    # Character creation, abilities, inventory, equipment
├── game/         # Game engine, events, combat, WebSocket consumers
├── master/       # Campaign management
├── user/         # Custom user authentication
└── ai/           # Claude AI integration for content generation
```

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Development

### Prerequisites

- Python 3.14+
- PostgreSQL
- Redis
- [uv](https://github.com/astral-sh/uv) — Fast Python package installer
- [Doppler](https://www.doppler.com/) — Secrets management

### Getting Started

```bash
# Clone the repository
git clone https://github.com/egraba/role-play.git
cd role-play

# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Set up database (migrate + load fixtures)
doppler run -- poe db-setup

# Start the development server
doppler run -- poe run

# In a separate terminal, start Celery worker
doppler run -- poe worker
```

### Common Tasks

```bash
poe run          # Start development server
poe worker       # Start Celery worker
poe test         # Run tests
poe ci           # Run full CI locally (tests + lint + typecheck)
poe db-setup     # Set up database (migrate + load fixtures)
```

Run `poe --help` to see all available tasks.

## Contributing

For AI coding assistants working on this project, see [AGENTS.md](AGENTS.md) for guidelines and conventions.

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE.md).

Game rules and mechanics are based on the D&D 5th Edition SRD 5.2, licensed under CC-BY-4.0 by Wizards of the Coast.
