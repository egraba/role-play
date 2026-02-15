"""Tests for the attack modal views."""

from unittest.mock import patch

import pytest
from django.urls import reverse

from character.tests.factories import CharacterFactory
from equipment.constants.equipment import WeaponName, WeaponType
from equipment.models.equipment import Weapon, WeaponSettings
from game.attack import AttackResult
from game.models.combat import Combat
from game.models.game import Player
from user.tests.factories import UserFactory

from ..factories import FighterFactory, GameFactory


pytestmark = pytest.mark.django_db


class TestAttackModalView:
    """Tests for AttackModalView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        # Create first user/character/player (current turn)
        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Add a weapon to character1's inventory
        weapon_settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.LONGSWORD,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 15,
                "damage": "1d8",
                "weight": 3,
                "properties": "versatile",
            },
        )
        weapon = Weapon.objects.create(
            settings=weapon_settings,
            inventory=character1.inventory,
        )

        # Create second user/character/player (target)
        user2 = UserFactory()
        character2 = CharacterFactory(user=user2)
        character2.ac = 15
        character2.save()
        player2 = Player.objects.create(user=user2, game=game, character=character2)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        fighter2 = FighterFactory(
            combat=combat,
            player=player2,
            character=character2,
            dexterity_check=10,
        )
        combat.start_combat()
        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "player2": player2,
            "fighter1": fighter1,
            "fighter2": fighter2,
            "weapon": weapon,
        }

    def test_modal_returns_html(self, client, active_combat_setup):
        """Test attack modal returns HTML content."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "attack-modal" in response.content.decode()

    def test_modal_shows_target_dropdown(self, client, active_combat_setup):
        """Test modal displays target selection dropdown."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Select Target" in content
        # Should show the other fighter as a target
        assert setup["fighter2"].character.name in content

    def test_modal_excludes_self_from_targets(self, client, active_combat_setup):
        """Test modal does not show attacker as a target option."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        # Count occurrences - fighter1's name should not be in target dropdown
        # but might appear elsewhere in the page
        assert f'value="{setup["fighter1"].id}"' not in content

    def test_modal_shows_advantage_toggle(self, client, active_combat_setup):
        """Test modal displays advantage/disadvantage toggle."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Advantage" in content
        assert "Disadvantage" in content
        assert "Normal" in content

    def test_modal_shows_attack_bonus(self, client, active_combat_setup):
        """Test modal displays attack bonus."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Attack Bonus" in content

    def test_modal_shows_weapon_selector(self, client, active_combat_setup):
        """Test modal displays weapon selection dropdown."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        content = response.content.decode()
        assert "Select Weapon" in content
        assert "Longsword" in content

    # Note: test_modal_requires_login is not implemented because GameContextMixin
    # runs setup() before LoginRequiredMixin can redirect, causing errors with
    # anonymous users. This would require refactoring the mixin order.

    def test_modal_forbidden_when_not_your_turn(self, client, active_combat_setup):
        """Test modal returns 403 when not your turn."""
        setup = active_combat_setup
        # Player2 is not current fighter
        client.force_login(setup["player2"].user)

        url = reverse(
            "combat-attack-modal",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.get(url)

        assert response.status_code == 403


class TestAttackRollView:
    """Tests for AttackRollView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Add a weapon to character1's inventory
        weapon_settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.LONGSWORD,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 15,
                "damage": "1d8",
                "weight": 3,
                "properties": "versatile",
            },
        )
        weapon = Weapon.objects.create(
            settings=weapon_settings,
            inventory=character1.inventory,
        )

        user2 = UserFactory()
        character2 = CharacterFactory(user=user2)
        character2.ac = 15
        character2.save()
        player2 = Player.objects.create(user=user2, game=game, character=character2)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        fighter2 = FighterFactory(
            combat=combat,
            player=player2,
            character=character2,
            dexterity_check=10,
        )
        combat.start_combat()
        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "player2": player2,
            "fighter1": fighter1,
            "fighter2": fighter2,
            "weapon": weapon,
        }

    @patch("game.views.attack.resolve_attack")
    def test_attack_roll_returns_result(
        self, mock_resolve, client, active_combat_setup
    ):
        """Test attack roll returns result HTML."""
        mock_resolve.return_value = AttackResult(
            attack_roll=18,
            natural_roll=15,
            attack_modifier=3,
            target_ac=15,
            is_hit=True,
            is_critical_hit=False,
            is_critical_miss=False,
            damage=7,
            damage_dice="1d8",
            damage_modifier=3,
            attacker_name="Attacker",
            target_name="Target",
            weapon_name="Longsword",
            ability_used="STR",
            damage_rolls=[4],
        )
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "roll_modifier": "normal",
            },
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "attack-modal" in content
        # Should show result (HIT or MISS)
        assert "HIT" in content or "MISS" in content

    @patch("game.views.attack.resolve_attack")
    def test_attack_roll_shows_critical_hit(
        self, mock_resolve, client, active_combat_setup
    ):
        """Test natural 20 shows critical hit."""
        mock_resolve.return_value = AttackResult(
            attack_roll=25,
            natural_roll=20,
            attack_modifier=5,
            target_ac=15,
            is_hit=True,
            is_critical_hit=True,
            is_critical_miss=False,
            damage=12,
            damage_dice="1d8",
            damage_modifier=3,
            attacker_name="Attacker",
            target_name="Target",
            weapon_name="Longsword",
            ability_used="STR",
            damage_rolls=[8],
        )
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "roll_modifier": "normal",
            },
        )

        content = response.content.decode()
        assert "CRITICAL HIT" in content
        assert "critical-hit" in content

    @patch("game.views.attack.resolve_attack")
    def test_attack_roll_shows_critical_miss(
        self, mock_resolve, client, active_combat_setup
    ):
        """Test natural 1 shows critical miss."""
        mock_resolve.return_value = AttackResult(
            attack_roll=4,
            natural_roll=1,
            attack_modifier=3,
            target_ac=15,
            is_hit=False,
            is_critical_hit=False,
            is_critical_miss=True,
            damage=0,
            damage_dice="1d8",
            damage_modifier=3,
            attacker_name="Attacker",
            target_name="Target",
            weapon_name="Longsword",
            ability_used="STR",
            damage_rolls=[],
        )
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "roll_modifier": "normal",
            },
        )

        content = response.content.decode()
        assert "CRITICAL MISS" in content
        assert "critical-miss" in content

    @patch("game.views.attack.resolve_attack")
    def test_attack_roll_with_advantage(
        self, mock_resolve, client, active_combat_setup
    ):
        """Test advantage passes advantage=True to resolve_attack."""
        mock_resolve.return_value = AttackResult(
            attack_roll=18,
            natural_roll=15,
            second_natural_roll=10,
            attack_modifier=3,
            target_ac=15,
            is_hit=True,
            is_critical_hit=False,
            is_critical_miss=False,
            damage=7,
            damage_dice="1d8",
            damage_modifier=3,
            attacker_name="Attacker",
            target_name="Target",
            weapon_name="Longsword",
            ability_used="STR",
            damage_rolls=[4],
        )
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "roll_modifier": "advantage",
            },
        )

        content = response.content.decode()
        assert "Advantage" in content
        # Verify resolve_attack was called with advantage=True
        mock_resolve.assert_called_once()
        call_kwargs = mock_resolve.call_args
        assert call_kwargs.kwargs.get("advantage") is True

    @patch("game.views.attack.resolve_attack")
    def test_attack_roll_with_disadvantage(
        self, mock_resolve, client, active_combat_setup
    ):
        """Test disadvantage passes disadvantage=True to resolve_attack."""
        mock_resolve.return_value = AttackResult(
            attack_roll=13,
            natural_roll=10,
            second_natural_roll=15,
            attack_modifier=3,
            target_ac=15,
            is_hit=False,
            is_critical_hit=False,
            is_critical_miss=False,
            damage=0,
            damage_dice="1d8",
            damage_modifier=3,
            attacker_name="Attacker",
            target_name="Target",
            weapon_name="Longsword",
            ability_used="STR",
            damage_rolls=[],
        )
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "roll_modifier": "disadvantage",
            },
        )

        content = response.content.decode()
        assert "Disadvantage" in content
        # Verify resolve_attack was called with disadvantage=True
        mock_resolve.assert_called_once()
        call_kwargs = mock_resolve.call_args
        assert call_kwargs.kwargs.get("disadvantage") is True

    def test_attack_roll_invalid_target(self, client, active_combat_setup):
        """Test attack roll with invalid target returns error."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-attack-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": 99999,  # Invalid
                "weapon_id": setup["weapon"].id,
                "roll_modifier": "normal",
            },
        )

        # Should return the modal with an error or target selection
        assert response.status_code == 200

    # Note: test_attack_roll_requires_login is not implemented because GameContextMixin
    # runs setup() before LoginRequiredMixin can redirect, causing errors with
    # anonymous users. This would require refactoring the mixin order.


class TestDamageRollView:
    """Tests for DamageRollView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Add a weapon to character1's inventory
        weapon_settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.LONGSWORD,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 15,
                "damage": "1d8",
                "weight": 3,
                "properties": "versatile",
            },
        )
        weapon = Weapon.objects.create(
            settings=weapon_settings,
            inventory=character1.inventory,
        )

        user2 = UserFactory()
        character2 = CharacterFactory(user=user2)
        character2.ac = 15
        character2.hp = 30
        character2.max_hp = 30
        character2.save()
        player2 = Player.objects.create(user=user2, game=game, character=character2)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        fighter2 = FighterFactory(
            combat=combat,
            player=player2,
            character=character2,
            dexterity_check=10,
        )
        combat.start_combat()
        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "player2": player2,
            "fighter1": fighter1,
            "fighter2": fighter2,
            "weapon": weapon,
        }

    def test_damage_roll_returns_result(self, client, active_combat_setup):
        """Test damage roll returns result HTML."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-damage-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "is_critical": "false",
                "natural_roll": 15,
                "total_roll": 18,
                "attack_bonus": 3,
                "total_damage": 7,
                "damage_rolls": "5",
                "damage_formula": "1d8 (5) + 2",
            },
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert "damage" in content.lower()
        assert "Apply" in content

    def test_damage_roll_shows_dice(self, client, active_combat_setup):
        """Test damage roll shows individual dice values."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-damage-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "is_critical": "false",
                "natural_roll": 15,
                "total_roll": 18,
                "attack_bonus": 3,
                "total_damage": 8,
                "damage_rolls": "6",
                "damage_formula": "1d8 (6) + 2",
            },
        )

        content = response.content.decode()
        assert "damage-die" in content

    def test_critical_doubles_dice(self, client, active_combat_setup):
        """Test critical hit shows double dice."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-damage-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "weapon_id": setup["weapon"].id,
                "is_critical": "true",
                "natural_roll": 20,
                "total_roll": 23,
                "attack_bonus": 3,
                "total_damage": 12,
                "damage_rolls": "6,4",
                "damage_formula": "2d8 (6+4) + 2",
            },
        )

        content = response.content.decode()
        # Verify two dice are shown (count HTML elements, not CSS class definitions)
        assert content.count('class="damage-die"') == 2

    def test_damage_roll_invalid_target(self, client, active_combat_setup):
        """Test damage roll with invalid target returns error."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-damage-roll",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": 99999,
                "weapon_id": setup["weapon"].id,
                "is_critical": "false",
                "natural_roll": 15,
                "total_roll": 18,
                "attack_bonus": 3,
                "total_damage": 7,
                "damage_rolls": "5",
                "damage_formula": "1d8 (5) + 2",
            },
        )

        assert response.status_code == 400


class TestApplyDamageView:
    """Tests for ApplyDamageView."""

    @pytest.fixture
    def active_combat_setup(self):
        """Set up an active combat with multiple fighters."""
        game = GameFactory()
        user1 = UserFactory()
        character1 = CharacterFactory(user=user1)
        player1 = Player.objects.create(user=user1, game=game, character=character1)

        # Add a weapon to character1's inventory
        weapon_settings, _ = WeaponSettings.objects.update_or_create(
            name=WeaponName.LONGSWORD,
            defaults={
                "weapon_type": WeaponType.MARTIAL_MELEE,
                "cost": 15,
                "damage": "1d8",
                "weight": 3,
                "properties": "versatile",
            },
        )
        weapon = Weapon.objects.create(
            settings=weapon_settings,
            inventory=character1.inventory,
        )

        user2 = UserFactory()
        character2 = CharacterFactory(user=user2)
        character2.ac = 15
        character2.hp = 30
        character2.max_hp = 30
        character2.save()
        player2 = Player.objects.create(user=user2, game=game, character=character2)

        combat = Combat.objects.create(game=game)
        fighter1 = FighterFactory(
            combat=combat,
            player=player1,
            character=character1,
            dexterity_check=15,
        )
        fighter2 = FighterFactory(
            combat=combat,
            player=player2,
            character=character2,
            dexterity_check=10,
        )
        combat.start_combat()
        return {
            "game": game,
            "combat": combat,
            "player1": player1,
            "player2": player2,
            "fighter1": fighter1,
            "fighter2": fighter2,
            "weapon": weapon,
        }

    def test_apply_damage_reduces_hp(self, client, active_combat_setup):
        """Test applying damage reduces target HP."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)
        initial_hp = setup["fighter2"].character.hp

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        assert response.status_code == 200
        setup["fighter2"].character.refresh_from_db()
        assert setup["fighter2"].character.hp == initial_hp - 10

    def test_apply_damage_shows_confirmation(self, client, active_combat_setup):
        """Test applying damage shows confirmation."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        content = response.content.decode()
        assert "Damage Applied" in content

    def test_apply_damage_uses_action(self, client, active_combat_setup):
        """Test applying damage uses the standard action."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        # Check that action was used
        from game.models.combat import Turn

        turn = Turn.objects.filter(
            fighter=setup["fighter1"],
            round__combat=setup["combat"],
            completed=False,
        ).first()
        assert turn.action_used is True

    def test_apply_damage_sets_htmx_trigger(self, client, active_combat_setup):
        """Test applying damage sets HX-Trigger header."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 10,
            },
        )

        assert "HX-Trigger" in response
        assert "damage-applied" in response["HX-Trigger"]
        assert "initiative-updated" in response["HX-Trigger"]

    def test_apply_damage_invalid_target(self, client, active_combat_setup):
        """Test applying damage with invalid target returns error."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": 99999,
                "damage": 10,
            },
        )

        assert response.status_code == 400

    def test_apply_damage_cannot_go_negative(self, client, active_combat_setup):
        """Test HP cannot go below 0."""
        setup = active_combat_setup
        client.force_login(setup["player1"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        client.post(
            url,
            {
                "target_id": setup["fighter2"].id,
                "damage": 100,  # More than HP
            },
        )

        setup["fighter2"].character.refresh_from_db()
        assert setup["fighter2"].character.hp == 0

    # Note: test_apply_damage_requires_login is not implemented because GameContextMixin
    # runs setup() before LoginRequiredMixin can redirect, causing errors with
    # anonymous users. This would require refactoring the mixin order.

    def test_apply_damage_forbidden_when_not_your_turn(
        self, client, active_combat_setup
    ):
        """Test applying damage returns 403 when not your turn."""
        setup = active_combat_setup
        client.force_login(setup["player2"].user)

        url = reverse(
            "combat-apply-damage",
            args=(setup["game"].id, setup["combat"].id),
        )
        response = client.post(
            url,
            {
                "target_id": setup["fighter1"].id,
                "damage": 10,
            },
        )

        assert response.status_code == 403
