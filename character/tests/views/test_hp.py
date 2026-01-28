import pytest
from django.urls import reverse

from ..factories import CharacterFactory


@pytest.fixture
def hp_character(client):
    """Create a test character with specific HP values for HP tests."""
    char = CharacterFactory(hp=50, max_hp=100)
    client.force_login(char.user)
    return char


@pytest.mark.django_db
class TestCharacterHPModel:
    """Test Character model HP-related methods."""

    def test_take_damage_reduces_hp(self, hp_character):
        hp_character.take_damage(10)
        assert hp_character.hp == 40

    def test_take_damage_floor_at_zero(self, hp_character):
        hp_character.take_damage(100)
        assert hp_character.hp == 0

    def test_take_damage_consumes_temp_hp_first(self, hp_character):
        hp_character.temp_hp = 20
        hp_character.save()
        hp_character.take_damage(15)
        assert hp_character.temp_hp == 5
        assert hp_character.hp == 50

    def test_take_damage_overflows_to_hp(self, hp_character):
        hp_character.temp_hp = 10
        hp_character.save()
        hp_character.take_damage(25)
        assert hp_character.temp_hp == 0
        assert hp_character.hp == 35

    def test_heal_increases_hp(self, hp_character):
        hp_character.hp = 30
        hp_character.save()
        actual = hp_character.heal(15)
        assert actual == 15
        assert hp_character.hp == 45

    def test_heal_caps_at_max_hp(self, hp_character):
        hp_character.hp = 90
        hp_character.save()
        actual = hp_character.heal(20)
        assert actual == 10
        assert hp_character.hp == 100

    def test_add_temp_hp(self, hp_character):
        hp_character.add_temp_hp(15)
        assert hp_character.temp_hp == 15

    def test_add_temp_hp_takes_higher(self, hp_character):
        hp_character.temp_hp = 10
        hp_character.save()
        hp_character.add_temp_hp(15)
        assert hp_character.temp_hp == 15

    def test_add_temp_hp_ignores_lower(self, hp_character):
        hp_character.temp_hp = 20
        hp_character.save()
        hp_character.add_temp_hp(10)
        assert hp_character.temp_hp == 20

    def test_remove_temp_hp(self, hp_character):
        hp_character.temp_hp = 15
        hp_character.save()
        hp_character.remove_temp_hp()
        assert hp_character.temp_hp == 0

    def test_is_unconscious(self, hp_character):
        assert not hp_character.is_unconscious
        hp_character.hp = 0
        assert hp_character.is_unconscious

    def test_death_save_success(self, hp_character):
        hp_character.hp = 0
        hp_character.save()
        hp_character.add_death_save_success()
        assert hp_character.death_save_successes == 1
        assert not hp_character.is_stable

    def test_death_save_stable_at_three_successes(self, hp_character):
        hp_character.hp = 0
        hp_character.save()
        hp_character.add_death_save_success()
        hp_character.add_death_save_success()
        is_stable = hp_character.add_death_save_success()
        assert is_stable
        assert hp_character.is_stable

    def test_death_save_failure(self, hp_character):
        hp_character.hp = 0
        hp_character.save()
        hp_character.add_death_save_failure()
        assert hp_character.death_save_failures == 1
        assert not hp_character.is_dead

    def test_death_save_dead_at_three_failures(self, hp_character):
        hp_character.hp = 0
        hp_character.save()
        hp_character.add_death_save_failure()
        hp_character.add_death_save_failure()
        is_dead = hp_character.add_death_save_failure()
        assert is_dead
        assert hp_character.is_dead

    def test_reset_death_saves(self, hp_character):
        hp_character.death_save_successes = 2
        hp_character.death_save_failures = 1
        hp_character.save()
        hp_character.reset_death_saves()
        assert hp_character.death_save_successes == 0
        assert hp_character.death_save_failures == 0

    def test_hp_percentage(self, hp_character):
        assert hp_character.hp_percentage == 50
        hp_character.hp = 25
        assert hp_character.hp_percentage == 25
        hp_character.hp = 0
        assert hp_character.hp_percentage == 0

    def test_effective_hp_includes_temp(self, hp_character):
        hp_character.temp_hp = 20
        hp_character.save()
        assert hp_character.effective_hp == 70


@pytest.mark.django_db
class TestHPBarView:
    """Test HP bar HTMX view."""

    def test_hp_bar_view(self, client, hp_character):
        url = reverse("character-hp-bar", args=[hp_character.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"hp-bar-component" in response.content


@pytest.mark.django_db
class TestTakeDamageView:
    """Test take damage HTMX view."""

    def test_take_damage(self, client, hp_character):
        url = reverse("character-take-damage", args=[hp_character.pk])
        response = client.post(url, {"damage": "10"})
        assert response.status_code == 200
        hp_character.refresh_from_db()
        assert hp_character.hp == 40

    def test_take_damage_returns_hp_bar(self, client, hp_character):
        url = reverse("character-take-damage", args=[hp_character.pk])
        response = client.post(url, {"damage": "10"})
        assert b"hp-damage" in response.content  # animation class

    def test_take_damage_triggers_htmx_event(self, client, hp_character):
        url = reverse("character-take-damage", args=[hp_character.pk])
        response = client.post(url, {"damage": "10"})
        assert response["HX-Trigger"] == "hp-updated"


@pytest.mark.django_db
class TestHealView:
    """Test heal HTMX view."""

    def test_heal(self, client, hp_character):
        hp_character.hp = 30
        hp_character.save()
        url = reverse("character-heal", args=[hp_character.pk])
        response = client.post(url, {"amount": "20"})
        assert response.status_code == 200
        hp_character.refresh_from_db()
        assert hp_character.hp == 50

    def test_heal_returns_hp_bar_with_animation(self, client, hp_character):
        hp_character.hp = 30
        hp_character.save()
        url = reverse("character-heal", args=[hp_character.pk])
        response = client.post(url, {"amount": "20"})
        assert b"hp-heal" in response.content


@pytest.mark.django_db
class TestAddTempHPView:
    """Test add temp HP HTMX view."""

    def test_add_temp_hp(self, client, hp_character):
        url = reverse("character-add-temp-hp", args=[hp_character.pk])
        response = client.post(url, {"amount": "15"})
        assert response.status_code == 200
        hp_character.refresh_from_db()
        assert hp_character.temp_hp == 15

    def test_add_temp_hp_returns_animation(self, client, hp_character):
        url = reverse("character-add-temp-hp", args=[hp_character.pk])
        response = client.post(url, {"amount": "15"})
        assert b"hp-temp" in response.content


@pytest.mark.django_db
class TestDeathSaveView:
    """Test death save HTMX view."""

    def test_death_save_success(self, client, hp_character):
        hp_character.hp = 0
        hp_character.save()
        url = reverse("character-death-save", args=[hp_character.pk])
        response = client.post(url, {"result": "success"})
        assert response.status_code == 200
        hp_character.refresh_from_db()
        assert hp_character.death_save_successes == 1

    def test_death_save_failure(self, client, hp_character):
        hp_character.hp = 0
        hp_character.save()
        url = reverse("character-death-save", args=[hp_character.pk])
        response = client.post(url, {"result": "failure"})
        assert response.status_code == 200
        hp_character.refresh_from_db()
        assert hp_character.death_save_failures == 1
