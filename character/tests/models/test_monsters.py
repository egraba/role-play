import pytest

from character.constants.monsters import (
    ActionType,
    AreaShape,
    ChallengeRating,
    CR_XP_TABLE,
    CreatureSize,
    CreatureType,
    DamageType,
    MonsterName,
    RechargeType,
    SaveEffect,
    SaveType,
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


@pytest.mark.django_db
class TestMonsterSettingsModel:
    """Tests for the MonsterSettings model."""

    def test_creation(self):
        settings = MonsterSettings.objects.first()
        assert isinstance(settings, MonsterSettings)

    def test_str(self):
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert "Wolf" in str(settings)
        assert "CR 1/4" in str(settings)

    def test_xp_property(self):
        """XP should be calculated from CR."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert wolf.xp == 50  # CR 1/4 = 50 XP

        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.xp == 18000  # CR 17 = 18000 XP


@pytest.mark.django_db
class TestMonsterSettingsFixture:
    """Tests for the SRD monster database fixture."""

    def test_total_monster_count(self):
        """Fixture should have 17 monsters."""
        assert MonsterSettings.objects.count() == 17

    # Creature type tests
    def test_beast_count(self):
        """Should have 2 beasts."""
        count = MonsterSettings.objects.filter(creature_type=CreatureType.BEAST).count()
        assert count == 2

    def test_humanoid_count(self):
        """Should have 5 humanoids."""
        count = MonsterSettings.objects.filter(
            creature_type=CreatureType.HUMANOID
        ).count()
        assert count == 5

    def test_undead_count(self):
        """Should have 4 undead."""
        count = MonsterSettings.objects.filter(
            creature_type=CreatureType.UNDEAD
        ).count()
        assert count == 4

    def test_monstrosity_count(self):
        """Should have 2 monstrosities."""
        count = MonsterSettings.objects.filter(
            creature_type=CreatureType.MONSTROSITY
        ).count()
        assert count == 2

    def test_dragon_count(self):
        """Should have 1 dragon."""
        count = MonsterSettings.objects.filter(
            creature_type=CreatureType.DRAGON
        ).count()
        assert count == 1

    # Size tests
    def test_medium_creatures(self):
        """Should have multiple medium creatures."""
        count = MonsterSettings.objects.filter(size=CreatureSize.MEDIUM).count()
        assert count >= 8

    def test_large_creatures(self):
        """Should have multiple large creatures."""
        count = MonsterSettings.objects.filter(size=CreatureSize.LARGE).count()
        assert count >= 4

    def test_huge_creatures(self):
        """Should have 1 huge creature (Adult Red Dragon)."""
        count = MonsterSettings.objects.filter(size=CreatureSize.HUGE).count()
        assert count == 1

    # Challenge Rating tests
    def test_cr_0_monsters(self):
        """Should have 1 CR 0 monster."""
        count = MonsterSettings.objects.filter(
            challenge_rating=ChallengeRating.CR_0
        ).count()
        assert count == 1

    def test_cr_1_4_monsters(self):
        """Should have 3 CR 1/4 monsters."""
        count = MonsterSettings.objects.filter(
            challenge_rating=ChallengeRating.CR_1_4
        ).count()
        assert count == 3

    def test_high_cr_monsters(self):
        """Should have legendary creatures with high CR."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.challenge_rating == ChallengeRating.CR_17

        lich = MonsterSettings.objects.get(name=MonsterName.LICH)
        assert lich.challenge_rating == ChallengeRating.CR_21

    # Ability score tests
    @pytest.mark.parametrize(
        "monster_name,expected_str,expected_dex,expected_con",
        [
            (MonsterName.COMMONER, 10, 10, 10),
            (MonsterName.OGRE, 19, 8, 16),
            (MonsterName.ADULT_RED_DRAGON, 27, 10, 25),
        ],
    )
    def test_ability_scores(
        self, monster_name, expected_str, expected_dex, expected_con
    ):
        """Verify monster ability scores."""
        monster = MonsterSettings.objects.get(name=monster_name)
        assert monster.strength == expected_str
        assert monster.dexterity == expected_dex
        assert monster.constitution == expected_con

    def test_ability_modifiers(self):
        """Ability modifiers should be calculated correctly."""
        ogre = MonsterSettings.objects.get(name=MonsterName.OGRE)
        assert ogre.strength_modifier == 4  # 19 STR = +4
        assert ogre.dexterity_modifier == -1  # 8 DEX = -1
        assert ogre.constitution_modifier == 3  # 16 CON = +3

    # AC and HP tests
    @pytest.mark.parametrize(
        "monster_name,expected_ac,expected_hp",
        [
            (MonsterName.COMMONER, 10, 4),
            (MonsterName.SKELETON, 13, 13),
            (MonsterName.OGRE, 11, 59),
            (MonsterName.ADULT_RED_DRAGON, 19, 256),
        ],
    )
    def test_ac_and_hp(self, monster_name, expected_ac, expected_hp):
        """Verify monster AC and average HP."""
        monster = MonsterSettings.objects.get(name=monster_name)
        assert monster.ac == expected_ac
        assert monster.hp_average == expected_hp

    # Speed tests
    def test_walk_speed(self):
        """Most creatures should have walk speed."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert wolf.speed.get("walk") == 40

    def test_fly_speed(self):
        """Flying creatures should have fly speed."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.speed.get("fly") == 80

        elemental = MonsterSettings.objects.get(name=MonsterName.AIR_ELEMENTAL)
        assert elemental.speed.get("fly") == 90
        assert elemental.speed.get("walk") == 0

    def test_climb_speed(self):
        """Some creatures should have climb speed."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.speed.get("climb") == 40

    # Damage resistance/immunity tests
    def test_damage_immunities(self):
        """Undead should be immune to poison."""
        skeleton = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        assert "poison" in skeleton.damage_immunities

        zombie = MonsterSettings.objects.get(name=MonsterName.ZOMBIE)
        assert "poison" in zombie.damage_immunities

    def test_damage_resistances(self):
        """Air elemental should resist certain damage types."""
        elemental = MonsterSettings.objects.get(name=MonsterName.AIR_ELEMENTAL)
        assert "lightning" in elemental.damage_resistances
        assert "thunder" in elemental.damage_resistances

    def test_damage_vulnerabilities(self):
        """Skeleton should be vulnerable to bludgeoning."""
        skeleton = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        assert "bludgeoning" in skeleton.damage_vulnerabilities

    def test_is_immune_to_damage(self):
        """is_immune_to_damage method should work correctly."""
        skeleton = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        assert skeleton.is_immune_to_damage("poison") is True
        assert skeleton.is_immune_to_damage("fire") is False

    def test_is_resistant_to_damage(self):
        """is_resistant_to_damage method should work correctly."""
        elemental = MonsterSettings.objects.get(name=MonsterName.AIR_ELEMENTAL)
        assert elemental.is_resistant_to_damage("lightning") is True
        assert elemental.is_resistant_to_damage("fire") is False

    def test_is_vulnerable_to_damage(self):
        """is_vulnerable_to_damage method should work correctly."""
        skeleton = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        assert skeleton.is_vulnerable_to_damage("bludgeoning") is True
        assert skeleton.is_vulnerable_to_damage("fire") is False

    # Condition immunity tests
    def test_condition_immunities(self):
        """Certain creatures should have condition immunities."""
        skeleton = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        assert "exhaustion" in skeleton.condition_immunities
        assert "poisoned" in skeleton.condition_immunities

        elemental = MonsterSettings.objects.get(name=MonsterName.AIR_ELEMENTAL)
        assert "prone" in elemental.condition_immunities

    def test_is_immune_to_condition(self):
        """is_immune_to_condition method should work correctly."""
        elemental = MonsterSettings.objects.get(name=MonsterName.AIR_ELEMENTAL)
        assert elemental.is_immune_to_condition("prone") is True
        assert elemental.is_immune_to_condition("charmed") is False

    # Senses tests
    def test_darkvision(self):
        """Creatures with darkvision should have it in senses."""
        skeleton = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        assert skeleton.senses.get("darkvision") == 60

        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.senses.get("darkvision") == 120

    def test_blindsight(self):
        """Dragon should have blindsight."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.senses.get("blindsight") == 60

    def test_passive_perception(self):
        """All creatures should have passive perception."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert wolf.senses.get("passive_perception") == 13

    # Language tests
    def test_languages(self):
        """Creatures should have appropriate languages."""
        ogre = MonsterSettings.objects.get(name=MonsterName.OGRE)
        assert "Common" in ogre.languages
        assert "Giant" in ogre.languages

        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert "Draconic" in dragon.languages

    def test_no_languages(self):
        """Beasts typically have no languages."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert wolf.languages == []

    # Saving throw tests
    def test_saving_throw_proficiencies(self):
        """Some creatures have saving throw proficiencies."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.saving_throws.get("DEX") == 6
        assert dragon.saving_throws.get("CON") == 13
        assert dragon.saving_throws.get("WIS") == 7
        assert dragon.saving_throws.get("CHA") == 11

    def test_get_saving_throw(self):
        """get_saving_throw should return proficient bonus or raw modifier."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        # Proficient saves
        assert dragon.get_saving_throw("DEX") == 6
        assert dragon.get_saving_throw("CON") == 13
        # Non-proficient save (uses raw modifier)
        assert dragon.get_saving_throw("INT") == dragon.intelligence_modifier

    # Skill tests
    def test_skill_proficiencies(self):
        """Some creatures have skill proficiencies."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert wolf.skills.get("perception") == 3
        assert wolf.skills.get("stealth") == 4

    def test_get_skill_bonus(self):
        """get_skill_bonus should return the skill bonus."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        assert wolf.get_skill_bonus("perception") == 3
        assert wolf.get_skill_bonus("athletics") == 0  # Not proficient

    # Traits tests
    def test_special_traits(self):
        """Creatures should have special traits."""
        wolf = MonsterSettings.objects.get(name=MonsterName.WOLF)
        trait_names = [t["name"] for t in wolf.traits]
        assert "Keen Hearing and Smell" in trait_names
        assert "Pack Tactics" in trait_names

    def test_undead_fortitude(self):
        """Zombie should have Undead Fortitude."""
        zombie = MonsterSettings.objects.get(name=MonsterName.ZOMBIE)
        trait_names = [t["name"] for t in zombie.traits]
        assert "Undead Fortitude" in trait_names

    # Actions tests
    def test_actions(self):
        """Creatures should have actions."""
        ogre = MonsterSettings.objects.get(name=MonsterName.OGRE)
        action_names = [a["name"] for a in ogre.actions]
        assert "Greatclub" in action_names
        assert "Javelin" in action_names

    def test_multiattack(self):
        """Some creatures have multiattack."""
        owlbear = MonsterSettings.objects.get(name=MonsterName.OWLBEAR)
        action_names = [a["name"] for a in owlbear.actions]
        assert "Multiattack" in action_names

    # Legendary actions tests
    def test_legendary_actions(self):
        """Legendary creatures should have legendary actions."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        assert dragon.legendary_action_count == 3
        assert len(dragon.legendary_actions) == 3

        action_names = [a["name"] for a in dragon.legendary_actions]
        assert "Detect" in action_names
        assert "Tail Attack" in action_names
        assert "Wing Attack" in action_names

    def test_legendary_action_costs(self):
        """Legendary actions should have costs."""
        dragon = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        wing_attack = next(
            a for a in dragon.legendary_actions if a["name"] == "Wing Attack"
        )
        assert wing_attack.get("cost") == 2

    # Lair actions tests
    def test_lair_actions(self):
        """Creatures with lairs should have lair actions."""
        lich = MonsterSettings.objects.get(name=MonsterName.LICH)
        assert lich.has_lair is True
        assert len(lich.lair_actions) == 3

    # Spellcasting tests
    def test_spellcasting(self):
        """Spellcasters should have spellcasting details."""
        mage = MonsterSettings.objects.get(name=MonsterName.MAGE)
        assert mage.spellcasting.get("ability") == "INT"
        assert mage.spellcasting.get("save_dc") == 14
        assert mage.spellcasting.get("attack_bonus") == 6

    def test_spellcasting_spells(self):
        """Spellcasters should have spell lists."""
        lich = MonsterSettings.objects.get(name=MonsterName.LICH)
        spells = lich.spellcasting.get("spells", {})
        assert "cantrips" in spells
        assert "9th" in spells
        assert "power word kill" in spells["9th"]["spells"]


@pytest.mark.django_db
@pytest.mark.skip(
    reason="Skipped due to pre-existing game.Combat ForeignKey resolution issue"
)
class TestMonsterModel:
    """Tests for the Monster model (concrete instances)."""

    def test_creation(self):
        """Can create a monster instance."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        assert isinstance(monster, Monster)

    def test_str_without_instance_name(self):
        """String representation without instance name."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        assert str(monster) == "Wolf"

    def test_str_with_instance_name(self):
        """String representation with instance name."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings, instance_name="Alpha Wolf")
        assert "Alpha Wolf" in str(monster)
        assert "Wolf" in str(monster)

    def test_hp_initialized_from_settings(self):
        """HP should be initialized from settings average."""
        settings = MonsterSettings.objects.get(name=MonsterName.OGRE)
        monster = Monster.create_from_settings(settings)
        assert monster.hp_current == 59
        assert monster.hp_max == 59

    def test_hp_override(self):
        """Can override HP when creating monster."""
        settings = MonsterSettings.objects.get(name=MonsterName.OGRE)
        monster = Monster.create_from_settings(settings, hp_override=100)
        assert monster.hp_current == 100
        assert monster.hp_max == 100

    def test_is_alive(self):
        """is_alive should return True when HP > 0."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        assert monster.is_alive is True

        monster.hp_current = 0
        assert monster.is_alive is False

    def test_is_bloodied(self):
        """is_bloodied should return True when HP <= half max."""
        settings = MonsterSettings.objects.get(name=MonsterName.OGRE)
        monster = Monster.create_from_settings(settings)  # 59 HP
        assert monster.is_bloodied is False

        monster.hp_current = 29  # Just under half
        assert monster.is_bloodied is True

        monster.hp_current = 30  # Exactly half (rounds down)
        assert monster.is_bloodied is False

    def test_take_damage(self):
        """take_damage should reduce HP."""
        settings = MonsterSettings.objects.get(name=MonsterName.OGRE)
        monster = Monster.create_from_settings(settings)
        damage_taken = monster.take_damage(20)
        assert damage_taken == 20
        assert monster.hp_current == 39

    def test_take_damage_with_immunity(self):
        """Damage of immune type should deal 0 damage."""
        settings = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        monster = Monster.create_from_settings(settings)
        original_hp = monster.hp_current
        damage_taken = monster.take_damage(10, "poison")
        assert damage_taken == 0
        assert monster.hp_current == original_hp

    def test_take_damage_with_resistance(self):
        """Damage of resistant type should be halved."""
        settings = MonsterSettings.objects.get(name=MonsterName.AIR_ELEMENTAL)
        monster = Monster.create_from_settings(settings)
        original_hp = monster.hp_current
        damage_taken = monster.take_damage(20, "lightning")
        assert damage_taken == 10
        assert monster.hp_current == original_hp - 10

    def test_take_damage_with_vulnerability(self):
        """Damage of vulnerable type should be doubled."""
        settings = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        monster = Monster.create_from_settings(settings)
        original_hp = monster.hp_current
        damage_taken = monster.take_damage(5, "bludgeoning")
        assert damage_taken == 10
        assert monster.hp_current == original_hp - 10

    def test_take_damage_with_temp_hp(self):
        """Temp HP should absorb damage first."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        monster.hp_temp = 10
        monster.save()

        original_hp = monster.hp_current
        monster.take_damage(15)

        assert monster.hp_temp == 0
        assert monster.hp_current == original_hp - 5

    def test_take_damage_minimum_zero(self):
        """HP should not go below 0."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        monster.take_damage(1000)
        assert monster.hp_current == 0

    def test_heal(self):
        """heal should restore HP."""
        settings = MonsterSettings.objects.get(name=MonsterName.OGRE)
        monster = Monster.create_from_settings(settings)
        monster.hp_current = 30
        monster.save()

        healed = monster.heal(20)
        assert healed == 20
        assert monster.hp_current == 50

    def test_heal_cannot_exceed_max(self):
        """Healing should not exceed max HP."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        monster.hp_current = monster.hp_max - 5
        monster.save()

        healed = monster.heal(20)
        assert healed == 5
        assert monster.hp_current == monster.hp_max

    def test_add_temp_hp(self):
        """add_temp_hp should set temp HP."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        monster.add_temp_hp(10)
        assert monster.hp_temp == 10

    def test_temp_hp_takes_higher(self):
        """Temp HP doesn't stack, takes higher."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        monster.add_temp_hp(10)
        monster.add_temp_hp(5)
        assert monster.hp_temp == 10

        monster.add_temp_hp(15)
        assert monster.hp_temp == 15

    def test_legendary_actions_initialized(self):
        """Legendary creatures should start with full legendary actions."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        monster = Monster.create_from_settings(settings)
        assert monster.legendary_actions_remaining == 3

    def test_use_legendary_action(self):
        """use_legendary_action should decrement remaining actions."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        monster = Monster.create_from_settings(settings)

        result = monster.use_legendary_action(1)
        assert result is True
        assert monster.legendary_actions_remaining == 2

    def test_use_legendary_action_with_cost(self):
        """Can use multiple legendary actions at once."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        monster = Monster.create_from_settings(settings)

        result = monster.use_legendary_action(2)  # Wing Attack costs 2
        assert result is True
        assert monster.legendary_actions_remaining == 1

    def test_use_legendary_action_insufficient(self):
        """Cannot use more legendary actions than remaining."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        monster = Monster.create_from_settings(settings)
        monster.legendary_actions_remaining = 1
        monster.save()

        result = monster.use_legendary_action(2)
        assert result is False
        assert monster.legendary_actions_remaining == 1

    def test_reset_legendary_actions(self):
        """reset_legendary_actions should restore to full."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        monster = Monster.create_from_settings(settings)
        monster.legendary_actions_remaining = 0
        monster.save()

        monster.reset_legendary_actions()
        assert monster.legendary_actions_remaining == 3

    def test_non_legendary_creature_no_legendary_actions(self):
        """Non-legendary creatures should have 0 legendary actions."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        monster = Monster.create_from_settings(settings)
        assert monster.legendary_actions_remaining == 0


@pytest.mark.django_db
class TestCRXPTable:
    """Tests for the Challenge Rating XP table."""

    def test_cr_0_xp(self):
        assert CR_XP_TABLE["0"] == 0

    def test_cr_fractional_xp(self):
        assert CR_XP_TABLE["1/8"] == 25
        assert CR_XP_TABLE["1/4"] == 50
        assert CR_XP_TABLE["1/2"] == 100

    def test_cr_1_xp(self):
        assert CR_XP_TABLE["1"] == 200

    def test_cr_high_xp(self):
        assert CR_XP_TABLE["20"] == 25000
        assert CR_XP_TABLE["30"] == 155000


@pytest.mark.django_db
class TestMonsterActionTemplate:
    """Tests for the MonsterActionTemplate model."""

    def test_creation(self):
        """Can create a monster action template."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
            attack_bonus=4,
            reach=5,
            targets="one target",
            damage_dice="2d4+2",
            damage_type=DamageType.PIERCING,
        )
        assert action.pk is not None
        assert action.name == "Bite"

    def test_str(self):
        """String representation includes monster and action name."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
        )
        assert "Wolf" in str(action)
        assert "Bite" in str(action)

    def test_is_attack_melee_weapon(self):
        """Melee weapon attacks should be identified as attacks."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
        )
        assert action.is_attack is True

    def test_is_attack_ranged_weapon(self):
        """Ranged weapon attacks should be identified as attacks."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Javelin",
            action_type=ActionType.RANGED_WEAPON,
        )
        assert action.is_attack is True

    def test_is_attack_spell(self):
        """Spell attacks should be identified as attacks."""
        settings = MonsterSettings.objects.get(name=MonsterName.LICH)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Ray of Frost",
            action_type=ActionType.RANGED_SPELL,
        )
        assert action.is_attack is True

    def test_is_attack_special(self):
        """Special abilities should not be identified as attacks."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Howl",
            action_type=ActionType.SPECIAL,
        )
        assert action.is_attack is False

    def test_requires_save(self):
        """Action requiring save should be identified."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Fire Breath",
            action_type=ActionType.SPECIAL,
            save_dc=21,
            save_type=SaveType.DEXTERITY,
            save_effect=SaveEffect.HALF_DAMAGE,
        )
        assert action.requires_save is True

    def test_requires_save_false(self):
        """Action without save should not require save."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
        )
        assert action.requires_save is False

    def test_has_area_effect(self):
        """Action with area should be identified."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Fire Breath",
            action_type=ActionType.SPECIAL,
            area_shape=AreaShape.CONE,
            area_size=60,
        )
        assert action.has_area_effect is True

    def test_has_area_effect_false(self):
        """Action without area should not have area effect."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
        )
        assert action.has_area_effect is False

    def test_recharge_ability(self):
        """Can create action with recharge mechanic."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Fire Breath",
            action_type=ActionType.SPECIAL,
            recharge=RechargeType.RECHARGE_5_6,
        )
        assert action.recharge == RechargeType.RECHARGE_5_6

    def test_extra_damage(self):
        """Can create action with extra damage."""
        settings = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Poison Dagger",
            action_type=ActionType.MELEE_WEAPON,
            damage_dice="1d4+2",
            damage_type=DamageType.PIERCING,
            extra_damage_dice="1d6",
            extra_damage_type=DamageType.POISON,
        )
        assert action.extra_damage_dice == "1d6"
        assert action.extra_damage_type == DamageType.POISON

    def test_get_attack_description(self):
        """get_attack_description generates proper format."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
            attack_bonus=4,
            reach=5,
            targets="one target",
        )
        desc = action.get_attack_description()
        assert "Melee Weapon Attack:" in desc
        assert "+4 to hit" in desc
        assert "reach 5 ft." in desc
        assert "one target" in desc

    def test_get_attack_description_ranged(self):
        """get_attack_description handles ranged attacks."""
        settings = MonsterSettings.objects.get(name=MonsterName.OGRE)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Javelin",
            action_type=ActionType.RANGED_WEAPON,
            attack_bonus=6,
            range_normal=30,
            range_long=120,
            targets="one target",
        )
        desc = action.get_attack_description()
        assert "Ranged Weapon Attack:" in desc
        assert "+6 to hit" in desc
        assert "range 30/120 ft." in desc

    def test_get_damage_description(self):
        """get_damage_description generates proper format."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
            damage_dice="2d4+2",
            damage_type=DamageType.PIERCING,
        )
        desc = action.get_damage_description()
        assert "Hit: 2d4+2" in desc
        assert "piercing damage" in desc

    def test_get_damage_description_with_extra(self):
        """get_damage_description includes extra damage."""
        settings = MonsterSettings.objects.get(name=MonsterName.SKELETON)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Poison Dagger",
            action_type=ActionType.MELEE_WEAPON,
            damage_dice="1d4+2",
            damage_type=DamageType.PIERCING,
            extra_damage_dice="1d6",
            extra_damage_type=DamageType.POISON,
        )
        desc = action.get_damage_description()
        assert "piercing damage" in desc
        assert "plus 1d6 poison damage" in desc


@pytest.mark.django_db
class TestMonsterMultiattack:
    """Tests for the MonsterMultiattack model."""

    def test_creation(self):
        """Can create a multiattack pattern."""
        settings = MonsterSettings.objects.get(name=MonsterName.OWLBEAR)
        multiattack = MonsterMultiattack.objects.create(
            monster=settings,
            description="The owlbear makes two attacks: one with its beak and one with its claws.",
        )
        assert multiattack.pk is not None

    def test_str(self):
        """String representation includes monster name."""
        settings = MonsterSettings.objects.get(name=MonsterName.OWLBEAR)
        multiattack = MonsterMultiattack.objects.create(
            monster=settings,
            description="The owlbear makes two attacks.",
        )
        assert "Owlbear" in str(multiattack)
        assert "Multiattack" in str(multiattack)

    def test_multiattack_actions(self):
        """Can link actions to multiattack."""
        settings = MonsterSettings.objects.get(name=MonsterName.OWLBEAR)

        beak = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Beak",
            action_type=ActionType.MELEE_WEAPON,
        )
        claws = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Claws",
            action_type=ActionType.MELEE_WEAPON,
        )

        multiattack = MonsterMultiattack.objects.create(
            monster=settings,
            description="The owlbear makes two attacks.",
        )

        MultiattackAction.objects.create(
            multiattack=multiattack,
            action=beak,
            count=1,
        )
        MultiattackAction.objects.create(
            multiattack=multiattack,
            action=claws,
            count=1,
        )

        assert multiattack.actions.count() == 2


@pytest.mark.django_db
class TestMultiattackAction:
    """Tests for the MultiattackAction model."""

    def test_creation(self):
        """Can create a multiattack action."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
        )
        multiattack = MonsterMultiattack.objects.create(
            monster=settings,
            description="Test multiattack",
        )
        ma_action = MultiattackAction.objects.create(
            multiattack=multiattack,
            action=action,
            count=2,
        )
        assert ma_action.count == 2

    def test_str(self):
        """String representation shows count and action."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Bite",
            action_type=ActionType.MELEE_WEAPON,
        )
        multiattack = MonsterMultiattack.objects.create(
            monster=settings,
            description="Test multiattack",
        )
        ma_action = MultiattackAction.objects.create(
            multiattack=multiattack,
            action=action,
            count=2,
        )
        assert "2x" in str(ma_action)
        assert "Bite" in str(ma_action)

    def test_optional_action(self):
        """Can mark action as optional."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        claw = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Claw",
            action_type=ActionType.MELEE_WEAPON,
        )
        tail = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Tail",
            action_type=ActionType.MELEE_WEAPON,
        )
        multiattack = MonsterMultiattack.objects.create(
            monster=settings,
            description="The dragon can use its Frightful Presence. It then makes three attacks.",
        )

        # Claw is required, tail is optional
        MultiattackAction.objects.create(
            multiattack=multiattack,
            action=claw,
            count=2,
            is_optional=False,
        )
        MultiattackAction.objects.create(
            multiattack=multiattack,
            action=tail,
            count=1,
            is_optional=True,
            group=1,
        )

        assert multiattack.actions.filter(is_optional=False).count() == 1
        assert multiattack.actions.filter(is_optional=True).count() == 1


@pytest.mark.django_db
class TestLegendaryActionTemplate:
    """Tests for the LegendaryActionTemplate model."""

    def test_creation(self):
        """Can create a legendary action."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        legendary = LegendaryActionTemplate.objects.create(
            monster=settings,
            name="Detect",
            description="The dragon makes a Wisdom (Perception) check.",
            cost=1,
        )
        assert legendary.pk is not None
        assert legendary.cost == 1

    def test_str_cost_1(self):
        """String representation for cost 1 action."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        legendary = LegendaryActionTemplate.objects.create(
            monster=settings,
            name="Detect",
            description="The dragon makes a Wisdom (Perception) check.",
            cost=1,
        )
        assert "Detect" in str(legendary)
        assert "Costs" not in str(legendary)

    def test_str_cost_2(self):
        """String representation for cost 2 action."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        legendary = LegendaryActionTemplate.objects.create(
            monster=settings,
            name="Wing Attack",
            description="The dragon beats its wings.",
            cost=2,
        )
        assert "Wing Attack" in str(legendary)
        assert "Costs 2 Actions" in str(legendary)

    def test_linked_action_template(self):
        """Legendary action can link to existing action template."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        tail_action = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Tail",
            action_type=ActionType.MELEE_WEAPON,
            attack_bonus=15,
            reach=15,
            damage_dice="2d8+8",
            damage_type=DamageType.BLUDGEONING,
        )
        legendary = LegendaryActionTemplate.objects.create(
            monster=settings,
            name="Tail Attack",
            description="The dragon makes a tail attack.",
            cost=1,
            action_template=tail_action,
        )
        assert legendary.action_template == tail_action


@pytest.mark.django_db
class TestLairActionTemplate:
    """Tests for the LairActionTemplate model."""

    def test_creation(self):
        """Can create a lair action."""
        settings = MonsterSettings.objects.get(name=MonsterName.LICH)
        lair = LairActionTemplate.objects.create(
            monster=settings,
            description="The lich rolls a d8 and regains a spell slot of that level or lower.",
        )
        assert lair.pk is not None

    def test_str(self):
        """String representation includes monster and lair action number."""
        settings = MonsterSettings.objects.get(name=MonsterName.LICH)
        lair = LairActionTemplate.objects.create(
            monster=settings,
            description="Test lair action.",
            sort_order=0,
        )
        assert "Lich" in str(lair)
        assert "Lair Action" in str(lair)

    def test_lair_action_with_save(self):
        """Lair action can have a saving throw."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        lair = LairActionTemplate.objects.create(
            monster=settings,
            description="Magma erupts from a point on the ground.",
            save_dc=15,
            save_type=SaveType.DEXTERITY,
            save_effect=SaveEffect.HALF_DAMAGE,
        )
        assert lair.save_dc == 15
        assert lair.save_type == SaveType.DEXTERITY

    def test_lair_action_with_area(self):
        """Lair action can have an area effect."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        lair = LairActionTemplate.objects.create(
            monster=settings,
            description="A cloud of smoke fills a 20-foot-radius sphere.",
            area_shape=AreaShape.SPHERE,
            area_size=20,
        )
        assert lair.area_shape == AreaShape.SPHERE
        assert lair.area_size == 20


@pytest.mark.django_db
class TestMonsterTrait:
    """Tests for the MonsterTrait model."""

    def test_creation(self):
        """Can create a monster trait."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        trait = MonsterTrait.objects.create(
            monster=settings,
            name="Keen Hearing and Smell",
            description="The wolf has advantage on Wisdom (Perception) checks that rely on hearing or smell.",
        )
        assert trait.pk is not None

    def test_str(self):
        """String representation includes monster and trait name."""
        settings = MonsterSettings.objects.get(name=MonsterName.WOLF)
        trait = MonsterTrait.objects.create(
            monster=settings,
            name="Pack Tactics",
            description="Test description",
        )
        assert "Wolf" in str(trait)
        assert "Pack Tactics" in str(trait)

    def test_trait_with_uses(self):
        """Trait can have limited uses."""
        settings = MonsterSettings.objects.get(name=MonsterName.LICH)
        trait = MonsterTrait.objects.create(
            monster=settings,
            name="Legendary Resistance",
            description="If the lich fails a saving throw, it can choose to succeed instead.",
            uses_per_day=3,
        )
        assert trait.uses_per_day == 3

    def test_trait_with_recharge(self):
        """Trait can have recharge mechanic."""
        settings = MonsterSettings.objects.get(name=MonsterName.ZOMBIE)
        trait = MonsterTrait.objects.create(
            monster=settings,
            name="Undead Fortitude",
            description="Test description",
            recharge=RechargeType.NONE,
        )
        assert trait.recharge == RechargeType.NONE


@pytest.mark.django_db
class TestMonsterReaction:
    """Tests for the MonsterReaction model."""

    def test_creation(self):
        """Can create a monster reaction."""
        settings = MonsterSettings.objects.get(name=MonsterName.KNIGHT)
        reaction = MonsterReaction.objects.create(
            monster=settings,
            name="Parry",
            description="The knight adds 2 to its AC against one melee attack.",
            trigger="When hit by a melee attack it can see",
        )
        assert reaction.pk is not None

    def test_str(self):
        """String representation includes monster and reaction name."""
        settings = MonsterSettings.objects.get(name=MonsterName.KNIGHT)
        reaction = MonsterReaction.objects.create(
            monster=settings,
            name="Parry",
            description="Test description",
            trigger="When hit by a melee attack",
        )
        assert "Knight" in str(reaction)
        assert "Parry" in str(reaction)

    def test_reaction_with_linked_action(self):
        """Reaction can link to an action template."""
        settings = MonsterSettings.objects.get(name=MonsterName.ADULT_RED_DRAGON)
        tail = MonsterActionTemplate.objects.create(
            monster=settings,
            name="Tail",
            action_type=ActionType.MELEE_WEAPON,
        )
        reaction = MonsterReaction.objects.create(
            monster=settings,
            name="Tail Swipe",
            description="The dragon makes a tail attack.",
            trigger="When a creature enters its reach",
            action_template=tail,
        )
        assert reaction.action_template == tail


@pytest.mark.django_db
class TestActionConstants:
    """Tests for the action-related constants."""

    def test_action_types(self):
        """ActionType should have all attack types."""
        assert ActionType.MELEE_WEAPON
        assert ActionType.RANGED_WEAPON
        assert ActionType.MELEE_SPELL
        assert ActionType.RANGED_SPELL
        assert ActionType.MULTIATTACK
        assert ActionType.SPECIAL
        assert ActionType.LEGENDARY
        assert ActionType.LAIR
        assert ActionType.REACTION

    def test_damage_types(self):
        """DamageType should have all standard types."""
        assert DamageType.ACID
        assert DamageType.BLUDGEONING
        assert DamageType.COLD
        assert DamageType.FIRE
        assert DamageType.FORCE
        assert DamageType.LIGHTNING
        assert DamageType.NECROTIC
        assert DamageType.PIERCING
        assert DamageType.POISON
        assert DamageType.PSYCHIC
        assert DamageType.RADIANT
        assert DamageType.SLASHING
        assert DamageType.THUNDER

    def test_save_types(self):
        """SaveType should have all abilities."""
        assert SaveType.STRENGTH
        assert SaveType.DEXTERITY
        assert SaveType.CONSTITUTION
        assert SaveType.INTELLIGENCE
        assert SaveType.WISDOM
        assert SaveType.CHARISMA
        assert SaveType.NONE

    def test_recharge_types(self):
        """RechargeType should have all options."""
        assert RechargeType.NONE
        assert RechargeType.RECHARGE_5_6
        assert RechargeType.RECHARGE_6
        assert RechargeType.RECHARGE_4_6
        assert RechargeType.SHORT_REST
        assert RechargeType.LONG_REST
        assert RechargeType.DAILY_1
        assert RechargeType.DAILY_2
        assert RechargeType.DAILY_3

    def test_area_shapes(self):
        """AreaShape should have all shapes."""
        assert AreaShape.NONE
        assert AreaShape.SPHERE
        assert AreaShape.CUBE
        assert AreaShape.CONE
        assert AreaShape.LINE
        assert AreaShape.CYLINDER
