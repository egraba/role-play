# 🎲 role-play

**A modern web-based platform for playing tabletop RPGs with friends — anywhere, anytime.**

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Renovate enabled](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![CI status](https://github.com/egraba/role-play/actions/workflows/ci.yml/badge.svg)](https://github.com/egraba/role-play/actions)
[![codecov](https://codecov.io/gh/egraba/role-play/graph/badge.svg?token=Z3E788461G)](https://codecov.io/gh/egraba/role-play)

## ✨ Why role-play?

Tired of coordinating schedules, hauling books, and losing character sheets? **role-play** brings your tabletop adventures online with real-time gameplay, so you can focus on what matters: epic stories and unforgettable moments with your party.

### 🚀 Features

- **🎭 Character Management** — Create and customize characters with abilities, classes, races, skills, and equipment
- **⚔️ Real-time Combat** — Seamless turn-based combat with initiative tracking and dice rolls
- **🎲 Integrated Dice Rolling** — Roll dice directly in the game with automatic modifiers
- **🧙 Game Master Tools** — Powerful tools to run your campaigns, manage events, and guide the story
- **🤖 AI-Enhanced Narratives** — Enrich your quests with AI-generated descriptions powered by Claude
- **💬 Live Updates** — WebSocket-powered real-time interactions between players and the Game Master

> **Note:** This project is under active development. New features are being added regularly!

## 🛠️ Tech Stack

- **Backend:** Python 3.14, Django 5.2
- **Real-time:** Django Channels, WebSockets
- **Background Tasks:** Celery with Redis
- **AI:** Anthropic Claude API
- **Database:** PostgreSQL

## 🧑‍💻 Development

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

# Run database migrations
doppler run -- uv run poe db-migrate

# Start the development server
doppler run -- uv run poe dev-run
```

### Running Tests

```bash
doppler run -- uv run poe test          # Run all tests
doppler run -- uv run poe test-cov      # Run tests with coverage
```

## 📄 License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE.md).
