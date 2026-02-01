import pytest
from django.urls import reverse

from character.models.spells import Concentration

from ..factories import (
    CharacterFactory,
    CharacterSpellSlotFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
)


@pytest.fixture
def spells_character(client):
    """Create a test character with spells for testing."""
    char = CharacterFactory()
    client.force_login(char.user)
    return char


@pytest.fixture
def character_with_slots(spells_character):
    """Create a character with spell slots."""
    CharacterSpellSlotFactory(character=spells_character, slot_level=1, total=4, used=1)
    CharacterSpellSlotFactory(character=spells_character, slot_level=2, total=3, used=0)
    CharacterSpellSlotFactory(character=spells_character, slot_level=3, total=2, used=2)
    return spells_character


@pytest.fixture
def character_with_spells(character_with_slots):
    """Create a character with prepared and known spells."""
    # Create some spell settings
    fireball = SpellSettingsFactory(
        name="Fireball",
        level=3,
        school="evocation",
        concentration=False,
    )
    shield = SpellSettingsFactory(
        name="Shield",
        level=1,
        school="abjuration",
        concentration=False,
    )
    hold_person = SpellSettingsFactory(
        name="Hold Person",
        level=2,
        school="enchantment",
        concentration=True,
    )
    fire_bolt = SpellSettingsFactory(
        name="Fire Bolt",
        level=0,
        school="evocation",
        concentration=False,
    )

    # Add prepared spells
    SpellPreparationFactory(
        character=character_with_slots,
        settings=fireball,
        always_prepared=False,
    )
    SpellPreparationFactory(
        character=character_with_slots,
        settings=shield,
        always_prepared=True,
    )

    # Add known spells
    SpellFactory(character=character_with_slots, settings=hold_person)
    SpellFactory(character=character_with_slots, settings=fire_bolt)

    return character_with_slots


@pytest.mark.django_db
class TestSpellsPanelView:
    """Test spells panel HTMX view."""

    def test_spells_panel_view(self, client, spells_character):
        url = reverse("character-spells-panel", args=[spells_character.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"spells-panel-component" in response.content

    def test_spells_panel_shows_spell_slots(self, client, character_with_slots):
        url = reverse("character-spells-panel", args=[character_with_slots.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"slot-circle" in response.content
        assert b"slot-level-badge" in response.content

    def test_spells_panel_shows_prepared_spells(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"Prepared Spells" in response.content
        assert b"Fireball" in response.content
        assert b"Shield" in response.content

    def test_spells_panel_shows_known_spells(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"Known Spells" in response.content
        assert b"Hold Person" in response.content
        assert b"Fire Bolt" in response.content

    def test_spells_panel_shows_filter_controls(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"filter-btn" in response.content
        assert b"search-input" in response.content

    def test_spells_panel_filter_by_level(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"level": "3"})
        assert response.status_code == 200
        assert b"Fireball" in response.content
        # Level 1 spell should not appear
        assert b"Shield" not in response.content

    def test_spells_panel_filter_by_school(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"school": "evocation"})
        assert response.status_code == 200
        assert b"Fireball" in response.content
        assert b"Fire Bolt" in response.content
        # Non-evocation spells should not appear
        assert b"Shield" not in response.content

    def test_spells_panel_filter_by_concentration(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"concentration": "true"})
        assert response.status_code == 200
        assert b"Hold Person" in response.content
        # Non-concentration spells should not appear
        assert b"Fireball" not in response.content

    def test_spells_panel_filter_concentration_false(
        self, client, character_with_spells
    ):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"concentration": "false"})
        assert response.status_code == 200
        assert b"Fireball" in response.content
        assert b"Shield" in response.content
        # Concentration spells should not appear
        assert b"Hold Person" not in response.content

    def test_spells_panel_search(self, client, character_with_spells):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"search": "fire"})
        assert response.status_code == 200
        assert b"Fireball" in response.content
        assert b"Fire Bolt" in response.content
        # Non-matching spells should not appear
        assert b"Shield" not in response.content

    def test_spells_panel_invalid_level_filter_ignored(
        self, client, character_with_spells
    ):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"level": "invalid"})
        assert response.status_code == 200
        # Should show all spells when filter is invalid
        assert b"Fireball" in response.content
        assert b"Shield" in response.content

    def test_spells_panel_invalid_school_filter_ignored(
        self, client, character_with_spells
    ):
        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url, {"school": "invalid_school"})
        assert response.status_code == 200
        # Should show all spells when filter is invalid
        assert b"Fireball" in response.content

    def test_spells_panel_requires_login(self, client, spells_character):
        client.logout()
        url = reverse("character-spells-panel", args=[spells_character.pk])
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login

    def test_spells_panel_shows_concentration_banner(
        self, client, character_with_spells
    ):
        # Start concentration on a spell
        spell = SpellSettingsFactory(name="Fly", concentration=True)
        Concentration.start_concentration(character_with_spells, spell)

        url = reverse("character-spells-panel", args=[character_with_spells.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert b"concentration-banner" in response.content
        assert b"Fly" in response.content


@pytest.mark.django_db
class TestUseSpellSlotView:
    """Test using spell slots."""

    def test_use_spell_slot(self, client, character_with_slots):
        slot = character_with_slots.spell_slots.get(slot_level=1)
        initial_used = slot.used

        url = reverse("character-use-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "1"})
        assert response.status_code == 200

        slot.refresh_from_db()
        assert slot.used == initial_used + 1

    def test_use_spell_slot_returns_panel(self, client, character_with_slots):
        url = reverse("character-use-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "1"})
        assert response.status_code == 200
        assert b"spells-panel-component" in response.content

    def test_use_spell_slot_invalid_level_defaults(self, client, character_with_slots):
        url = reverse("character-use-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "invalid"})
        assert response.status_code == 200

    def test_use_spell_slot_requires_login(self, client, character_with_slots):
        client.logout()
        url = reverse("character-use-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "1"})
        assert response.status_code == 302


@pytest.mark.django_db
class TestRestoreSpellSlotView:
    """Test restoring spell slots."""

    def test_restore_spell_slot(self, client, character_with_slots):
        slot = character_with_slots.spell_slots.get(slot_level=1)
        initial_used = slot.used
        assert initial_used > 0  # Make sure there's something to restore

        url = reverse("character-restore-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "1"})
        assert response.status_code == 200

        slot.refresh_from_db()
        assert slot.used == initial_used - 1

    def test_restore_spell_slot_returns_panel(self, client, character_with_slots):
        url = reverse("character-restore-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "1"})
        assert response.status_code == 200
        assert b"spells-panel-component" in response.content

    def test_restore_spell_slot_requires_login(self, client, character_with_slots):
        client.logout()
        url = reverse("character-restore-spell-slot", args=[character_with_slots.pk])
        response = client.post(url, {"slot_level": "1"})
        assert response.status_code == 302


@pytest.mark.django_db
class TestRestoreAllSlotsView:
    """Test restoring all spell slots (long rest)."""

    def test_restore_all_slots(self, client, character_with_slots):
        url = reverse("character-restore-all-slots", args=[character_with_slots.pk])
        response = client.post(url)
        assert response.status_code == 200

        # All slots should be fully restored
        for slot in character_with_slots.spell_slots.all():
            slot.refresh_from_db()
            assert slot.used == 0

    def test_restore_all_slots_returns_panel(self, client, character_with_slots):
        url = reverse("character-restore-all-slots", args=[character_with_slots.pk])
        response = client.post(url)
        assert response.status_code == 200
        assert b"spells-panel-component" in response.content

    def test_restore_all_slots_requires_login(self, client, character_with_slots):
        client.logout()
        url = reverse("character-restore-all-slots", args=[character_with_slots.pk])
        response = client.post(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestCastSpellView:
    """Test quick-casting spells."""

    def test_cast_cantrip(self, client, character_with_spells):
        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(url, {"spell_name": "Fire Bolt", "cast_level": "0"})
        assert response.status_code == 200
        assert b"Cast Fire Bolt" in response.content

    def test_cast_spell_uses_slot(self, client, character_with_spells):
        slot = character_with_spells.spell_slots.get(slot_level=1)
        initial_used = slot.used

        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(url, {"spell_name": "Shield", "cast_level": "1"})
        assert response.status_code == 200

        slot.refresh_from_db()
        assert slot.used == initial_used + 1

    def test_cast_concentration_spell_starts_concentration(
        self, client, character_with_spells
    ):
        # Make sure level 2 slot is available
        slot = character_with_spells.spell_slots.get(slot_level=2)
        assert slot.remaining > 0

        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(url, {"spell_name": "Hold Person", "cast_level": "2"})
        assert response.status_code == 200

        # Check concentration was started
        assert Concentration.objects.filter(character=character_with_spells).exists()

    def test_cast_spell_no_slots_remaining(self, client, character_with_spells):
        # Use all level 3 slots
        slot = character_with_spells.spell_slots.get(slot_level=3)
        assert slot.remaining == 0  # Already depleted in fixture

        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(url, {"spell_name": "Fireball", "cast_level": "3"})
        assert response.status_code == 200
        assert b"No level 3 slots remaining" in response.content

    def test_cast_spell_not_found(self, client, character_with_spells):
        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(
            url, {"spell_name": "Nonexistent Spell", "cast_level": "1"}
        )
        assert response.status_code == 200
        assert b"Spell not found" in response.content

    def test_cast_spell_returns_panel(self, client, character_with_spells):
        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(url, {"spell_name": "Fire Bolt", "cast_level": "0"})
        assert response.status_code == 200
        assert b"spells-panel-component" in response.content

    def test_cast_spell_requires_login(self, client, character_with_spells):
        client.logout()
        url = reverse("character-cast-spell", args=[character_with_spells.pk])
        response = client.post(url, {"spell_name": "Fire Bolt", "cast_level": "0"})
        assert response.status_code == 302


@pytest.mark.django_db
class TestBreakConcentrationView:
    """Test breaking concentration."""

    def test_break_concentration(self, client, spells_character):
        # Start concentration
        spell = SpellSettingsFactory(name="Fly", concentration=True)
        Concentration.start_concentration(spells_character, spell)
        assert Concentration.objects.filter(character=spells_character).exists()

        url = reverse("character-break-concentration", args=[spells_character.pk])
        response = client.post(url)
        assert response.status_code == 200

        # Concentration should be broken
        assert not Concentration.objects.filter(character=spells_character).exists()

    def test_break_concentration_no_active_concentration(
        self, client, spells_character
    ):
        # Should not error if no concentration
        url = reverse("character-break-concentration", args=[spells_character.pk])
        response = client.post(url)
        assert response.status_code == 200

    def test_break_concentration_returns_panel(self, client, spells_character):
        url = reverse("character-break-concentration", args=[spells_character.pk])
        response = client.post(url)
        assert response.status_code == 200
        assert b"spells-panel-component" in response.content

    def test_break_concentration_requires_login(self, client, spells_character):
        client.logout()
        url = reverse("character-break-concentration", args=[spells_character.pk])
        response = client.post(url)
        assert response.status_code == 302
