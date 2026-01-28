import pytest
from django.urls import reverse


@pytest.fixture
def character(character_factory, user):
    """Create a test character with specific HP values."""
    char = character_factory(user=user, hp=50, max_hp=100)
    return char


@pytest.mark.django_db
class TestCharacterHPModel:
    """Test Character model HP-related methods."""

    def test_take_damage_reduces_hp(self, character):
        character.take_damage(10)
        assert character.hp == 40

    def test_take_damage_floor_at_zero(self, character):
        character.take_damage(100)
        assert character.hp == 0

    def test_take_damage_consumes_temp_hp_first(self, character):
        character.temp_hp = 20
        character.save()
        character.take_damage(15)
        assert character.temp_hp == 5
        assert character.hp == 50

    def test_take_damage_overflows_to_hp(self, character):
        character.temp_hp = 10
        character.save()
        character.take_damage(25)
        assert character.temp_hp == 0
        assert character.hp == 35

    def test_heal_increases_hp(self, character):
        character.hp = 30
        character.save()
        actual = character.heal(15)
        assert actual == 15
        assert character.hp == 45

    def test_heal_caps_at_max_hp(self, character):
        character.hp = 90
        character.save()
        actual = character.heal(20)
        assert actual == 10
        assert character.hp == 100

    def test_add_temp_hp(self, character):
        character.add_temp_hp(15)
        assert character.temp_hp == 15

    def test_add_temp_hp_takes_higher(self, character):
        character.temp_hp = 10
        character.save()
        character.add_temp_hp(15)
        assert character.temp_hp == 15

    def test_add_temp_hp_ignores_lower(self, character):
        character.temp_hp = 20
        character.save()
        character.add_temp_hp(10)
        assert character.temp_hp == 20

    def test_remove_temp_hp(self, character):
        character.temp_hp = 15
        character.save()
        character.remove_temp_hp()
        assert character.temp_hp == 0

    def test_is_unconscious(self, character):
        assert not character.is_unconscious
        character.hp = 0
        assert character.is_unconscious

    def test_death_save_success(self, character):
        character.hp = 0
        character.save()
        character.add_death_save_success()
        assert character.death_save_successes == 1
        assert not character.is_stable

    def test_death_save_stable_at_three_successes(self, character):
        character.hp = 0
        character.save()
        character.add_death_save_success()
        character.add_death_save_success()
        is_stable = character.add_death_save_success()
        assert is_stable
        assert character.is_stable

    def test_death_save_failure(self, character):
        character.hp = 0
        character.save()
        character.add_death_save_failure()
        assert character.death_save_failures == 1
        assert not character.is_dead

    def test_death_save_dead_at_three_failures(self, character):
        character.hp = 0
        character.save()
        character.add_death_save_failure()
        character.add_death_save_failure()
        is_dead = character.add_death_save_failure()
        assert is_dead
        assert character.is_dead

    def test_reset_death_saves(self, character):
        character.death_save_successes = 2
        character.death_save_failures = 1
        character.save()
        character.reset_death_saves()
        assert character.death_save_successes == 0
        assert character.death_save_failures == 0

    def test_hp_percentage(self, character):
        assert character.hp_percentage == 50
        character.hp = 25
        assert character.hp_percentage == 25
        character.hp = 0
        assert character.hp_percentage == 0

    def test_effective_hp_includes_temp(self, character):
        character.temp_hp = 20
        character.save()
        assert character.effective_hp == 70


@pytest.mark.django_db
class TestHPBarView:
    """Test HP bar HTMX view."""

    def test_hp_bar_view(self, client, character):
        client.force_login(character.user)
        url = reverse("character-hp-bar", args=[character.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"hp-bar-component" in response.content


@pytest.mark.django_db
class TestTakeDamageView:
    """Test take damage HTMX view."""

    def test_take_damage(self, client, character):
        client.force_login(character.user)
        url = reverse("character-take-damage", args=[character.pk])
        response = client.post(url, {"damage": "10"})
        assert response.status_code == 200
        character.refresh_from_db()
        assert character.hp == 40

    def test_take_damage_returns_hp_bar(self, client, character):
        client.force_login(character.user)
        url = reverse("character-take-damage", args=[character.pk])
        response = client.post(url, {"damage": "10"})
        assert b"hp-damage" in response.content  # animation class

    def test_take_damage_triggers_htmx_event(self, client, character):
        client.force_login(character.user)
        url = reverse("character-take-damage", args=[character.pk])
        response = client.post(url, {"damage": "10"})
        assert response["HX-Trigger"] == "hp-updated"


@pytest.mark.django_db
class TestHealView:
    """Test heal HTMX view."""

    def test_heal(self, client, character):
        client.force_login(character.user)
        character.hp = 30
        character.save()
        url = reverse("character-heal", args=[character.pk])
        response = client.post(url, {"amount": "20"})
        assert response.status_code == 200
        character.refresh_from_db()
        assert character.hp == 50

    def test_heal_returns_hp_bar_with_animation(self, client, character):
        client.force_login(character.user)
        character.hp = 30
        character.save()
        url = reverse("character-heal", args=[character.pk])
        response = client.post(url, {"amount": "20"})
        assert b"hp-heal" in response.content


@pytest.mark.django_db
class TestAddTempHPView:
    """Test add temp HP HTMX view."""

    def test_add_temp_hp(self, client, character):
        client.force_login(character.user)
        url = reverse("character-add-temp-hp", args=[character.pk])
        response = client.post(url, {"amount": "15"})
        assert response.status_code == 200
        character.refresh_from_db()
        assert character.temp_hp == 15

    def test_add_temp_hp_returns_animation(self, client, character):
        client.force_login(character.user)
        url = reverse("character-add-temp-hp", args=[character.pk])
        response = client.post(url, {"amount": "15"})
        assert b"hp-temp" in response.content


@pytest.mark.django_db
class TestDeathSaveView:
    """Test death save HTMX view."""

    def test_death_save_success(self, client, character):
        client.force_login(character.user)
        character.hp = 0
        character.save()
        url = reverse("character-death-save", args=[character.pk])
        response = client.post(url, {"result": "success"})
        assert response.status_code == 200
        character.refresh_from_db()
        assert character.death_save_successes == 1

    def test_death_save_failure(self, client, character):
        client.force_login(character.user)
        character.hp = 0
        character.save()
        url = reverse("character-death-save", args=[character.pk])
        response = client.post(url, {"result": "failure"})
        assert response.status_code == 200
        character.refresh_from_db()
        assert character.death_save_failures == 1
