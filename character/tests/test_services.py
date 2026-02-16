import pytest

from magic.constants.spells import SpellLevel, SpellSchool
from magic.models.spells import Concentration

from ..services import SpellsPanelService
from .factories import (
    CharacterFactory,
    CharacterSpellSlotFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
    WarlockSpellSlotFactory,
)


@pytest.fixture()
def character():
    return CharacterFactory()


@pytest.mark.django_db
class TestGetSpellsPanelData:
    """Tests for SpellsPanelService.get_spells_panel_data."""

    def test_returns_spell_slots(self, character):
        """Verifies slot data structure with circles visualization."""
        CharacterSpellSlotFactory(character=character, slot_level=1, total=2, used=0)
        CharacterSpellSlotFactory(character=character, slot_level=2, total=3, used=1)

        result = SpellsPanelService.get_spells_panel_data(character)

        assert len(result["spell_slots"]) == 2
        slot1 = result["spell_slots"][0]
        assert slot1["level"] == 1
        assert slot1["total"] == 2
        assert slot1["used"] == 0
        assert slot1["remaining"] == 2
        assert len(slot1["circles"]) == 2
        # All circles should be filled (none used)
        assert all(c["filled"] for c in slot1["circles"])

        slot2 = result["spell_slots"][1]
        assert slot2["level"] == 2
        assert slot2["total"] == 3
        assert slot2["used"] == 1
        assert slot2["remaining"] == 2
        assert len(slot2["circles"]) == 3
        # First circle unfilled (used), rest filled
        assert not slot2["circles"][0]["filled"]
        assert slot2["circles"][1]["filled"]
        assert slot2["circles"][2]["filled"]

    def test_excludes_zero_total_slots(self, character):
        """Slots with total=0 should not appear in the result."""
        CharacterSpellSlotFactory(character=character, slot_level=1, total=0, used=0)
        CharacterSpellSlotFactory(character=character, slot_level=2, total=3, used=0)

        result = SpellsPanelService.get_spells_panel_data(character)

        assert len(result["spell_slots"]) == 1
        assert result["spell_slots"][0]["level"] == 2

    def test_returns_prepared_spells(self, character):
        """Verifies prepared spells are included."""
        settings = SpellSettingsFactory(name="Shield", level=SpellLevel.FIRST)
        SpellPreparationFactory(character=character, settings=settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        assert len(result["prepared_spells"]) == 1
        assert result["prepared_spells"][0].settings.name == "Shield"
        assert result["has_prepared"] is True

    def test_returns_known_spells(self, character):
        """Verifies known spells are included."""
        settings = SpellSettingsFactory(name="Magic Missile", level=SpellLevel.FIRST)
        SpellFactory(character=character, settings=settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        assert len(result["known_spells"]) == 1
        assert result["known_spells"][0].settings.name == "Magic Missile"
        assert result["has_known"] is True

    def test_groups_spells_by_level(self, character):
        """Verifies spells are grouped by level."""
        cantrip_settings = SpellSettingsFactory(
            name="Fire Bolt", level=SpellLevel.CANTRIP
        )
        first_settings = SpellSettingsFactory(
            name="Magic Missile", level=SpellLevel.FIRST
        )
        second_settings = SpellSettingsFactory(
            name="Scorching Ray", level=SpellLevel.SECOND
        )
        SpellFactory(character=character, settings=cantrip_settings)
        SpellFactory(character=character, settings=first_settings)
        SpellFactory(character=character, settings=second_settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        known_by_level = result["known_by_level"]
        assert 0 in known_by_level
        assert 1 in known_by_level
        assert 2 in known_by_level
        assert known_by_level[0][0].settings.name == "Fire Bolt"
        assert known_by_level[1][0].settings.name == "Magic Missile"
        assert known_by_level[2][0].settings.name == "Scorching Ray"

    def test_filter_by_level(self, character):
        """Level filter returns only matching spells."""
        first_settings = SpellSettingsFactory(
            name="Magic Missile", level=SpellLevel.FIRST
        )
        second_settings = SpellSettingsFactory(
            name="Scorching Ray", level=SpellLevel.SECOND
        )
        SpellFactory(character=character, settings=first_settings)
        SpellFactory(character=character, settings=second_settings)

        result = SpellsPanelService.get_spells_panel_data(
            character, level_filter=SpellLevel.FIRST
        )

        assert len(result["known_spells"]) == 1
        assert result["known_spells"][0].settings.name == "Magic Missile"

    def test_filter_by_school(self, character):
        """School filter returns only matching spells."""
        evo_settings = SpellSettingsFactory(
            name="Fireball", level=SpellLevel.THIRD, school=SpellSchool.EVOCATION
        )
        abj_settings = SpellSettingsFactory(
            name="Shield", level=SpellLevel.FIRST, school=SpellSchool.ABJURATION
        )
        SpellPreparationFactory(character=character, settings=evo_settings)
        SpellPreparationFactory(character=character, settings=abj_settings)

        result = SpellsPanelService.get_spells_panel_data(
            character, school_filter=SpellSchool.EVOCATION
        )

        assert len(result["prepared_spells"]) == 1
        assert result["prepared_spells"][0].settings.name == "Fireball"

    def test_filter_by_concentration(self, character):
        """Concentration filter returns only matching spells."""
        conc_settings = SpellSettingsFactory(
            name="Bless", level=SpellLevel.FIRST, concentration=True
        )
        non_conc_settings = SpellSettingsFactory(
            name="Magic Missile", level=SpellLevel.FIRST, concentration=False
        )
        SpellPreparationFactory(character=character, settings=conc_settings)
        SpellPreparationFactory(character=character, settings=non_conc_settings)

        # Filter for concentration spells
        result = SpellsPanelService.get_spells_panel_data(
            character, concentration_filter=True
        )
        assert len(result["prepared_spells"]) == 1
        assert result["prepared_spells"][0].settings.name == "Bless"

        # Filter for non-concentration spells
        result = SpellsPanelService.get_spells_panel_data(
            character, concentration_filter=False
        )
        assert len(result["prepared_spells"]) == 1
        assert result["prepared_spells"][0].settings.name == "Magic Missile"

    def test_filter_by_search(self, character):
        """Search query filters by spell name (case-insensitive)."""
        SpellFactory(
            character=character,
            settings=SpellSettingsFactory(name="Fireball", level=SpellLevel.THIRD),
        )
        SpellFactory(
            character=character,
            settings=SpellSettingsFactory(name="Fire Bolt", level=SpellLevel.CANTRIP),
        )
        SpellFactory(
            character=character,
            settings=SpellSettingsFactory(name="Magic Missile", level=SpellLevel.FIRST),
        )

        result = SpellsPanelService.get_spells_panel_data(
            character, search_query="fire"
        )

        assert len(result["known_spells"]) == 2
        names = {s.settings.name for s in result["known_spells"]}
        assert names == {"Fireball", "Fire Bolt"}

    def test_returns_quick_cast_cantrips(self, character):
        """Cantrips should appear in quick-cast with can_cast=True."""
        cantrip_settings = SpellSettingsFactory(
            name="Fire Bolt", level=SpellLevel.CANTRIP
        )
        SpellPreparationFactory(character=character, settings=cantrip_settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        assert len(result["quick_cast_spells"]) == 1
        qc = result["quick_cast_spells"][0]
        assert qc["spell"].settings.name == "Fire Bolt"
        assert qc["type"] == "prepared"
        assert qc["can_cast"] is True

    def test_quick_cast_includes_first_level_with_slots(self, character):
        """First-level spells in quick-cast show can_cast based on slots."""
        CharacterSpellSlotFactory(character=character, slot_level=1, total=2, used=0)
        first_settings = SpellSettingsFactory(
            name="Magic Missile", level=SpellLevel.FIRST
        )
        SpellPreparationFactory(character=character, settings=first_settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        first_level_qc = [
            qc for qc in result["quick_cast_spells"] if qc["spell"].settings.level == 1
        ]
        assert len(first_level_qc) == 1
        assert first_level_qc[0]["can_cast"] is True

    def test_quick_cast_first_level_no_slots_remaining(self, character):
        """First-level spells show can_cast=False when no slots left."""
        CharacterSpellSlotFactory(character=character, slot_level=1, total=2, used=2)
        first_settings = SpellSettingsFactory(
            name="Magic Missile", level=SpellLevel.FIRST
        )
        SpellPreparationFactory(character=character, settings=first_settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        first_level_qc = [
            qc for qc in result["quick_cast_spells"] if qc["spell"].settings.level == 1
        ]
        assert len(first_level_qc) == 1
        assert first_level_qc[0]["can_cast"] is False

    def test_quick_cast_limits_first_level_to_three(self, character):
        """Quick-cast includes at most 3 first-level spells."""
        CharacterSpellSlotFactory(character=character, slot_level=1, total=4, used=0)
        for i in range(5):
            settings = SpellSettingsFactory(
                name=f"Spell L1 {i}", level=SpellLevel.FIRST
            )
            SpellPreparationFactory(character=character, settings=settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        first_level_qc = [
            qc for qc in result["quick_cast_spells"] if qc["spell"].settings.level == 1
        ]
        assert len(first_level_qc) == 3

    def test_returns_active_concentration(self, character):
        """Active concentration spell is returned when present."""
        conc_settings = SpellSettingsFactory(
            name="Bless", level=SpellLevel.FIRST, concentration=True
        )
        Concentration.start_concentration(character, conc_settings)

        result = SpellsPanelService.get_spells_panel_data(character)

        assert result["active_concentration"] is not None
        assert result["active_concentration"].spell.name == "Bless"

    def test_no_active_concentration(self, character):
        """No active concentration returns None."""
        result = SpellsPanelService.get_spells_panel_data(character)

        assert result["active_concentration"] is None

    def test_returns_pact_magic_when_present(self, character):
        """Warlock pact magic slot data is returned."""
        WarlockSpellSlotFactory(character=character, slot_level=1, total=2, used=1)

        result = SpellsPanelService.get_spells_panel_data(character)

        pact_magic = result["pact_magic"]
        assert pact_magic is not None
        assert pact_magic["level"] == 1
        assert pact_magic["total"] == 2
        assert pact_magic["used"] == 1
        assert pact_magic["remaining"] == 1
        assert len(pact_magic["circles"]) == 2
        # First circle unfilled (used), second filled
        assert not pact_magic["circles"][0]["filled"]
        assert pact_magic["circles"][1]["filled"]

    def test_no_pact_magic_when_absent(self, character):
        """Non-warlock characters have pact_magic=None."""
        result = SpellsPanelService.get_spells_panel_data(character)

        assert result["pact_magic"] is None

    def test_returns_filter_options(self, character):
        """Spell levels and schools choices are included."""
        result = SpellsPanelService.get_spells_panel_data(character)

        assert len(result["spell_levels"]) == len(SpellLevel.choices)
        assert len(result["spell_schools"]) == len(SpellSchool.choices)
        # Check structure
        assert result["spell_levels"][0]["value"] == SpellLevel.CANTRIP
        assert result["spell_levels"][0]["label"] == "Cantrip"

    def test_returns_character(self, character):
        """The character is included in the result."""
        result = SpellsPanelService.get_spells_panel_data(character)

        assert result["character"] is character

    def test_returns_filter_values(self, character):
        """Filter values are echoed back in the result."""
        result = SpellsPanelService.get_spells_panel_data(
            character,
            level_filter=1,
            school_filter="evocation",
            concentration_filter=True,
            search_query="fire",
        )

        assert result["level_filter"] == 1
        assert result["school_filter"] == "evocation"
        assert result["concentration_filter"] is True
        assert result["search_query"] == "fire"

    def test_empty_spells(self, character):
        """Character with no spells returns empty lists/dicts."""
        result = SpellsPanelService.get_spells_panel_data(character)

        assert result["prepared_spells"] == []
        assert result["known_spells"] == []
        assert result["prepared_by_level"] == {}
        assert result["known_by_level"] == {}
        assert result["quick_cast_spells"] == []
        assert result["has_prepared"] is False
        assert result["has_known"] is False
