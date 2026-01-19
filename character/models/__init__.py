# Import all models so Django can discover them
from .abilities import Ability, AbilityType
from .advancement import Advancement
from .character import Character
from .conditions import CharacterCondition, Condition
from .disadvantages import (
    AbilityCheckDisadvantage,
    AttackRollDisadvantage,
    SavingThrowDisadvantage,
    SpellCastDisadvantage,
)
from .equipment import (
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
from .feats import CharacterFeat, Feat
from .classes import (
    CharacterClass,
    Class,
    ClassFeature,
)
from .proficiencies import SavingThrowProficiency, SkillProficiency
from .races import Language
from .skills import Skill
from .species import Species, SpeciesTrait
from .spells import (
    CharacterSpellSlot,
    ClassSpellcasting,
    Concentration,
    Spell,
    SpellPreparation,
    SpellSettings,
    SpellSlotTable,
    WarlockSpellSlot,
)
from .spell_effects import (
    ActiveSpellEffect,
    SpellEffectTemplate,
    SummonedCreature,
)
from .magic_items import (
    Attunement,
    MagicItem,
    MagicItemSettings,
)
from .monsters import (
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

__all__ = [
    "Ability",
    "AbilityType",
    "Advancement",
    "Armor",
    "ArmorSettings",
    "Character",
    "CharacterClass",
    "CharacterCondition",
    "CharacterFeat",
    "Class",
    "ClassFeature",
    "Condition",
    "AbilityCheckDisadvantage",
    "AttackRollDisadvantage",
    "SavingThrowDisadvantage",
    "SpellCastDisadvantage",
    "Feat",
    "Gear",
    "GearSettings",
    "Inventory",
    "Language",
    "Pack",
    "PackSettings",
    "SavingThrowProficiency",
    "Skill",
    "SkillProficiency",
    "Species",
    "SpeciesTrait",
    "Tool",
    "ToolSettings",
    "Weapon",
    "WeaponSettings",
    # Spellcasting
    "CharacterSpellSlot",
    "ClassSpellcasting",
    "Concentration",
    "Spell",
    "SpellPreparation",
    "SpellSettings",
    "SpellSlotTable",
    "WarlockSpellSlot",
    # Spell Effects
    "ActiveSpellEffect",
    "SpellEffectTemplate",
    "SummonedCreature",
    # Magic Items
    "Attunement",
    "MagicItem",
    "MagicItemSettings",
    # Monsters
    "LairActionTemplate",
    "LegendaryActionTemplate",
    "Monster",
    "MonsterActionTemplate",
    "MonsterMultiattack",
    "MonsterReaction",
    "MonsterSettings",
    "MonsterTrait",
    "MultiattackAction",
]
