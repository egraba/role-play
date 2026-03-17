# Management Command Suite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add 9 management commands across the `game` and `character` apps to support local testing workflows covering game lifecycle, character management, and DB inspection.

**Architecture:** Commands follow the existing pattern in `delete_character.py` and `populate_users.py`: Django `BaseCommand` subclasses with `add_arguments`/`handle`, raising `CommandError` on invalid input, using `self.stdout.write(self.style.SUCCESS(...))` on success. Tests use pytest + `call_command()` + `StringIO`. All game commands go in `game/management/commands/`, character commands in `character/management/commands/` (which already exists).

**Tech Stack:** Django 6.0 management commands, pytest-django, factory-boy, `django.core.management.call_command`

**Key domain facts:**
- `Game.state` is either `GameState.UNDER_PREPARATION` ("P") or `GameState.ONGOING` ("O")
- `Player.user` is `OneToOneField` — a user can be a player in at most one game
- `Character.increase_xp(amount)` handles XP + automatic level-up
- `Character` has `hp`, `max_hp` fields; validate `0 ≤ hp ≤ max_hp`
- `Master.game` is `OneToOneField` — one master per game (but a user can master multiple games)
- `GameFactory` is in `game/tests/factories.py`, `CharacterFactory` in `character/tests/factories.py`
- Existing test pattern: `pytestmark = pytest.mark.django_db`, `call_command("cmd_name", arg, stdout=out)`

---

### Task 1: `create_scenario` command

**Files:**
- Create: `game/management/commands/create_scenario.py`
- Create: `game/tests/management/__init__.py`
- Create: `game/tests/management/commands/__init__.py`
- Create: `game/tests/management/commands/test_create_scenario.py`

**Step 1: Write the failing tests**

```python
# game/tests/management/commands/test_create_scenario.py
from io import StringIO

import pytest
from django.core.management import call_command

from character.models.character import Character
from game.models.game import Game, Master, Player
from user.models import User

pytestmark = pytest.mark.django_db


def test_create_scenario_creates_users():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    assert User.objects.filter(username="thomas").exists()
    assert User.objects.filter(username="eric").exists()
    assert User.objects.filter(username="seb").exists()


def test_create_scenario_creates_characters_for_players_only():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    thomas = User.objects.get(username="thomas")
    eric = User.objects.get(username="eric")
    seb = User.objects.get(username="seb")
    assert not Character.objects.filter(user=thomas).exists()
    assert Character.objects.filter(user=eric).exists()
    assert Character.objects.filter(user=seb).exists()


def test_create_scenario_creates_game():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    assert Game.objects.filter(name="Scenario").exists()


def test_create_scenario_assigns_master():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    thomas = User.objects.get(username="thomas")
    game = Game.objects.get(name="Scenario")
    assert Master.objects.filter(user=thomas, game=game).exists()


def test_create_scenario_assigns_players():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    game = Game.objects.get(name="Scenario")
    eric = User.objects.get(username="eric")
    seb = User.objects.get(username="seb")
    assert Player.objects.filter(user=eric, game=game).exists()
    assert Player.objects.filter(user=seb, game=game).exists()


def test_create_scenario_is_idempotent():
    out = StringIO()
    call_command("create_scenario", stdout=out)
    call_command("create_scenario", stdout=out)
    assert Game.objects.filter(name="Scenario").count() == 1
    assert User.objects.filter(username="eric").count() == 1
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_create_scenario.py -v
```
Expected: FAIL — `No module named 'game.management.commands.create_scenario'`

**Step 3: Write the implementation**

```python
# game/management/commands/create_scenario.py
from django.core.management.base import BaseCommand

from character.models.character import Character
from character.tests.factories import CharacterFactory
from game.models.game import Game, Master, Player
from user.tests.factories import UserWithPasswordFactory


class Command(BaseCommand):
    help = "create full test scenario: users, characters, game, and players"

    def handle(self, *args: object, **options: object) -> None:
        thomas = UserWithPasswordFactory(username="thomas")
        eric = UserWithPasswordFactory(username="eric")
        seb = UserWithPasswordFactory(username="seb")

        if not Character.objects.filter(user=eric).exists():
            CharacterFactory(user=eric)
        if not Character.objects.filter(user=seb).exists():
            CharacterFactory(user=seb)

        game, _ = Game.objects.get_or_create(name="Scenario")
        Master.objects.get_or_create(user=thomas, game=game)

        eric_char = Character.objects.get(user=eric)
        Player.objects.get_or_create(user=eric, defaults={"game": game, "character": eric_char})

        seb_char = Character.objects.get(user=seb)
        Player.objects.get_or_create(user=seb, defaults={"game": game, "character": seb_char})

        self.stdout.write(self.style.SUCCESS("Successfully created scenario"))
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_create_scenario.py -v
```
Expected: 6 passed

**Step 5: Commit**

```bash
git add game/management/commands/create_scenario.py \
        game/tests/management/ \
        game/tests/management/commands/
git commit -m "feat: add create_scenario management command"
```

---

### Task 2: `create_game` command

**Files:**
- Create: `game/management/commands/create_game.py`
- Create: `game/tests/management/commands/test_create_game.py`

**Step 1: Write the failing tests**

```python
# game/tests/management/commands/test_create_game.py
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from faker import Faker

from game.models.game import Game, Master
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_create_game_creates_game():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    assert Game.objects.filter(master__user=user).exists()
    assert "Successfully created game" in out.getvalue()


def test_create_game_assigns_master():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    game = Game.objects.get(master__user=user)
    assert Master.objects.filter(user=user, game=game).exists()


def test_create_game_user_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("create_game", "nonexistent_user", stdout=out)


def test_create_game_prints_game_id():
    out = StringIO()
    user = UserFactory()
    call_command("create_game", user.username, stdout=out)
    game = Game.objects.get(master__user=user)
    assert str(game.id) in out.getvalue()
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_create_game.py -v
```

**Step 3: Write the implementation**

```python
# game/management/commands/create_game.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from game.models.game import Game, Master, Quest
from user.models import User


class Command(BaseCommand):
    help = "create a game for a master user"

    def add_arguments(self, parser):
        parser.add_argument("master", type=str, help="username of the game master")

    def handle(self, *args: object, **options: object) -> None:
        username = options["master"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        game = Game.objects.create(name=f"{username}'s game")
        Master.objects.create(user=user, game=game)
        Quest.objects.create(environment="A new adventure awaits.", game=game)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created game (id={game.id})")
        )
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_create_game.py -v
```

**Step 5: Commit**

```bash
git add game/management/commands/create_game.py \
        game/tests/management/commands/test_create_game.py
git commit -m "feat: add create_game management command"
```

---

### Task 3: `add_player` command

**Files:**
- Create: `game/management/commands/add_player.py`
- Create: `game/tests/management/commands/test_add_player.py`

**Step 1: Write the failing tests**

```python
# game/tests/management/commands/test_add_player.py
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from faker import Faker

from character.tests.factories import CharacterFactory
from game.models.game import Player
from game.tests.factories import GameFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_add_player_success():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("add_player", game.id, user.username, stdout=out)
    assert Player.objects.filter(user=user, game=game).exists()
    assert "Successfully added player" in out.getvalue()


def test_add_player_game_does_not_exist():
    out = StringIO()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("add_player", 99999, user.username, stdout=out)


def test_add_player_user_does_not_exist():
    out = StringIO()
    game = GameFactory()
    with pytest.raises(CommandError):
        call_command("add_player", game.id, "nonexistent", stdout=out)


def test_add_player_user_has_no_character():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("add_player", game.id, user.username, stdout=out)


def test_add_player_already_a_player():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    char = CharacterFactory(user=user)
    Player.objects.create(user=user, game=game, character=char)
    with pytest.raises(CommandError):
        call_command("add_player", game.id, user.username, stdout=out)
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_add_player.py -v
```

**Step 3: Write the implementation**

```python
# game/management/commands/add_player.py
from django.core.management.base import BaseCommand, CommandError

from character.models.character import Character
from game.models.game import Game, Player
from user.models import User


class Command(BaseCommand):
    help = "add a player to a game"

    def add_arguments(self, parser):
        parser.add_argument("game_id", type=int, help="game ID")
        parser.add_argument("username", type=str, help="username of the player")

    def handle(self, *args: object, **options: object) -> None:
        try:
            game = Game.objects.get(id=options["game_id"])
        except Game.DoesNotExist as exc:
            raise CommandError(f"game id={options['game_id']} doesn't exist") from exc

        username = options["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        try:
            character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            raise CommandError(f"{username=} has no character") from exc

        if Player.objects.filter(user=user).exists():
            raise CommandError(f"{username=} is already a player in a game")

        Player.objects.create(user=user, game=game, character=character)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully added player {username} to game {game.id}")
        )
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_add_player.py -v
```

**Step 5: Commit**

```bash
git add game/management/commands/add_player.py \
        game/tests/management/commands/test_add_player.py
git commit -m "feat: add add_player management command"
```

---

### Task 4: `start_game` command

**Files:**
- Create: `game/management/commands/start_game.py`
- Create: `game/tests/management/commands/test_start_game.py`

**Step 1: Write the failing tests**

```python
# game/tests/management/commands/test_start_game.py
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from game.constants.game import GameState
from game.tests.factories import GameFactory

pytestmark = pytest.mark.django_db


def test_start_game_sets_state_ongoing():
    out = StringIO()
    game = GameFactory()
    call_command("start_game", game.id, stdout=out)
    game.refresh_from_db()
    assert game.state == GameState.ONGOING
    assert "Successfully started game" in out.getvalue()


def test_start_game_sets_start_date():
    out = StringIO()
    game = GameFactory()
    call_command("start_game", game.id, stdout=out)
    game.refresh_from_db()
    assert game.start_date is not None


def test_start_game_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("start_game", 99999, stdout=out)


def test_start_game_already_ongoing():
    out = StringIO()
    game = GameFactory(state=GameState.ONGOING)
    with pytest.raises(CommandError):
        call_command("start_game", game.id, stdout=out)
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_start_game.py -v
```

**Step 3: Write the implementation**

```python
# game/management/commands/start_game.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from game.constants.game import GameState
from game.models.game import Game


class Command(BaseCommand):
    help = "start a game (set state to ongoing)"

    def add_arguments(self, parser):
        parser.add_argument("game_id", type=int, help="game ID")

    def handle(self, *args: object, **options: object) -> None:
        try:
            game = Game.objects.get(id=options["game_id"])
        except Game.DoesNotExist as exc:
            raise CommandError(f"game id={options['game_id']} doesn't exist") from exc

        if game.state == GameState.ONGOING:
            raise CommandError(f"game id={game.id} is already ongoing")

        game.state = GameState.ONGOING
        game.start_date = timezone.now()
        game.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully started game {game.id}"))
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_start_game.py -v
```

**Step 5: Commit**

```bash
git add game/management/commands/start_game.py \
        game/tests/management/commands/test_start_game.py
git commit -m "feat: add start_game management command"
```

---

### Task 5: `list_games` command

**Files:**
- Create: `game/management/commands/list_games.py`
- Create: `game/tests/management/commands/test_list_games.py`

**Step 1: Write the failing tests**

```python
# game/tests/management/commands/test_list_games.py
from io import StringIO

import pytest
from django.core.management import call_command

from game.tests.factories import GameFactory

pytestmark = pytest.mark.django_db


def test_list_games_shows_game_id():
    out = StringIO()
    game = GameFactory()
    call_command("list_games", stdout=out)
    assert str(game.id) in out.getvalue()


def test_list_games_shows_game_name():
    out = StringIO()
    game = GameFactory()
    call_command("list_games", stdout=out)
    assert game.name in out.getvalue()


def test_list_games_shows_state():
    out = StringIO()
    GameFactory()
    call_command("list_games", stdout=out)
    assert "preparation" in out.getvalue().lower()


def test_list_games_no_games():
    out = StringIO()
    call_command("list_games", stdout=out)
    assert "No games" in out.getvalue()


def test_list_games_shows_master():
    out = StringIO()
    game = GameFactory()
    call_command("list_games", stdout=out)
    assert game.master.user.username in out.getvalue()
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_list_games.py -v
```

**Step 3: Write the implementation**

```python
# game/management/commands/list_games.py
from django.core.management.base import BaseCommand

from game.models.game import Game


class Command(BaseCommand):
    help = "list all games"

    def handle(self, *args: object, **options: object) -> None:
        games = Game.objects.select_related("master__user").prefetch_related("player_set")
        if not games.exists():
            self.stdout.write("No games found.")
            return

        self.stdout.write(
            f"{'ID':<6} {'Name':<30} {'State':<20} {'Master':<20} {'Players'}"
        )
        self.stdout.write("-" * 85)
        for game in games:
            master = game.master.user.username if hasattr(game, "master") else "-"
            player_count = game.player_set.count()
            self.stdout.write(
                f"{game.id:<6} {game.name:<30} {game.get_state_display():<20} {master:<20} {player_count}"
            )
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_list_games.py -v
```

**Step 5: Commit**

```bash
git add game/management/commands/list_games.py \
        game/tests/management/commands/test_list_games.py
git commit -m "feat: add list_games management command"
```

---

### Task 6: `game_summary` command

**Files:**
- Create: `game/management/commands/game_summary.py`
- Create: `game/tests/management/commands/test_game_summary.py`

**Step 1: Write the failing tests**

```python
# game/tests/management/commands/test_game_summary.py
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from game.models.game import Player
from game.tests.factories import GameFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_game_summary_shows_game_name():
    out = StringIO()
    game = GameFactory()
    call_command("game_summary", game.id, stdout=out)
    assert game.name in out.getvalue()


def test_game_summary_shows_master():
    out = StringIO()
    game = GameFactory()
    call_command("game_summary", game.id, stdout=out)
    assert game.master.user.username in out.getvalue()


def test_game_summary_shows_players():
    out = StringIO()
    game = GameFactory()
    user = UserFactory()
    char = CharacterFactory(user=user)
    Player.objects.create(user=user, game=game, character=char)
    call_command("game_summary", game.id, stdout=out)
    assert user.username in out.getvalue()


def test_game_summary_game_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("game_summary", 99999, stdout=out)
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_game_summary.py -v
```

**Step 3: Write the implementation**

```python
# game/management/commands/game_summary.py
from django.core.management.base import BaseCommand, CommandError

from game.models.combat import Combat
from game.models.game import Game


class Command(BaseCommand):
    help = "show a detailed summary of a game"

    def add_arguments(self, parser):
        parser.add_argument("game_id", type=int, help="game ID")

    def handle(self, *args: object, **options: object) -> None:
        try:
            game = Game.objects.select_related("master__user").prefetch_related(
                "player_set__user", "player_set__character"
            ).get(id=options["game_id"])
        except Game.DoesNotExist as exc:
            raise CommandError(f"game id={options['game_id']} doesn't exist") from exc

        self.stdout.write(f"Game: {game.name} (id={game.id})")
        self.stdout.write(f"State: {game.get_state_display()}")
        if game.start_date:
            self.stdout.write(f"Started: {game.start_date:%Y-%m-%d %H:%M}")

        master = game.master.user.username if hasattr(game, "master") else "-"
        self.stdout.write(f"Master: {master}")

        players = game.player_set.all()
        if players.exists():
            self.stdout.write("\nPlayers:")
            self.stdout.write(f"  {'Username':<20} {'Character':<20} {'HP':<12} {'XP'}")
            self.stdout.write("  " + "-" * 60)
            for player in players:
                char = player.character
                hp_display = f"{char.hp}/{char.max_hp}"
                self.stdout.write(
                    f"  {player.user.username:<20} {char.name:<20} {hp_display:<12} {char.xp}"
                )
        else:
            self.stdout.write("\nNo players.")

        active_combats = Combat.objects.filter(game=game, ended_at=None) if hasattr(Combat, 'ended_at') else Combat.objects.filter(game=game)
        combat_count = active_combats.count()
        self.stdout.write(f"\nActive combats: {combat_count}")
```

Note: Check `Combat` fields — if there's no `ended_at`, just show total combat count.

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest game/tests/management/commands/test_game_summary.py -v
```

**Step 5: Commit**

```bash
git add game/management/commands/game_summary.py \
        game/tests/management/commands/test_game_summary.py
git commit -m "feat: add game_summary management command"
```

---

### Task 7: `grant_xp` command

**Files:**
- Create: `character/management/commands/grant_xp.py`
- Create: `character/tests/management/commands/test_grant_xp.py`

**Step 1: Write the failing tests**

```python
# character/tests/management/commands/test_grant_xp.py
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_grant_xp_increases_xp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("grant_xp", user.username, "100", stdout=out)
    char.refresh_from_db()
    assert char.xp == 100
    assert "Successfully granted" in out.getvalue()


def test_grant_xp_user_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("grant_xp", "nonexistent", "100", stdout=out)


def test_grant_xp_user_has_no_character():
    out = StringIO()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("grant_xp", user.username, "100", stdout=out)


def test_grant_xp_invalid_amount():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("grant_xp", user.username, "0", stdout=out)
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest character/tests/management/commands/test_grant_xp.py -v
```

**Step 3: Write the implementation**

```python
# character/management/commands/grant_xp.py
from django.core.management.base import BaseCommand, CommandError

from character.models.character import Character
from user.models import User


class Command(BaseCommand):
    help = "grant XP to a character"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="username of the character owner")
        parser.add_argument("amount", type=int, help="XP amount to grant")

    def handle(self, *args: object, **options: object) -> None:
        username = options["username"]
        amount = options["amount"]

        if amount <= 0:
            raise CommandError("amount must be greater than 0")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        try:
            character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            raise CommandError(f"{username=} has no character") from exc

        character.increase_xp(amount)
        character.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully granted {amount} XP to {character.name} (total: {character.xp})"
            )
        )
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest character/tests/management/commands/test_grant_xp.py -v
```

**Step 5: Commit**

```bash
git add character/management/commands/grant_xp.py \
        character/tests/management/commands/test_grant_xp.py
git commit -m "feat: add grant_xp management command"
```

---

### Task 8: `set_hp` command

**Files:**
- Create: `character/management/commands/set_hp.py`
- Create: `character/tests/management/commands/test_set_hp.py`

**Step 1: Write the failing tests**

```python
# character/tests/management/commands/test_set_hp.py
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_set_hp_updates_hp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("set_hp", user.username, str(char.max_hp - 10), stdout=out)
    char.refresh_from_db()
    assert char.hp == char.max_hp - 10
    assert "Successfully set HP" in out.getvalue()


def test_set_hp_to_zero():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("set_hp", user.username, "0", stdout=out)


def test_set_hp_exceeds_max_hp():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("set_hp", user.username, str(char.max_hp + 1), stdout=out)


def test_set_hp_negative():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    with pytest.raises(CommandError):
        call_command("set_hp", user.username, "-1", stdout=out)


def test_set_hp_user_does_not_exist():
    out = StringIO()
    with pytest.raises(CommandError):
        call_command("set_hp", "nonexistent", "10", stdout=out)


def test_set_hp_user_has_no_character():
    out = StringIO()
    user = UserFactory()
    with pytest.raises(CommandError):
        call_command("set_hp", user.username, "10", stdout=out)
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest character/tests/management/commands/test_set_hp.py -v
```

**Step 3: Write the implementation**

```python
# character/management/commands/set_hp.py
from django.core.management.base import BaseCommand, CommandError

from character.models.character import Character
from user.models import User


class Command(BaseCommand):
    help = "set a character's current HP"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="username of the character owner")
        parser.add_argument("amount", type=int, help="HP value to set")

    def handle(self, *args: object, **options: object) -> None:
        username = options["username"]
        amount = options["amount"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise CommandError(f"{username=} doesn't exist") from exc

        try:
            character = Character.objects.get(user=user)
        except Character.DoesNotExist as exc:
            raise CommandError(f"{username=} has no character") from exc

        if amount < 0:
            raise CommandError("amount must be >= 0")
        if amount > character.max_hp:
            raise CommandError(f"amount exceeds max HP ({character.max_hp})")

        character.hp = amount
        character.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully set HP of {character.name} to {amount}/{character.max_hp}"
            )
        )
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest character/tests/management/commands/test_set_hp.py -v
```

**Step 5: Commit**

```bash
git add character/management/commands/set_hp.py \
        character/tests/management/commands/test_set_hp.py
git commit -m "feat: add set_hp management command"
```

---

### Task 9: `list_characters` command

**Files:**
- Create: `character/management/commands/list_characters.py`
- Create: `character/tests/management/commands/test_list_characters.py`

**Step 1: Write the failing tests**

```python
# character/tests/management/commands/test_list_characters.py
from io import StringIO

import pytest
from django.core.management import call_command

from character.tests.factories import CharacterFactory
from user.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_list_characters_shows_username():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    assert user.username in out.getvalue()


def test_list_characters_shows_character_name():
    out = StringIO()
    user = UserFactory()
    char = CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    assert char.name in out.getvalue()


def test_list_characters_shows_hp():
    out = StringIO()
    user = UserFactory()
    CharacterFactory(user=user)
    call_command("list_characters", stdout=out)
    output = out.getvalue()
    assert "/" in output  # hp/max_hp format


def test_list_characters_no_characters():
    out = StringIO()
    call_command("list_characters", stdout=out)
    assert "No characters" in out.getvalue()
```

**Step 2: Run tests to verify they fail**

```bash
doppler run -- uv run pytest character/tests/management/commands/test_list_characters.py -v
```

**Step 3: Write the implementation**

```python
# character/management/commands/list_characters.py
from django.core.management.base import BaseCommand

from character.models.character import Character


class Command(BaseCommand):
    help = "list all characters"

    def handle(self, *args: object, **options: object) -> None:
        characters = Character.objects.select_related("user", "species").order_by("user__username")
        if not characters.exists():
            self.stdout.write("No characters found.")
            return

        self.stdout.write(
            f"{'Username':<20} {'Character':<20} {'Species':<15} {'Level':<8} {'HP':<12} {'XP'}"
        )
        self.stdout.write("-" * 85)
        for char in characters:
            hp_display = f"{char.hp}/{char.max_hp}"
            species = char.species.name if char.species else "-"
            self.stdout.write(
                f"{char.user.username:<20} {char.name:<20} {species:<15} {char.level:<8} {hp_display:<12} {char.xp}"
            )
```

**Step 4: Run tests to verify they pass**

```bash
doppler run -- uv run pytest character/tests/management/commands/test_list_characters.py -v
```

**Step 5: Commit**

```bash
git add character/management/commands/list_characters.py \
        character/tests/management/commands/test_list_characters.py
git commit -m "feat: add list_characters management command"
```

---

### Task 10: Poe tasks + CHANGELOG

**Files:**
- Modify: `poe_tasks.toml`
- Modify: `CHANGELOG.md`

**Step 1: Add poe tasks**

In `poe_tasks.toml`, under the `# Management Commands` section, add after the existing `delete-combats` task:

```toml
[tasks.db-create-scenario]
help = "Create full test scenario: users, characters, game, and players"
cmd = "manage.py create_scenario"

[tasks.create-game]
help = "Create a game for a master user"
args = [{ name = "master", positional = true, required = true, help = "Master username" }]
cmd = "manage.py create_game ${master}"

[tasks.add-player]
help = "Add a player to a game"
args = [
    { name = "game_id", positional = true, required = true, help = "Game ID" },
    { name = "username", positional = true, required = true, help = "Player username" },
]
cmd = "manage.py add_player ${game_id} ${username}"

[tasks.start-game]
help = "Start a game (set state to ongoing)"
args = [{ name = "game_id", positional = true, required = true, help = "Game ID" }]
cmd = "manage.py start_game ${game_id}"

[tasks.grant-xp]
help = "Grant XP to a character"
args = [
    { name = "username", positional = true, required = true, help = "Username" },
    { name = "amount", positional = true, required = true, help = "XP amount" },
]
cmd = "manage.py grant_xp ${username} ${amount}"

[tasks.set-hp]
help = "Set a character's current HP"
args = [
    { name = "username", positional = true, required = true, help = "Username" },
    { name = "amount", positional = true, required = true, help = "HP value" },
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
args = [{ name = "game_id", positional = true, required = true, help = "Game ID" }]
cmd = "manage.py game_summary ${game_id}"
```

**Step 2: Update CHANGELOG.md**

Under `## Unreleased → ### Added`, append:

```
- Management commands: `create_scenario`, `create_game`, `add_player`, `start_game`, `list_games`, `game_summary`, `grant_xp`, `set_hp`, `list_characters` with matching poe tasks
```

**Step 3: Run full test suite**

```bash
doppler run -- uv run poe test
```
Expected: all tests pass

**Step 4: Commit**

```bash
git add poe_tasks.toml CHANGELOG.md
git commit -m "chore: add poe tasks and changelog for management command suite"
```

---

### Task 11: Push and open PR

```bash
git push -u origin feat/management-commands-suite
```

Then use `/commit-commands:commit-push-pr` skill or:

```bash
gh pr create --title "feat: management command suite for local testing" \
  --body "Adds 9 management commands covering game lifecycle, character management, and DB inspection. See docs/plans/2026-03-15-management-commands-suite-design.md."
```
