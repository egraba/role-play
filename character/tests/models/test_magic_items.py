import pytest
from django.core.exceptions import ValidationError

from equipment.constants.magic_items import (
    MagicItemName,
    MagicItemType,
    Rarity,
)
from equipment.models.magic_items import (
    Attunement,
    MagicItem,
    MagicItemSettings,
)

from ..factories import (
    CharacterFactory,
    MagicItemFactory,
)


@pytest.mark.django_db
class TestMagicItemSettingsModel:
    """Tests for the MagicItemSettings model."""

    def test_creation(self):
        settings = MagicItemSettings.objects.first()
        assert isinstance(settings, MagicItemSettings)

    def test_str(self):
        settings = MagicItemSettings.objects.get(name=MagicItemName.WEAPON_PLUS_1)
        assert "Weapon +1" in str(settings)
        assert "Uncommon" in str(settings)


@pytest.mark.django_db
class TestMagicItemSettingsFixture:
    """Tests for the SRD magic item database fixture."""

    def test_total_magic_item_count(self):
        """SRD 5.2.1 fixture should have 33 magic items."""
        assert MagicItemSettings.objects.count() == 33

    def test_weapon_count(self):
        """3 weapon types (+1, +2, +3)."""
        count = MagicItemSettings.objects.filter(item_type=MagicItemType.WEAPON).count()
        assert count == 3

    def test_armor_count(self):
        """6 armor types (+1/+2/+3 armor and shields)."""
        count = MagicItemSettings.objects.filter(item_type=MagicItemType.ARMOR).count()
        assert count == 6

    def test_potion_count(self):
        """4 healing potion types."""
        count = MagicItemSettings.objects.filter(item_type=MagicItemType.POTION).count()
        assert count == 4

    def test_wand_count(self):
        """4 wand types."""
        count = MagicItemSettings.objects.filter(item_type=MagicItemType.WAND).count()
        assert count == 4

    def test_staff_count(self):
        """4 staff types."""
        count = MagicItemSettings.objects.filter(item_type=MagicItemType.STAFF).count()
        assert count == 4

    def test_ring_count(self):
        """2 ring types."""
        count = MagicItemSettings.objects.filter(item_type=MagicItemType.RING).count()
        assert count == 2

    def test_wondrous_item_count(self):
        """10 wondrous items."""
        count = MagicItemSettings.objects.filter(
            item_type=MagicItemType.WONDROUS
        ).count()
        assert count == 10

    # Rarity tests
    def test_common_items(self):
        """1 common item (Potion of Healing)."""
        count = MagicItemSettings.objects.filter(rarity=Rarity.COMMON).count()
        assert count == 1

    def test_uncommon_items(self):
        """12 uncommon items."""
        count = MagicItemSettings.objects.filter(rarity=Rarity.UNCOMMON).count()
        assert count == 12

    def test_rare_items(self):
        """12 rare items."""
        count = MagicItemSettings.objects.filter(rarity=Rarity.RARE).count()
        assert count == 12

    def test_very_rare_items(self):
        """6 very rare items."""
        count = MagicItemSettings.objects.filter(rarity=Rarity.VERY_RARE).count()
        assert count == 6

    def test_legendary_items(self):
        """2 legendary items."""
        count = MagicItemSettings.objects.filter(rarity=Rarity.LEGENDARY).count()
        assert count == 2

    # Weapon bonus tests
    @pytest.mark.parametrize(
        "item_name,expected_bonus,expected_rarity",
        [
            (MagicItemName.WEAPON_PLUS_1, "+1", Rarity.UNCOMMON),
            (MagicItemName.WEAPON_PLUS_2, "+2", Rarity.RARE),
            (MagicItemName.WEAPON_PLUS_3, "+3", Rarity.VERY_RARE),
        ],
    )
    def test_weapon_bonuses(self, item_name, expected_bonus, expected_rarity):
        """Verify +1/+2/+3 weapons have correct bonuses and rarity."""
        item = MagicItemSettings.objects.get(name=item_name)
        assert item.bonus == expected_bonus
        assert item.rarity == expected_rarity
        assert item.effects.get("attack_bonus") == int(expected_bonus[1])
        assert item.effects.get("damage_bonus") == int(expected_bonus[1])

    # Armor bonus tests
    @pytest.mark.parametrize(
        "item_name,expected_bonus,expected_rarity",
        [
            (MagicItemName.ARMOR_PLUS_1, "+1", Rarity.RARE),
            (MagicItemName.ARMOR_PLUS_2, "+2", Rarity.VERY_RARE),
            (MagicItemName.ARMOR_PLUS_3, "+3", Rarity.LEGENDARY),
        ],
    )
    def test_armor_bonuses(self, item_name, expected_bonus, expected_rarity):
        """Verify +1/+2/+3 armors have correct bonuses and rarity."""
        item = MagicItemSettings.objects.get(name=item_name)
        assert item.bonus == expected_bonus
        assert item.rarity == expected_rarity
        assert item.effects.get("ac_bonus") == int(expected_bonus[1])

    # Potion tests
    @pytest.mark.parametrize(
        "item_name,expected_dice,expected_bonus,expected_rarity",
        [
            (MagicItemName.POTION_OF_HEALING, "2d4", 2, Rarity.COMMON),
            (MagicItemName.POTION_OF_GREATER_HEALING, "4d4", 4, Rarity.UNCOMMON),
            (MagicItemName.POTION_OF_SUPERIOR_HEALING, "8d4", 8, Rarity.RARE),
            (MagicItemName.POTION_OF_SUPREME_HEALING, "10d4", 20, Rarity.VERY_RARE),
        ],
    )
    def test_healing_potions(
        self, item_name, expected_dice, expected_bonus, expected_rarity
    ):
        """Verify healing potions have correct healing values."""
        item = MagicItemSettings.objects.get(name=item_name)
        assert item.rarity == expected_rarity
        assert item.is_consumable is True
        assert item.effects.get("healing_dice") == expected_dice
        assert item.effects.get("healing_bonus") == expected_bonus

    # Attunement tests
    def test_items_requiring_attunement(self):
        """Certain items should require attunement."""
        attunement_items = MagicItemSettings.objects.filter(requires_attunement=True)
        assert attunement_items.count() >= 15  # At least 15 items require attunement

    def test_potions_no_attunement(self):
        """Potions should not require attunement."""
        potions = MagicItemSettings.objects.filter(item_type=MagicItemType.POTION)
        for potion in potions:
            assert potion.requires_attunement is False

    def test_weapons_no_attunement(self):
        """Basic +X weapons should not require attunement."""
        weapons = MagicItemSettings.objects.filter(item_type=MagicItemType.WEAPON)
        for weapon in weapons:
            assert weapon.requires_attunement is False

    # Staff tests
    @pytest.mark.parametrize(
        "item_name,expected_charges",
        [
            (MagicItemName.STAFF_OF_HEALING, 10),
            (MagicItemName.STAFF_OF_POWER, 20),
            (MagicItemName.STAFF_OF_THE_MAGI, 50),
            (MagicItemName.STAFF_OF_THE_WOODLANDS, 10),
        ],
    )
    def test_staff_charges(self, item_name, expected_charges):
        """Verify staffs have correct charge amounts."""
        item = MagicItemSettings.objects.get(name=item_name)
        assert item.effects.get("charges") == expected_charges
        assert item.requires_attunement is True

    # Wand tests
    def test_wand_of_magic_missiles(self):
        """Wand of Magic Missiles should have 7 charges."""
        wand = MagicItemSettings.objects.get(name=MagicItemName.WAND_OF_MAGIC_MISSILES)
        assert wand.effects.get("charges") == 7
        assert wand.requires_attunement is False

    @pytest.mark.parametrize(
        "item_name,expected_bonus",
        [
            (MagicItemName.WAND_OF_THE_WAR_MAGE_PLUS_1, 1),
            (MagicItemName.WAND_OF_THE_WAR_MAGE_PLUS_2, 2),
            (MagicItemName.WAND_OF_THE_WAR_MAGE_PLUS_3, 3),
        ],
    )
    def test_war_mage_wands(self, item_name, expected_bonus):
        """Verify War Mage wands have correct spell attack bonuses."""
        wand = MagicItemSettings.objects.get(name=item_name)
        assert wand.effects.get("spell_attack_bonus") == expected_bonus
        assert wand.requires_attunement is True
        assert "spellcaster" in wand.attunement_requirement

    # Wondrous item tests
    def test_amulet_of_health(self):
        """Amulet of Health should set Constitution to 19."""
        item = MagicItemSettings.objects.get(name=MagicItemName.AMULET_OF_HEALTH)
        assert item.effects.get("set_constitution") == 19
        assert item.requires_attunement is True

    def test_gauntlets_of_ogre_power(self):
        """Gauntlets of Ogre Power should set Strength to 19."""
        item = MagicItemSettings.objects.get(name=MagicItemName.GAUNTLETS_OF_OGRE_POWER)
        assert item.effects.get("set_strength") == 19
        assert item.requires_attunement is True

    def test_headband_of_intellect(self):
        """Headband of Intellect should set Intelligence to 19."""
        item = MagicItemSettings.objects.get(name=MagicItemName.HEADBAND_OF_INTELLECT)
        assert item.effects.get("set_intelligence") == 19
        assert item.requires_attunement is True

    def test_bag_of_holding(self):
        """Bag of Holding should have specific capacity."""
        item = MagicItemSettings.objects.get(name=MagicItemName.BAG_OF_HOLDING)
        assert item.effects.get("capacity_pounds") == 500
        assert item.requires_attunement is False


@pytest.mark.django_db
class TestMagicItemModel:
    """Tests for the MagicItem model (concrete instances)."""

    def test_creation(self):
        item = MagicItemFactory()
        assert isinstance(item, MagicItem)

    def test_str(self):
        settings = MagicItemSettings.objects.get(name=MagicItemName.WEAPON_PLUS_1)
        item = MagicItem.objects.create(settings=settings)
        assert str(item) == "Weapon +1"

    def test_charges_initialized_from_settings(self):
        """Items with charges should initialize current_charges from settings."""
        settings = MagicItemSettings.objects.get(
            name=MagicItemName.WAND_OF_MAGIC_MISSILES
        )
        item = MagicItem.objects.create(settings=settings)
        assert item.current_charges == 7
        assert item.max_charges == 7

    def test_use_charge(self):
        """Using a charge should decrement current_charges."""
        settings = MagicItemSettings.objects.get(
            name=MagicItemName.WAND_OF_MAGIC_MISSILES
        )
        item = MagicItem.objects.create(settings=settings)
        assert item.use_charge(1) is True
        item.refresh_from_db()
        assert item.current_charges == 6

    def test_use_multiple_charges(self):
        """Using multiple charges at once should work."""
        settings = MagicItemSettings.objects.get(
            name=MagicItemName.WAND_OF_MAGIC_MISSILES
        )
        item = MagicItem.objects.create(settings=settings)
        assert item.use_charge(3) is True
        item.refresh_from_db()
        assert item.current_charges == 4

    def test_use_charge_insufficient(self):
        """Using more charges than available should fail."""
        settings = MagicItemSettings.objects.get(
            name=MagicItemName.WAND_OF_MAGIC_MISSILES
        )
        item = MagicItem.objects.create(settings=settings)
        item.current_charges = 2
        item.save()
        assert item.use_charge(3) is False
        item.refresh_from_db()
        assert item.current_charges == 2  # Unchanged

    def test_item_without_charges(self):
        """Items without charges should return None for max_charges."""
        settings = MagicItemSettings.objects.get(name=MagicItemName.WEAPON_PLUS_1)
        item = MagicItem.objects.create(settings=settings)
        assert item.max_charges is None
        assert item.current_charges is None

    def test_item_identification(self):
        """Items can be identified or unidentified."""
        settings = MagicItemSettings.objects.get(name=MagicItemName.WEAPON_PLUS_1)
        item = MagicItem.objects.create(settings=settings, is_identified=False)
        assert item.is_identified is False

    def test_item_curse(self):
        """Items can be cursed."""
        settings = MagicItemSettings.objects.get(name=MagicItemName.WEAPON_PLUS_1)
        item = MagicItem.objects.create(settings=settings, is_cursed=True)
        assert item.is_cursed is True
        assert item.curse_revealed is False


@pytest.mark.django_db
class TestAttunementModel:
    """Tests for the Attunement model (character-item relationships)."""

    def test_creation(self):
        """Can create an attunement between character and magic item."""
        character = CharacterFactory()
        settings = MagicItemSettings.objects.get(name=MagicItemName.RING_OF_PROTECTION)
        item = MagicItem.objects.create(settings=settings)
        attunement = Attunement.attune(character, item)
        assert isinstance(attunement, Attunement)
        assert attunement.character == character
        assert attunement.magic_item == item

    def test_str(self):
        """Attunement string representation."""
        character = CharacterFactory()
        settings = MagicItemSettings.objects.get(name=MagicItemName.RING_OF_PROTECTION)
        item = MagicItem.objects.create(settings=settings)
        attunement = Attunement.attune(character, item)
        assert character.name in str(attunement)
        assert "Ring of Protection" in str(attunement)

    def test_max_attunement_slots(self):
        """Characters can only attune to 3 items."""
        assert Attunement.MAX_ATTUNEMENT_SLOTS == 3

    def test_attunement_limit_enforced(self):
        """Cannot attune to more than 3 items."""
        character = CharacterFactory()

        # Create and attune to 3 items
        for name in [
            MagicItemName.RING_OF_PROTECTION,
            MagicItemName.CLOAK_OF_PROTECTION,
            MagicItemName.BOOTS_OF_SPEED,
        ]:
            settings = MagicItemSettings.objects.get(name=name)
            item = MagicItem.objects.create(settings=settings)
            Attunement.attune(character, item)

        # Try to attune to a 4th item
        settings = MagicItemSettings.objects.get(name=MagicItemName.AMULET_OF_HEALTH)
        item = MagicItem.objects.create(settings=settings)
        with pytest.raises(ValidationError) as exc_info:
            Attunement.attune(character, item)
        assert "Cannot attune to more than 3 items" in str(exc_info.value)

    def test_cannot_attune_non_attunement_item(self):
        """Cannot attune to items that don't require attunement."""
        character = CharacterFactory()
        settings = MagicItemSettings.objects.get(name=MagicItemName.WEAPON_PLUS_1)
        item = MagicItem.objects.create(settings=settings)
        with pytest.raises(ValidationError) as exc_info:
            Attunement.attune(character, item)
        assert "does not require attunement" in str(exc_info.value)

    def test_end_attunement(self):
        """Can end attunement to free up a slot."""
        character = CharacterFactory()
        settings = MagicItemSettings.objects.get(name=MagicItemName.RING_OF_PROTECTION)
        item = MagicItem.objects.create(settings=settings)
        attunement = Attunement.attune(character, item)

        assert Attunement.get_attunement_count(character) == 1
        attunement.end_attunement()
        assert Attunement.get_attunement_count(character) == 0

    def test_get_available_slots(self):
        """Can check available attunement slots."""
        character = CharacterFactory()
        assert Attunement.get_available_slots(character) == 3

        settings = MagicItemSettings.objects.get(name=MagicItemName.RING_OF_PROTECTION)
        item = MagicItem.objects.create(settings=settings)
        Attunement.attune(character, item)

        assert Attunement.get_available_slots(character) == 2

    def test_attunement_freed_after_ending(self):
        """Can attune to new item after ending previous attunement."""
        character = CharacterFactory()

        # Attune to 3 items
        attunements = []
        for name in [
            MagicItemName.RING_OF_PROTECTION,
            MagicItemName.CLOAK_OF_PROTECTION,
            MagicItemName.BOOTS_OF_SPEED,
        ]:
            settings = MagicItemSettings.objects.get(name=name)
            item = MagicItem.objects.create(settings=settings)
            attunements.append(Attunement.attune(character, item))

        # End one attunement
        attunements[0].end_attunement()

        # Should now be able to attune to a new item
        settings = MagicItemSettings.objects.get(name=MagicItemName.AMULET_OF_HEALTH)
        item = MagicItem.objects.create(settings=settings)
        new_attunement = Attunement.attune(character, item)
        assert new_attunement is not None
        assert Attunement.get_attunement_count(character) == 3
