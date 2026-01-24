import factory

from character.constants.abilities import AbilityName
from character.constants.backgrounds import Background
from character.constants.conditions import ConditionName
from character.constants.feats import FeatName, FeatType
from character.constants.equipment import (
    ArmorName,
    ArmorType,
    GearName,
    PackName,
    ToolName,
    WeaponType,
    WeaponName,
)
from character.constants.classes import ClassName
from character.constants.species import SpeciesName, SpeciesTraitName
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from character.models.conditions import CharacterCondition, Condition
from character.models.feats import CharacterFeat, Feat
from character.models.equipment import (
    Armor,
    ArmorSettings,
    Gear,
    GearSettings,
    Inventory,
    Pack,
    PackSettings,
    Tool,
    ToolSettings,
    Weapon,
    WeaponSettings,
)
from character.models.classes import (
    CharacterClass,
    CharacterFeature,
    Class,
    ClassFeature,
)
from character.models.species import Species, SpeciesTrait
from character.models.spells import (
    CharacterSpellSlot,
    ClassSpellcasting,
    Concentration,
    Spell,
    SpellPreparation,
    SpellSettings,
    SpellSlotTable,
    WarlockSpellSlot,
)
from character.models.spell_effects import (
    ActiveSpellEffect,
    SpellEffectTemplate,
    SummonedCreature,
)
from character.models.magic_items import (
    Attunement,
    MagicItem,
    MagicItemSettings,
)
from character.constants.magic_items import (
    MagicItemName,
    MagicItemType,
    Rarity,
)
from character.models.monsters import (
    LairActionTemplate,
    LegendaryActionTemplate,
    Monster,
    MonsterActionTemplate,
    MonsterMultiattack,
    MonsterReaction,
    MonsterSettings,
    MonsterTrait,
    MultiattackAction,
)
from character.constants.monsters import (
    ActionType,
    Alignment,
    ChallengeRating,
    CreatureSize,
    CreatureType,
    DamageType,
    MonsterName,
)
from character.constants.spells import (
    CasterType,
    CastingTime,
    EffectDurationType,
    SpellDamageType,
    SpellDuration,
    SpellEffectType,
    SpellLevel,
    SpellRange,
    SpellSaveEffect,
    SpellSaveType,
    SpellSchool,
    SpellTargetType,
    SpellcastingAbility,
)


class AbilityTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AbilityType
        django_get_or_create = ("name",)

    name = factory.Faker("enum", enum_cls=AbilityName)


class AbilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ability

    ability_type = factory.SubFactory(AbilityTypeFactory)
    score = factory.Faker("random_int")
    modifier = factory.Faker("random_int", min=-5, max=5)


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory


class SpeciesTraitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpeciesTrait
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=SpeciesTraitName)
    description = factory.Faker("text", max_nb_chars=200)


class SpeciesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Species
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=SpeciesName)
    size = "M"
    speed = 30
    darkvision = 0


class CharacterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Character
        django_get_or_create = ("user",)

    name = factory.Sequence(lambda n: f"character{n}")
    user = factory.SubFactory("user.tests.factories.UserFactory")
    species = factory.SubFactory(SpeciesFactory)
    background = factory.Faker("enum", enum_cls=Background)
    xp = factory.Faker("random_int")
    inventory = factory.SubFactory(InventoryFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        character = model_class(*args, **kwargs)
        character.save()
        for ability_name, _ in AbilityName.choices:
            ability = AbilityFactory(ability_type__name=ability_name)
            character.abilities.add(ability)
        return character


class ArmorSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ArmorSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ArmorName)
    armor_type = ArmorType.LIGHT_ARMOR
    cost = factory.Faker("random_int")
    ac = factory.Faker("pystr", max_chars=5)
    weight = factory.Faker("random_int")


class ArmorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Armor

    settings = factory.SubFactory(ArmorSettingsFactory)


class WeponSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WeaponSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=WeaponName)
    weapon_type = WeaponType.SIMPLE_MELEE
    cost = factory.Faker("random_int")
    damage = factory.Faker("pystr", max_chars=5)
    weight = factory.Faker("random_int")
    properties = ""


class WeaponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Weapon

    settings = factory.SubFactory(WeponSettingsFactory)


class PackSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=PackName)


class PackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Pack

    settings = factory.SubFactory(PackSettingsFactory)


class GearSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GearSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=GearName)


class GearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Gear

    settings = factory.SubFactory(GearSettingsFactory)


class ToolSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ToolSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ToolName)


class ToolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tool

    settings = factory.SubFactory(ToolSettingsFactory)


class ConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Condition
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ConditionName)
    description = factory.Faker("text", max_nb_chars=200)


class CharacterConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterCondition

    character = factory.SubFactory(CharacterFactory)
    condition = factory.SubFactory(ConditionFactory)


class FeatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feat
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=FeatName)
    feat_type = FeatType.ORIGIN
    description = factory.Faker("text", max_nb_chars=200)


class CharacterFeatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterFeat

    character = factory.SubFactory(CharacterFactory)
    feat = factory.SubFactory(FeatFactory)
    granted_by = "background"


class ClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Class
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=ClassName)
    description = factory.Faker("text", max_nb_chars=200)
    hit_die = 10
    hp_first_level = 10
    hp_higher_levels = 6
    primary_ability = factory.SubFactory(AbilityTypeFactory, name="STR")
    armor_proficiencies = factory.LazyFunction(list)
    weapon_proficiencies = factory.LazyFunction(list)
    starting_wealth_dice = "5d4"


class ClassFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassFeature

    name = factory.Faker("word")
    klass = factory.SubFactory(ClassFactory)
    level = 1
    description = factory.Faker("text", max_nb_chars=500)


class CharacterClassFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterClass

    character = factory.SubFactory(CharacterFactory)
    klass = factory.SubFactory(ClassFactory)
    level = 1
    is_primary = True


class CharacterFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterFeature

    character = factory.SubFactory(CharacterFactory)
    class_feature = factory.SubFactory(ClassFeatureFactory)
    source_class = factory.SubFactory(ClassFactory)
    level_gained = 1


class SpellSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellSettings
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Test Spell {n}")
    level = SpellLevel.FIRST
    school = factory.Faker("random_element", elements=SpellSchool)
    casting_time = CastingTime.ACTION
    range = SpellRange.FEET_60
    components = ["V", "S"]
    duration = SpellDuration.INSTANTANEOUS
    concentration = False
    ritual = False
    description = factory.Faker("text", max_nb_chars=500)
    classes = ["wizard", "sorcerer"]


class SpellFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Spell

    character = factory.SubFactory(CharacterFactory)
    settings = factory.SubFactory(SpellSettingsFactory)
    source = "class"


class SpellPreparationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellPreparation

    character = factory.SubFactory(CharacterFactory)
    settings = factory.SubFactory(SpellSettingsFactory)
    always_prepared = False


class SpellSlotTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellSlotTable
        django_get_or_create = ("class_name", "class_level", "slot_level")

    class_name = ClassName.WIZARD
    class_level = 1
    slot_level = 1
    slots = 2


class CharacterSpellSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CharacterSpellSlot

    character = factory.SubFactory(CharacterFactory)
    slot_level = 1
    total = 2
    used = 0


class WarlockSpellSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WarlockSpellSlot

    character = factory.SubFactory(CharacterFactory)
    slot_level = 1
    total = 1
    used = 0


class ClassSpellcastingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassSpellcasting
        django_get_or_create = ("klass",)

    klass = factory.SubFactory(ClassFactory)
    caster_type = CasterType.PREPARED
    spellcasting_ability = SpellcastingAbility.INTELLIGENCE
    learns_cantrips = True
    spell_list_access = True
    ritual_casting = True
    spellcasting_focus = "arcane focus"


class ConcentrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Concentration

    character = factory.SubFactory(CharacterFactory)
    spell = factory.SubFactory(SpellSettingsFactory, concentration=True)


class SpellEffectTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellEffectTemplate

    spell = factory.SubFactory(SpellSettingsFactory)
    effect_type = SpellEffectType.DAMAGE
    target_type = SpellTargetType.SINGLE
    damage_type = SpellDamageType.FIRE
    base_dice = "8d6"
    dice_per_level = "1d6"
    save_type = SpellSaveType.DEXTERITY
    save_effect = SpellSaveEffect.HALF_DAMAGE
    duration_type = EffectDurationType.INSTANTANEOUS


class ActiveSpellEffectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActiveSpellEffect

    character = factory.SubFactory(CharacterFactory)
    template = factory.SubFactory(SpellEffectTemplateFactory)
    caster = factory.SubFactory(CharacterFactory)
    rounds_remaining = 10
    is_concentration = False


class SummonedCreatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SummonedCreature

    summoner = factory.SubFactory(CharacterFactory)
    spell = factory.SubFactory(SpellSettingsFactory)
    name = factory.Faker("first_name")
    hp_current = 20
    hp_max = 20
    ac = 13
    rounds_remaining = 10
    is_concentration = True


class MagicItemSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MagicItemSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=MagicItemName)
    item_type = MagicItemType.WONDROUS
    rarity = Rarity.UNCOMMON
    requires_attunement = False
    description = factory.Faker("text", max_nb_chars=200)


class MagicItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MagicItem

    settings = factory.SubFactory(MagicItemSettingsFactory)
    inventory = factory.SubFactory(InventoryFactory)


class AttunementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attunement

    character = factory.SubFactory(CharacterFactory)
    magic_item = factory.SubFactory(MagicItemFactory)


class MonsterSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSettings
        django_get_or_create = ("name",)

    name = factory.Faker("random_element", elements=MonsterName)
    size = CreatureSize.MEDIUM
    creature_type = CreatureType.HUMANOID
    alignment = Alignment.TRUE_NEUTRAL
    ac = 10
    hit_dice = "1d8"
    hp_average = 4
    speed = factory.LazyFunction(lambda: {"walk": 30})
    strength = 10
    dexterity = 10
    constitution = 10
    intelligence = 10
    wisdom = 10
    charisma = 10
    challenge_rating = ChallengeRating.CR_0
    proficiency_bonus = 2
    senses = factory.LazyFunction(lambda: {"passive_perception": 10})


class MonsterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Monster

    settings = factory.SubFactory(MonsterSettingsFactory)
    hp_current = factory.LazyAttribute(lambda o: o.settings.hp_average)
    hp_max = factory.LazyAttribute(lambda o: o.settings.hp_average)


class MonsterActionTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterActionTemplate

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Action {n}")
    action_type = ActionType.MELEE_WEAPON
    attack_bonus = 5
    reach = 5
    targets = "one target"
    damage_dice = "1d8+3"
    damage_type = DamageType.SLASHING


class MonsterMultiattackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterMultiattack

    monster = factory.SubFactory(MonsterSettingsFactory)
    description = "The creature makes two attacks."


class MultiattackActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MultiattackAction

    multiattack = factory.SubFactory(MonsterMultiattackFactory)
    action = factory.SubFactory(MonsterActionTemplateFactory)
    count = 2


class LegendaryActionTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LegendaryActionTemplate

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Legendary Action {n}")
    description = "The creature performs a legendary action."
    cost = 1


class LairActionTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LairActionTemplate

    monster = factory.SubFactory(MonsterSettingsFactory)
    description = "A lair effect occurs."


class MonsterTraitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterTrait

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Trait {n}")
    description = "This creature has a special trait."


class MonsterReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterReaction

    monster = factory.SubFactory(MonsterSettingsFactory)
    name = factory.Sequence(lambda n: f"Reaction {n}")
    description = "The creature reacts."
    trigger = "When attacked"
