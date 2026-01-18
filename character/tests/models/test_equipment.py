from django.db.models import TextChoices
import pytest
from faker import Faker

from character.constants.abilities import AbilityName
from character.constants.equipment import (
    ArmorName,
    ArmorType,
    Disadvantage,
    ToolName,
    WeaponMastery,
    WeaponName,
    WeaponType,
)
from character.models.equipment import (
    ArmorSettings,
    GearSettings,
    Inventory,
    PackSettings,
    ToolSettings,
    WeaponSettings,
)

from ..factories import (
    ArmorFactory,
    ArmorSettingsFactory,
    CharacterFactory,
    GearFactory,
    InventoryFactory,
    PackFactory,
    WeaponFactory,
)


@pytest.mark.django_db
class TestWeaponModel:
    weapon = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.weapon = WeaponSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.weapon, WeaponSettings)

    def test_str(self):
        assert str(self.weapon) == self.weapon.name


@pytest.mark.django_db
class TestWeaponSettingsFixture:
    """Tests for the SRD weapon database fixture."""

    def test_total_weapon_count(self):
        """SRD 5.2.1 has 37 weapons."""
        assert WeaponSettings.objects.count() == 37

    def test_simple_melee_count(self):
        """10 simple melee weapons in SRD."""
        count = WeaponSettings.objects.filter(
            weapon_type=WeaponType.SIMPLE_MELEE
        ).count()
        assert count == 10

    def test_simple_ranged_count(self):
        """4 simple ranged weapons in SRD."""
        count = WeaponSettings.objects.filter(
            weapon_type=WeaponType.SIMPLE_RANGED
        ).count()
        assert count == 4

    def test_martial_melee_count(self):
        """18 martial melee weapons in SRD."""
        count = WeaponSettings.objects.filter(
            weapon_type=WeaponType.MARTIAL_MELEE
        ).count()
        assert count == 18

    def test_martial_ranged_count(self):
        """5 martial ranged weapons in SRD."""
        count = WeaponSettings.objects.filter(
            weapon_type=WeaponType.MARTIAL_RANGED
        ).count()
        assert count == 5

    def test_all_weapons_have_mastery_except_net(self):
        """All weapons should have a mastery property except Net."""
        weapons_without_mastery = WeaponSettings.objects.filter(mastery__isnull=True)
        assert weapons_without_mastery.count() == 1
        assert weapons_without_mastery.first().name == WeaponName.NET

    def test_mastery_values_are_valid(self):
        """All mastery values should be valid WeaponMastery choices."""
        valid_masteries = [choice[0] for choice in WeaponMastery.choices]
        weapons_with_mastery = WeaponSettings.objects.exclude(mastery__isnull=True)
        for weapon in weapons_with_mastery:
            assert weapon.mastery in valid_masteries, (
                f"{weapon.name} has invalid mastery: {weapon.mastery}"
            )

    @pytest.mark.parametrize(
        "weapon_name,expected_damage,expected_mastery",
        [
            # Simple Melee
            (WeaponName.CLUB, "1d4 bludgeoning", WeaponMastery.SLOW),
            (WeaponName.DAGGER, "1d4 piercing", WeaponMastery.NICK),
            (WeaponName.GREATCLUB, "1d8 bludgeoning", WeaponMastery.PUSH),
            (WeaponName.HANDAXE, "1d6 slashing", WeaponMastery.VEX),
            (WeaponName.MACE, "1d6 bludgeoning", WeaponMastery.SAP),
            (WeaponName.QUARTERSTAFF, "1d6 bludgeoning", WeaponMastery.TOPPLE),
            (WeaponName.SPEAR, "1d6 piercing", WeaponMastery.SAP),
            # Simple Ranged
            (WeaponName.CROSSBOW_LIGHT, "1d8 piercing", WeaponMastery.SLOW),
            (WeaponName.SHORTBOW, "1d6 piercing", WeaponMastery.VEX),
            # Martial Melee
            (WeaponName.LONGSWORD, "1d8 slashing", WeaponMastery.SAP),
            (WeaponName.GREATSWORD, "2d6 slashing", WeaponMastery.GRAZE),
            (WeaponName.GREATAXE, "1d12 slashing", WeaponMastery.CLEAVE),
            (WeaponName.RAPIER, "1d8 piercing", WeaponMastery.VEX),
            (WeaponName.SCIMITAR, "1d6 slashing", WeaponMastery.NICK),
            (WeaponName.MAUL, "2d6 bludgeoning", WeaponMastery.TOPPLE),
            (WeaponName.HALBERD, "1d10 slashing", WeaponMastery.CLEAVE),
            (WeaponName.PIKE, "1d10 piercing", WeaponMastery.PUSH),
            (WeaponName.WHIP, "1d4 slashing", WeaponMastery.SLOW),
            # Martial Ranged
            (WeaponName.LONGBOW, "1d8 piercing", WeaponMastery.SLOW),
            (WeaponName.CROSSBOW_HEAVY, "1d10 piercing", WeaponMastery.PUSH),
            (WeaponName.CROSSBOW_HAND, "1d6 piercing", WeaponMastery.VEX),
        ],
    )
    def test_weapon_damage_and_mastery(
        self, weapon_name, expected_damage, expected_mastery
    ):
        """Verify specific weapon damage and mastery values per SRD 5.2.1."""
        weapon = WeaponSettings.objects.get(name=weapon_name)
        assert weapon.damage == expected_damage
        assert weapon.mastery == expected_mastery

    @pytest.mark.parametrize(
        "weapon_name,expected_properties",
        [
            (WeaponName.DAGGER, "Finesse, light, thrown (range 20/60)"),
            (WeaponName.LONGSWORD, "Versatile (1d10)"),
            (WeaponName.GREATSWORD, "Heavy, two-handed"),
            (WeaponName.RAPIER, "Finesse"),
            (WeaponName.LONGBOW, "Ammunition (range 150/600), heavy, two-handed"),
            (WeaponName.GLAIVE, "Heavy, reach, two-handed"),
            (WeaponName.WHIP, "Finesse, reach"),
        ],
    )
    def test_weapon_properties(self, weapon_name, expected_properties):
        """Verify weapon properties match SRD 5.2.1."""
        weapon = WeaponSettings.objects.get(name=weapon_name)
        assert weapon.properties == expected_properties

    @pytest.mark.parametrize(
        "weapon_name,expected_cost,expected_weight",
        [
            (WeaponName.DAGGER, 2, 1),
            (WeaponName.LONGSWORD, 15, 3),
            (WeaponName.GREATSWORD, 50, 6),
            (WeaponName.GREATAXE, 30, 7),
            (WeaponName.LONGBOW, 50, 2),
            (WeaponName.CROSSBOW_HAND, 75, 3),
            (WeaponName.PIKE, 5, 18),
        ],
    )
    def test_weapon_cost_and_weight(self, weapon_name, expected_cost, expected_weight):
        """Verify weapon cost (in gp) and weight (in lb) match SRD 5.2.1."""
        weapon = WeaponSettings.objects.get(name=weapon_name)
        assert weapon.cost == expected_cost
        assert weapon.weight == expected_weight

    def test_net_has_no_damage(self):
        """Net is a special weapon with no damage."""
        net = WeaponSettings.objects.get(name=WeaponName.NET)
        assert net.damage is None
        assert net.mastery is None
        assert "Special" in net.properties


@pytest.mark.django_db
class TestArmorModel:
    armor = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.armor = ArmorSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.armor, ArmorSettings)

    def test_str(self):
        assert str(self.armor) == self.armor.name


@pytest.mark.django_db
class TestArmorSettingsFixture:
    """Tests for the SRD armor database fixture."""

    def test_total_armor_count(self):
        """SRD has 13 armor types (12 armors + 1 shield)."""
        assert ArmorSettings.objects.count() == 13

    def test_light_armor_count(self):
        """3 light armors in SRD."""
        count = ArmorSettings.objects.filter(armor_type=ArmorType.LIGHT_ARMOR).count()
        assert count == 3

    def test_medium_armor_count(self):
        """5 medium armors in SRD."""
        count = ArmorSettings.objects.filter(armor_type=ArmorType.MEDIUM_ARMOR).count()
        assert count == 5

    def test_heavy_armor_count(self):
        """4 heavy armors in SRD."""
        count = ArmorSettings.objects.filter(armor_type=ArmorType.HEAVY_ARMOR).count()
        assert count == 4

    def test_shield_count(self):
        """1 shield in SRD."""
        count = ArmorSettings.objects.filter(armor_type=ArmorType.SHIELD).count()
        assert count == 1

    # Light Armor Tests - AC = base + full DEX modifier
    @pytest.mark.parametrize(
        "armor_name,expected_ac,expected_cost,expected_weight",
        [
            (ArmorName.PADDED, "11 + Dex modifier", 5, 8),
            (ArmorName.LEATHER, "11 + Dex modifier", 10, 10),
            (ArmorName.STUDDED_LEATHER, "12 + Dex modifier", 45, 13),
        ],
    )
    def test_light_armor_stats(
        self, armor_name, expected_ac, expected_cost, expected_weight
    ):
        """Light armor: AC = base + full DEX modifier."""
        armor = ArmorSettings.objects.get(name=armor_name)
        assert armor.armor_type == ArmorType.LIGHT_ARMOR
        assert armor.ac == expected_ac
        assert armor.cost == expected_cost
        assert armor.weight == expected_weight

    # Medium Armor Tests - AC = base + DEX modifier (max 2)
    @pytest.mark.parametrize(
        "armor_name,expected_ac,expected_cost,expected_weight",
        [
            (ArmorName.HIDE, "12 + Dex modifier (max 2)", 10, 12),
            (ArmorName.CHAIN_SHIRT, "13 + Dex modifier (max 2)", 50, 20),
            (ArmorName.SCALE_MAIL, "14 + Dex modifier (max 2)", 50, 45),
            (ArmorName.BREASTPLATE, "14 + Dex modifier (max 2)", 400, 20),
            (ArmorName.HALF_PLATE, "15 + Dex modifier (max 2)", 750, 40),
        ],
    )
    def test_medium_armor_stats(
        self, armor_name, expected_ac, expected_cost, expected_weight
    ):
        """Medium armor: AC = base + DEX modifier (max 2)."""
        armor = ArmorSettings.objects.get(name=armor_name)
        assert armor.armor_type == ArmorType.MEDIUM_ARMOR
        assert armor.ac == expected_ac
        assert armor.cost == expected_cost
        assert armor.weight == expected_weight

    # Heavy Armor Tests - AC = base (no DEX modifier)
    @pytest.mark.parametrize(
        "armor_name,expected_ac,expected_cost,expected_weight,expected_strength",
        [
            (ArmorName.RING_MAIL, "14", 30, 40, None),
            (ArmorName.CHAIN_MAIL, "16", 75, 55, "Str 13"),
            (ArmorName.SPLINT, "17", 200, 60, "Str 15"),
            (ArmorName.PLATE, "18", 1500, 65, "Str 15"),
        ],
    )
    def test_heavy_armor_stats(
        self, armor_name, expected_ac, expected_cost, expected_weight, expected_strength
    ):
        """Heavy armor: AC = base (no DEX modifier), may have STR requirement."""
        armor = ArmorSettings.objects.get(name=armor_name)
        assert armor.armor_type == ArmorType.HEAVY_ARMOR
        assert armor.ac == expected_ac
        assert armor.cost == expected_cost
        assert armor.weight == expected_weight
        assert armor.strength == expected_strength

    def test_shield_stats(self):
        """Shield: +2 AC bonus."""
        shield = ArmorSettings.objects.get(name=ArmorName.SHIELD)
        assert shield.armor_type == ArmorType.SHIELD
        assert shield.ac == "+2"
        assert shield.cost == 10
        assert shield.weight == 6

    # Stealth Disadvantage Tests
    @pytest.mark.parametrize(
        "armor_name",
        [
            ArmorName.PADDED,
            ArmorName.SCALE_MAIL,
            ArmorName.HALF_PLATE,
            ArmorName.RING_MAIL,
            ArmorName.CHAIN_MAIL,
            ArmorName.SPLINT,
            ArmorName.PLATE,
        ],
    )
    def test_armor_with_stealth_disadvantage(self, armor_name):
        """Certain armors impose disadvantage on Stealth checks."""
        armor = ArmorSettings.objects.get(name=armor_name)
        assert armor.stealth == Disadvantage.DISADVANTAGE

    @pytest.mark.parametrize(
        "armor_name",
        [
            ArmorName.LEATHER,
            ArmorName.STUDDED_LEATHER,
            ArmorName.HIDE,
            ArmorName.CHAIN_SHIRT,
            ArmorName.BREASTPLATE,
            ArmorName.SHIELD,
        ],
    )
    def test_armor_without_stealth_disadvantage(self, armor_name):
        """Certain armors do not impose disadvantage on Stealth checks."""
        armor = ArmorSettings.objects.get(name=armor_name)
        assert armor.stealth is None

    # Strength Requirement Tests
    @pytest.mark.parametrize(
        "armor_name,expected_strength",
        [
            (ArmorName.CHAIN_MAIL, "Str 13"),
            (ArmorName.SPLINT, "Str 15"),
            (ArmorName.PLATE, "Str 15"),
        ],
    )
    def test_armor_with_strength_requirement(self, armor_name, expected_strength):
        """Heavy armors may require minimum strength."""
        armor = ArmorSettings.objects.get(name=armor_name)
        assert armor.strength == expected_strength

    def test_light_armor_no_strength_requirement(self):
        """Light armors have no strength requirement."""
        light_armors = ArmorSettings.objects.filter(armor_type=ArmorType.LIGHT_ARMOR)
        for armor in light_armors:
            assert armor.strength is None or armor.strength == ""

    def test_medium_armor_no_strength_requirement(self):
        """Medium armors have no strength requirement."""
        medium_armors = ArmorSettings.objects.filter(armor_type=ArmorType.MEDIUM_ARMOR)
        for armor in medium_armors:
            assert armor.strength is None or armor.strength == ""


@pytest.mark.django_db
class TestPackModel:
    pack = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.pack = PackSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.pack, PackSettings)

    def test_str(self):
        assert str(self.pack) == self.pack.name


@pytest.mark.django_db
class TestGearModel:
    gear = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.gear = GearSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.gear, GearSettings)

    def test_str(self):
        assert str(self.gear) == self.gear.name


@pytest.mark.django_db
class TestToolModel:
    tool = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.tool = ToolSettings.objects.last()

    def test_creation(self):
        assert isinstance(self.tool, ToolSettings)

    def test_str(self):
        assert str(self.tool) == self.tool.name


@pytest.mark.django_db
class TestInventoryModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.inventory = InventoryFactory()
        self.inventory.character = CharacterFactory()

    def test_creation(self):
        assert isinstance(self.inventory, Inventory)

    def test_add_armor_simple_ac(self):
        ring_mail_settings = ArmorSettingsFactory(name=ArmorName.RING_MAIL, ac="14")
        ring_mail = ArmorFactory(settings=ring_mail_settings)
        self.inventory.add(ring_mail.settings.name)
        assert self.inventory.character.ac == 14

    def test_add_armor_ac_plus_dex_modifier(self):
        padded_settings = ArmorSettingsFactory(
            name=ArmorName.PADDED, ac="11 + Dex modifier"
        )
        padded = ArmorFactory(settings=padded_settings)
        self.inventory.add(padded.settings.name)
        dex_modifier = self.inventory.character.abilities.get(
            ability_type__name=AbilityName.DEXTERITY
        ).modifier
        assert self.inventory.character.ac == 11 + dex_modifier

    def test_add_armor_ac_plus_dex_modifier_max(self):
        hide_settings = ArmorSettingsFactory(
            name=ArmorName.HIDE, ac="12 + Dex modifier (max 2)"
        )
        hide = ArmorFactory(settings=hide_settings)
        self.inventory.add(hide.settings.name)
        dex_modifier = self.inventory.character.abilities.get(
            ability_type__name=AbilityName.DEXTERITY
        ).modifier
        if dex_modifier > 2:
            assert self.inventory.character.ac == 12 + 2
        else:
            assert self.inventory.character.ac == 12 + dex_modifier

    def test_contains_armor(self):
        armor = ArmorFactory()
        self.inventory.armor_set.add(armor)
        assert self.inventory.contains(armor.settings.name)

    def test_contains_weapon(self):
        weapon = WeaponFactory()
        self.inventory.weapon_set.add(weapon)
        assert self.inventory.contains(weapon.settings.name)

    def test_contains_pack(self):
        pack = PackFactory()
        self.inventory.pack_set.add(pack)
        assert self.inventory.contains(pack.settings.name)

    def test_contains_gear(self):
        gear = GearFactory()
        self.inventory.gear_set.add(gear)
        assert self.inventory.contains(gear.settings.name)

    def test_contains_tool(self):
        fake = Faker()
        tool_name = fake.enum(enum_cls=ToolName)
        self.inventory.add(tool_name)
        assert self.inventory.contains(tool_name)

    def test_contains_unkown_equipment(self):
        class UnknownEquipment(TextChoices):
            UNKNOWN_EQUIPMENT = "unknown_equipment", "Unknown equipment"

        assert not self.inventory.contains(UnknownEquipment.UNKNOWN_EQUIPMENT)

    def test_contains_below_quantity(self):
        weapon = WeaponFactory()
        self.inventory.weapon_set.add(weapon)
        self.inventory.weapon_set.add(weapon)
        assert not self.inventory.contains(weapon.settings.name, 3)

    def test_contains_above_quantity(self):
        weapon = WeaponFactory()
        self.inventory.weapon_set.add(weapon)
        self.inventory.weapon_set.add(weapon)
        assert self.inventory.contains(weapon.settings.name)
