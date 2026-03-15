# Management Command Suite Design

**Date**: 2026-03-15

## Overview

Add a suite of management commands to support local testing workflows, covering game lifecycle, character management, and inspection. These complement the existing `populate_users` command without replacing it.

## Typical Workflow

```bash
poe db-populate-users       # create users + characters, no game → test game creation UI
# — or skip straight to —
poe db-create-scenario      # full ready-to-play state (users + game + players)
poe start-game <id>         # advance game to ongoing
```

## Commands

### Game lifecycle — `game/management/commands/`

| Command | Args | Behaviour |
|---|---|---|
| `create_scenario` | — | Creates thomas (DM), eric + seb (with characters), a game named "Scenario" with thomas as master, eric and seb as players. Idempotent via `get_or_create`. |
| `create_game` | `<master>` | Creates a new game (+ quest) for the given master username. Errors if user does not exist. |
| `add_player` | `<game_id> <username>` | Links a user and their character to a game as a Player. Errors if user has no character or is already a player. |
| `start_game` | `<game_id>` | Sets `state=ONGOING` and `start_date=now()`. Errors if game is already ongoing. |
| `list_games` | — | Prints a table: ID, name, state, master username, player count. |
| `game_summary` | `<game_id>` | Prints master, players + characters (hp/max_hp, xp), and active combat status. |

### Character management — `character/management/commands/`

| Command | Args | Behaviour |
|---|---|---|
| `grant_xp` | `<username> <amount>` | Adds XP to the user's character. Errors if user has no character or amount ≤ 0. |
| `set_hp` | `<username> <amount>` | Sets character `hp`. Validates 0 ≤ amount ≤ max_hp. |
| `list_characters` | — | Prints a table: username, character name, species, level, hp/max_hp, xp. |

## Poe Tasks

Added under the `# Management Commands` section of `poe_tasks.toml`:

```toml
[tasks.db-create-scenario]
help = "Create full test scenario: users, characters, game, and players"
cmd = "manage.py create_scenario"

[tasks.create-game]
help = "Create a game for a master user"
args = [{ name = "master", positional = true, required = true }]
cmd = "manage.py create_game ${master}"

[tasks.add-player]
help = "Add a player to a game"
args = [
    { name = "game_id", positional = true, required = true },
    { name = "username", positional = true, required = true },
]
cmd = "manage.py add_player ${game_id} ${username}"

[tasks.start-game]
help = "Start a game (set state to ongoing)"
args = [{ name = "game_id", positional = true, required = true }]
cmd = "manage.py start_game ${game_id}"

[tasks.grant-xp]
help = "Grant XP to a character"
args = [
    { name = "username", positional = true, required = true },
    { name = "amount", positional = true, required = true },
]
cmd = "manage.py grant_xp ${username} ${amount}"

[tasks.set-hp]
help = "Set a character's current HP"
args = [
    { name = "username", positional = true, required = true },
    { name = "amount", positional = true, required = true },
]
cmd = "manage.py set_hp ${username} ${amount}"

[tasks.list-characters]
help = "List all characters"
cmd = "manage.py list_characters"

[tasks.list-games]
help = "List all games"
cmd = "manage.py list_games"

[tasks.game-summary]
help = "Show a detailed summary of a game"
args = [{ name = "game_id", positional = true, required = true }]
cmd = "manage.py game_summary ${game_id}"
```

## Kept

- `db-populate-users` — baseline state for testing the game creation UI flow.

## Error Handling Convention

All commands follow the existing pattern: raise `CommandError` for invalid input, use `self.stdout.write(self.style.SUCCESS(...))` on success.
