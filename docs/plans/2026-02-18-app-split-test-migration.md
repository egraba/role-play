# App Split Test Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move bestiary/equipment/magic tests and factories out of `character/tests/` into their correct app directories, completing the app split refactoring.

**Architecture:** Per-app factory files in `{app}/tests/factories.py`; `character/tests/factories.py` becomes a re-export aggregator. Factory-boy's lazy string SubFactory (`'character.tests.factories.CharacterFactory'`) breaks the circular import between magic/equipment factories and CharacterFactory. Six test files are moved and their relative factory imports are updated to absolute app-specific imports.

**Tech Stack:** pytest-django, factory-boy, Django fixtures

---

## Reference

### Factory ownership after migration

| Factory | Destination |
|---|---|
| MonsterSettingsFactory, MonsterFactory, MonsterActionTemplateFactory, MonsterMultiattackFactory, MultiattackActionFactory, LegendaryActionTemplateFactory, LairActionTemplateFactory, MonsterTraitFactory, MonsterReactionFactory, MonsterSpeedFactory, MonsterSavingThrowFactory, MonsterSkillFactory, MonsterSenseFactory, MonsterDamageRelationFactory, MonsterConditionImmunityFactory, MonsterLanguageFactory | `bestiary/tests/factories.py` |
| InventoryFactory, ArmorSettingsFactory, ArmorFactory, WeponSettingsFactory, WeaponFactory, PackSettingsFactory, PackFactory, GearSettingsFactory, GearFactory, ToolSettingsFactory, ToolFactory, MagicItemSettingsFactory, MagicItemFactory, AttunementFactory | `equipment/tests/factories.py` |
| SpellSettingsFactory, SpellFactory, SpellPreparationFactory, SpellSlotTableFactory, CharacterSpellSlotFactory, WarlockSpellSlotFactory, ClassSpellcastingFactory, ConcentrationFactory, SpellEffectTemplateFactory, ActiveSpellEffectFactory, SummonedCreatureFactory | `magic/tests/factories.py` |
| AbilityTypeFactory, AbilityFactory, SpeciesTraitFactory, SpeciesFactory, CharacterFactory, ConditionFactory, CharacterConditionFactory, FeatFactory, CharacterFeatFactory, ClassFactory, ClassFeatureFactory, CharacterClassFactory, CharacterFeatureFactory | stays in `character/tests/factories.py` |

### Test file moves

| From | To |
|---|---|
| `character/tests/models/test_monsters.py` | `bestiary/tests/models/test_monsters.py` |
| `character/tests/models/test_equipment.py` | `equipment/tests/models/test_equipment.py` |
| `character/tests/models/test_magic_items.py` | `equipment/tests/models/test_magic_items.py` |
| `character/tests/utils/test_equipment_parsers.py` | `equipment/tests/utils/test_equipment_parsers.py` |
| `character/tests/models/test_spells.py` | `magic/tests/models/test_spells.py` |
| `character/tests/models/test_spell_effects.py` | `magic/tests/models/test_spell_effects.py` |

---

## Task 1: Create branch and add magic fixtures to conftest.py

**Files:**
- Modify: `conftest.py`

**Step 1: Create branch**

```bash
git checkout -b refactor/complete-app-split
```

**Step 2: Add magic fixtures**

In `conftest.py`, the `FIXTURES` list ends with bestiary fixtures. Add two entries after `"bestiary/fixtures/monster_attributes.yaml"`:

```python
FIXTURES = [
    "character/fixtures/advancement.yaml",
    "character/fixtures/abilities.yaml",
    "character/fixtures/languages.yaml",
    "character/fixtures/classes.yaml",
    "character/fixtures/class_features.yaml",
    "character/fixtures/skills.yaml",
    "equipment/fixtures/equipment.yaml",
    "character/fixtures/species_traits.yaml",
    "character/fixtures/species.yaml",
    "character/fixtures/feats.yaml",
    "equipment/fixtures/magic_items.yaml",
    "bestiary/fixtures/monsters.yaml",
    "bestiary/fixtures/monster_attributes.yaml",
    "magic/fixtures/spells.yaml",          # ADD
    "magic/fixtures/spell_effects.yaml",   # ADD
]
```

**Step 3: Run tests to verify fixtures load cleanly**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass (same count as before).

**Step 4: Commit**

```bash
git add conftest.py
git commit -m "fix: load magic fixtures in test session setup"
```

---

## Task 2: Create bestiary/tests/factories.py

**Files:**
- Create: `bestiary/tests/factories.py`

**Step 1: Create the file with all monster factories**

```python
import factory

from bestiary.constants.monsters import (
    ActionType,
    Alignment,
    ChallengeRating,
    CreatureSize,
    CreatureType,
    DamageRelationType,
    DamageType,
    MonsterName,
    MovementType,
    SenseType,
)
from bestiary.models.monsters import (
    LairActionTemplate,
    LegendaryActionTemplate,
    Monster,
    MonsterActionTemplate,
    MonsterConditionImmunity,
    MonsterDamageRelation,
    MonsterLanguage,
    MonsterMultiattack,
    MonsterReaction,
    MonsterSavingThrow,
    MonsterSense,
    MonsterSettings,
    MonsterSkill,
    MonsterSpeed,
    MonsterTrait,
    MultiattackAction,
)


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
    passive_perception = 10
    strength = 10
    dexterity = 10
    constitution = 10
    intelligence = 10
    wisdom = 10
    charisma = 10
    challenge_rating = ChallengeRating.CR_0
    proficiency_bonus = 2


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


class MonsterSpeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSpeed

    monster = factory.SubFactory(MonsterSettingsFactory)
    movement_type = MovementType.WALK
    feet = 30


class MonsterSavingThrowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSavingThrow

    monster = factory.SubFactory(MonsterSettingsFactory)
    ability = "STR"
    bonus = 5


class MonsterSkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSkill

    monster = factory.SubFactory(MonsterSettingsFactory)
    skill = "Perception"
    bonus = 3


class MonsterSenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterSense

    monster = factory.SubFactory(MonsterSettingsFactory)
    sense_type = SenseType.DARKVISION
    range_feet = 60


class MonsterDamageRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterDamageRelation

    monster = factory.SubFactory(MonsterSettingsFactory)
    damage_type = DamageType.FIRE
    relation_type = DamageRelationType.IMMUNITY


class MonsterConditionImmunityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterConditionImmunity

    monster = factory.SubFactory(MonsterSettingsFactory)
    condition = "poisoned"


class MonsterLanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MonsterLanguage

    monster = factory.SubFactory(MonsterSettingsFactory)
    language = "Common"
```

**Step 2: Run tests to confirm nothing broken**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass.

**Step 3: Commit**

```bash
git add bestiary/tests/factories.py
git commit -m "feat: add bestiary/tests/factories.py"
```

---

## Task 3: Create equipment/tests/factories.py

**Files:**
- Create: `equipment/tests/factories.py`

**Step 1: Create the file**

Note: `AttunementFactory` has a FK to `Character`. Use factory-boy's lazy string syntax to avoid a circular import with `character/tests/factories.py`.

```python
import factory

from equipment.constants.equipment import (
    ArmorName,
    ArmorType,
    GearName,
    GearType,
    PackName,
    ToolName,
    ToolType,
    WeaponMastery,
    WeaponName,
    WeaponType,
)
from equipment.constants.magic_items import (
    MagicItemName,
    MagicItemType,
    Rarity,
)
from equipment.models.equipment import (
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
from equipment.models.magic_items import (
    Attunement,
    MagicItem,
    MagicItemSettings,
)


class InventoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Inventory


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

    # Lazy string avoids circular import with character.tests.factories
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    magic_item = factory.SubFactory(MagicItemFactory)
```

**Step 2: Run tests**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass.

**Step 3: Commit**

```bash
git add equipment/tests/factories.py
git commit -m "feat: add equipment/tests/factories.py"
```

---

## Task 4: Create magic/tests/factories.py

**Files:**
- Create: `magic/tests/factories.py`

**Step 1: Create the file**

All factories with a FK to `Character` or `Class` use lazy string SubFactory to avoid circular imports.

```python
import factory

from magic.constants.spells import (
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
from magic.models.spell_effects import (
    ActiveSpellEffect,
    SpellEffectTemplate,
    SummonedCreature,
)
from magic.models.spells import (
    CharacterSpellSlot,
    ClassSpellcasting,
    Concentration,
    Spell,
    SpellPreparation,
    SpellSettings,
    SpellSlotTable,
    WarlockSpellSlot,
)

from character.constants.classes import ClassName


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

    # Lazy string avoids circular import with character.tests.factories
    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    settings = factory.SubFactory(SpellSettingsFactory)
    source = "class"


class SpellPreparationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpellPreparation

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
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

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    slot_level = 1
    total = 2
    used = 0


class WarlockSpellSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WarlockSpellSlot

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    slot_level = 1
    total = 1
    used = 0


class ClassSpellcastingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClassSpellcasting
        django_get_or_create = ("klass",)

    # Lazy string avoids circular import with character.tests.factories
    klass = factory.SubFactory("character.tests.factories.ClassFactory")
    caster_type = CasterType.PREPARED
    spellcasting_ability = SpellcastingAbility.INTELLIGENCE
    learns_cantrips = True
    spell_list_access = True
    ritual_casting = True
    spellcasting_focus = "arcane focus"


class ConcentrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Concentration

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
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

    character = factory.SubFactory("character.tests.factories.CharacterFactory")
    template = factory.SubFactory(SpellEffectTemplateFactory)
    caster = factory.SubFactory("character.tests.factories.CharacterFactory")
    rounds_remaining = 10
    is_concentration = False


class SummonedCreatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SummonedCreature

    summoner = factory.SubFactory("character.tests.factories.CharacterFactory")
    spell = factory.SubFactory(SpellSettingsFactory)
    name = factory.Faker("first_name")
    hp_current = 20
    hp_max = 20
    ac = 13
    rounds_remaining = 10
    is_concentration = True
```

**Step 2: Run tests**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass.

**Step 3: Commit**

```bash
git add magic/tests/factories.py
git commit -m "feat: add magic/tests/factories.py"
```

---

## Task 5: Refactor character/tests/factories.py to re-export

**Files:**
- Modify: `character/tests/factories.py`

**Step 1: Replace the entire file**

The new file imports from the three new factory modules and re-exports everything for backward compatibility. The character-specific factories are defined here. Note: `CharacterFactory` now imports `InventoryFactory` from `equipment.tests.factories`.

```python
import factory

# Re-exports for backward compatibility
from bestiary.tests.factories import (  # noqa: F401
    LairActionTemplateFactory,
    LegendaryActionTemplateFactory,
    MonsterActionTemplateFactory,
    MonsterConditionImmunityFactory,
    MonsterDamageRelationFactory,
    MonsterFactory,
    MonsterLanguageFactory,
    MonsterMultiattackFactory,
    MonsterReactionFactory,
    MonsterSavingThrowFactory,
    MonsterSenseFactory,
    MonsterSettingsFactory,
    MonsterSkillFactory,
    MonsterSpeedFactory,
    MonsterTraitFactory,
    MultiattackActionFactory,
)
from equipment.tests.factories import (  # noqa: F401
    ArmorFactory,
    ArmorSettingsFactory,
    AttunementFactory,
    GearFactory,
    GearSettingsFactory,
    InventoryFactory,
    MagicItemFactory,
    MagicItemSettingsFactory,
    PackFactory,
    PackSettingsFactory,
    ToolFactory,
    ToolSettingsFactory,
    WeaponFactory,
    WeponSettingsFactory,
)
from magic.tests.factories import (  # noqa: F401
    ActiveSpellEffectFactory,
    CharacterSpellSlotFactory,
    ClassSpellcastingFactory,
    ConcentrationFactory,
    SpellEffectTemplateFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
    SpellSlotTableFactory,
    SummonedCreatureFactory,
    WarlockSpellSlotFactory,
)

# Character-specific imports
from character.constants.abilities import AbilityName
from character.constants.backgrounds import Background
from character.constants.classes import ClassName
from character.constants.conditions import ConditionName
from character.constants.feats import FeatName, FeatType
from character.constants.species import SpeciesName, SpeciesTraitName
from character.models.abilities import Ability, AbilityType
from character.models.character import Character
from character.models.classes import (
    CharacterClass,
    CharacterFeature,
    Class,
    ClassFeature,
)
from character.models.conditions import CharacterCondition, Condition
from character.models.feats import CharacterFeat, Feat
from character.models.species import Species, SpeciesTrait


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
```

**Step 2: Run full test suite — this is the critical check**

```bash
doppler run -- uv run poe test
```

Expected: all tests pass. If any fail with import errors, check which factory is missing from a re-export.

**Step 3: Commit**

```bash
git add character/tests/factories.py
git commit -m "refactor: split character/tests/factories.py into per-app factory modules"
```

---

## Task 6: Move bestiary test file

**Files:**
- Create: `bestiary/tests/models/test_monsters.py` (moved content)
- Delete: `character/tests/models/test_monsters.py`

**Step 1: Copy the file**

```bash
cp character/tests/models/test_monsters.py bestiary/tests/models/test_monsters.py
```

**Step 2: Update imports in the new file**

The original imports `from ..factories import (...)`. Change this to import from `bestiary.tests.factories`.

In `bestiary/tests/models/test_monsters.py`, the file uses only fixtures (no factory imports). Verify by checking the import block — it only imports from `bestiary.constants.monsters` and `bestiary.models.monsters`. No factory imports to update.

**Step 3: Run tests to confirm the new file is discovered and passes**

```bash
doppler run -- uv run pytest bestiary/tests/ -v
```

Expected: all monster tests pass.

**Step 4: Delete the original**

```bash
git rm character/tests/models/test_monsters.py
```

**Step 5: Run full suite to confirm nothing broken**

```bash
doppler run -- uv run poe test
```

**Step 6: Commit**

```bash
git add bestiary/tests/models/test_monsters.py
git commit -m "refactor: move test_monsters.py to bestiary/tests/models/"
```

---

## Task 7: Move equipment model tests

**Files:**
- Create: `equipment/tests/models/test_equipment.py`
- Create: `equipment/tests/models/test_magic_items.py`
- Delete: `character/tests/models/test_equipment.py`
- Delete: `character/tests/models/test_magic_items.py`

### test_equipment.py

**Step 1: Copy the file**

```bash
cp character/tests/models/test_equipment.py equipment/tests/models/test_equipment.py
```

**Step 2: Update factory imports**

The original has `from ..factories import (ArmorFactory, ArmorSettingsFactory, CharacterFactory, GearFactory, InventoryFactory, PackFactory, ToolFactory, WeponSettingsFactory, WeaponFactory, ...)`.

Replace that import block with:

```python
from equipment.tests.factories import (
    ArmorFactory,
    ArmorSettingsFactory,
    GearFactory,
    InventoryFactory,
    PackFactory,
    ToolFactory,
    WeaponFactory,
    WeponSettingsFactory,
)
from character.tests.factories import CharacterFactory
```

**Step 3: Run tests to confirm**

```bash
doppler run -- uv run pytest equipment/tests/models/test_equipment.py -v
```

Expected: all pass.

### test_magic_items.py

**Step 4: Copy the file**

```bash
cp character/tests/models/test_magic_items.py equipment/tests/models/test_magic_items.py
```

**Step 5: Update factory imports**

Original: `from ..factories import (CharacterFactory, MagicItemFactory,)`

Replace with:

```python
from equipment.tests.factories import MagicItemFactory
from character.tests.factories import CharacterFactory
```

**Step 6: Run tests**

```bash
doppler run -- uv run pytest equipment/tests/models/test_magic_items.py -v
```

Expected: all pass.

**Step 7: Delete originals and run full suite**

```bash
git rm character/tests/models/test_equipment.py character/tests/models/test_magic_items.py
doppler run -- uv run poe test
```

**Step 8: Commit**

```bash
git add equipment/tests/models/
git commit -m "refactor: move equipment model tests to equipment/tests/models/"
```

---

## Task 8: Move equipment utils tests

**Files:**
- Create: `equipment/tests/utils/test_equipment_parsers.py`
- Delete: `character/tests/utils/test_equipment_parsers.py`

**Step 1: Copy the file**

```bash
cp character/tests/utils/test_equipment_parsers.py equipment/tests/utils/test_equipment_parsers.py
```

**Step 2: Check imports**

This file has no factory imports — only imports from `equipment.utils.equipment_parsers`. No changes needed.

**Step 3: Run tests**

```bash
doppler run -- uv run pytest equipment/tests/utils/ -v
```

Expected: all pass.

**Step 4: Delete original**

```bash
git rm character/tests/utils/test_equipment_parsers.py
```

**Step 5: Run full suite**

```bash
doppler run -- uv run poe test
```

**Step 6: Commit**

```bash
git add equipment/tests/utils/test_equipment_parsers.py
git commit -m "refactor: move test_equipment_parsers.py to equipment/tests/utils/"
```

---

## Task 9: Move magic model tests

**Files:**
- Create: `magic/tests/models/test_spells.py`
- Create: `magic/tests/models/test_spell_effects.py`
- Delete: `character/tests/models/test_spells.py`
- Delete: `character/tests/models/test_spell_effects.py`

### test_spells.py

**Step 1: Copy the file**

```bash
cp character/tests/models/test_spells.py magic/tests/models/test_spells.py
```

**Step 2: Update factory imports**

Original: `from ..factories import (CharacterFactory, CharacterSpellSlotFactory, ClassFactory, ClassSpellcastingFactory, ConcentrationFactory, SpellFactory, SpellPreparationFactory, SpellSettingsFactory, SpellSlotTableFactory, WarlockSpellSlotFactory,)`

Replace with:

```python
from magic.tests.factories import (
    CharacterSpellSlotFactory,
    ClassSpellcastingFactory,
    ConcentrationFactory,
    SpellFactory,
    SpellPreparationFactory,
    SpellSettingsFactory,
    SpellSlotTableFactory,
    WarlockSpellSlotFactory,
)
from character.tests.factories import CharacterFactory, ClassFactory
```

**Step 3: Run tests**

```bash
doppler run -- uv run pytest magic/tests/models/test_spells.py -v
```

Expected: all pass.

### test_spell_effects.py

**Step 4: Copy the file**

```bash
cp character/tests/models/test_spell_effects.py magic/tests/models/test_spell_effects.py
```

**Step 5: Update factory imports**

Original: `from ..factories import (ActiveSpellEffectFactory, CharacterFactory, ConditionFactory, SpellEffectTemplateFactory, SpellSettingsFactory, SummonedCreatureFactory,)`

Replace with:

```python
from magic.tests.factories import (
    ActiveSpellEffectFactory,
    SpellEffectTemplateFactory,
    SpellSettingsFactory,
    SummonedCreatureFactory,
)
from character.tests.factories import CharacterFactory, ConditionFactory
```

**Step 6: Run tests**

```bash
doppler run -- uv run pytest magic/tests/models/test_spell_effects.py -v
```

Expected: all pass.

**Step 7: Delete originals and run full suite**

```bash
git rm character/tests/models/test_spells.py character/tests/models/test_spell_effects.py
doppler run -- uv run poe test
```

**Step 8: Commit**

```bash
git add magic/tests/models/
git commit -m "refactor: move magic model tests to magic/tests/models/"
```

---

## Task 10: Final verification and PR

**Step 1: Run full test suite with coverage**

```bash
doppler run -- uv run poe test-cov
```

Expected: all tests pass, coverage maintained or improved.

**Step 2: Run pre-commit**

```bash
pre-commit run --all-files
```

Expected: all checks pass.

**Step 3: Update CHANGELOG.md**

Under `## Unreleased`, add:

```markdown
### Changed
- Moved bestiary/equipment/magic tests from `character/tests/` to their respective app test directories
- Split `character/tests/factories.py` into per-app factory modules (`bestiary/tests/factories.py`, `equipment/tests/factories.py`, `magic/tests/factories.py`)
- Added magic fixtures (`spells.yaml`, `spell_effects.yaml`) to test session setup
```

**Step 4: Commit and push**

```bash
git add CHANGELOG.md
git commit -m "docs: update changelog for app split test migration"
git push -u origin refactor/complete-app-split
```

**Step 5: Open PR**

```bash
gh pr create \
  --title "refactor: complete app split - move tests to bestiary/equipment/magic" \
  --body "Completes the app split refactoring by moving tests and factories to their correct homes.

## Changes
- Added magic fixtures to test session setup (were silently never loaded)
- Created per-app factory files for bestiary, equipment, and magic
- character/tests/factories.py becomes a re-export aggregator (backward compatible)
- Moved 6 test files to their correct app directories

## Test plan
- [ ] Full test suite passes: \`doppler run -- uv run poe test\`
- [ ] Coverage maintained: \`doppler run -- uv run poe test-cov\`
- [ ] Pre-commit passes: \`pre-commit run --all-files\`"
```
