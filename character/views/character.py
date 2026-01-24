import re
from enum import StrEnum

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from formtools.wizard.views import SessionWizardView

from ..character_attributes_builders import (
    BackgroundBuilder,
    BaseBuilder,
    ClassBuilder,
    DerivedStatsBuilder,
    SpeciesBuilder,
    SpellcastingBuilder,
)
from ..constants.equipment import ArmorName, GearName, ToolName, WeaponName
from ..constants.classes import ClassName
from ..forms.backgrounds import BackgroundForm
from ..forms.character import CharacterCreateForm
from ..forms.equipment import EquipmentSelectForm
from ..forms.skills import SkillsSelectForm
from ..models.character import Character

MULTI_EQUIPMENT_REGEX = r"\S+\s&\s\S+"


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "character/character_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.object

        # Inventory
        context["inventory"] = character.inventory

        # Abilities with abbreviations for display
        abilities = []
        for ability in character.abilities.all().select_related("ability_type"):
            abilities.append(
                {
                    "name": ability.ability_type.get_name_display(),
                    "abbreviation": ability.ability_type.name,
                    "score": ability.score,
                    "modifier": ability.modifier,
                }
            )
        context["abilities"] = abilities

        # Skills with proficiency status and modifiers
        from ..models.skills import Skill

        all_skills = Skill.objects.all().select_related("ability_type")
        character_skill_names = set(character.skills.values_list("name", flat=True))

        # Build ability modifier lookup
        ability_modifiers = {a["abbreviation"]: a["modifier"] for a in abilities}

        skills = []
        for skill in all_skills:
            is_proficient = skill.name in character_skill_names
            ability_mod = ability_modifiers.get(skill.ability_type.name, 0)
            modifier = ability_mod + (
                character.proficiency_bonus if is_proficient else 0
            )
            skills.append(
                {
                    "name": skill.get_name_display(),
                    "ability": skill.ability_type.name,
                    "proficient": is_proficient,
                    "modifier": modifier,
                }
            )
        context["skills"] = skills

        # Saving throws with proficiency and modifiers
        saving_throw_proficiencies = set(
            character.savingthrowproficiency_set.values_list(
                "ability_type__name", flat=True
            )
        )
        saving_throws = []
        for ability in abilities:
            is_proficient = ability["abbreviation"] in saving_throw_proficiencies
            modifier = ability["modifier"] + (
                character.proficiency_bonus if is_proficient else 0
            )
            saving_throws.append(
                {
                    "name": ability["abbreviation"],
                    "proficient": is_proficient,
                    "modifier": modifier,
                }
            )
        context["saving_throws"] = saving_throws

        # Attacks from equipped weapons
        attacks = []
        if character.inventory:
            str_mod = ability_modifiers.get("STR", 0)
            dex_mod = ability_modifiers.get("DEX", 0)
            for weapon in character.inventory.weapon_set.select_related(
                "settings"
            ).all():
                settings = weapon.settings
                # Check if weapon is ranged or has finesse property
                is_ranged = settings.weapon_type in ("SR", "MR")
                is_finesse = (
                    settings.properties and "finesse" in settings.properties.lower()
                )
                # Use DEX for finesse/ranged weapons, STR otherwise
                # For finesse, use the higher of STR or DEX
                if is_finesse:
                    attack_mod = max(str_mod, dex_mod)
                elif is_ranged:
                    attack_mod = dex_mod
                else:
                    attack_mod = str_mod
                attack_bonus = attack_mod + character.proficiency_bonus
                damage_dice = settings.damage or "1d4"
                damage = f"{damage_dice}+{attack_mod}" if attack_mod else damage_dice
                attacks.append(
                    {
                        "name": str(weapon),
                        "bonus": attack_bonus,
                        "damage": damage,
                    }
                )
        context["attacks"] = attacks

        # Species/Racial traits
        racial_traits = []
        if character.species:
            for trait in character.species.traits.all():
                racial_traits.append(
                    {
                        "name": trait.get_name_display(),
                        "description": trait.description,
                    }
                )
        context["racial_traits"] = racial_traits

        # Class features
        class_features = []
        for char_feature in character.class_features.all().select_related(
            "class_feature"
        ):
            class_features.append(
                {
                    "name": char_feature.class_feature.name,
                    "description": char_feature.class_feature.description,
                    "level": char_feature.level_gained,
                }
            )
        context["class_features"] = class_features

        # Feats
        feats = []
        for char_feat in character.character_feats.all().select_related("feat"):
            feats.append(
                {
                    "name": char_feat.feat.get_name_display(),
                    "description": char_feat.feat.description,
                }
            )
        context["feats"] = feats

        # Spells (placeholder - extend if spellcasting model exists)
        context["spells_by_level"] = {}
        context["spell_slots"] = []

        return context


class CharacterCreateView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        CharacterCreateForm,
        SkillsSelectForm,
        BackgroundForm,
        EquipmentSelectForm,
    ]
    template_name = "character/character_create.html"

    class Step(StrEnum):
        BASE_ATTRIBUTES_SELECTION = "0"
        SKILLS_SELECTION = "1"
        BACKGROUND_COMPLETION = "2"
        EQUIPMENT_SELECTION = "3"

    def get_form_initial(self, step):
        if step == self.Step.SKILLS_SELECTION or step == self.Step.EQUIPMENT_SELECTION:
            data = self.storage.get_step_data(self.Step.BASE_ATTRIBUTES_SELECTION)
            if data:
                klass = data.get("0-klass")
                return self.initial_dict.get(step, {"klass": klass})
        if step == self.Step.BACKGROUND_COMPLETION:
            data = self.storage.get_step_data(self.Step.BASE_ATTRIBUTES_SELECTION)
            if data:
                species = data.get("0-species")
                background = data.get("0-background")
                return self.initial_dict.get(
                    step, {"species": species, "background": background}
                )
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        klass = None
        for form in form_list:
            if isinstance(form, CharacterCreateForm):
                character = form.save(commit=False)
                character.user = self.request.user
                klass = form.cleaned_data["klass"]
                # Phase 1: Base setup - inventory and ability scores
                BaseBuilder(character, form).build()
                # Phase 2: Species traits - size, speed, darkvision, languages
                SpeciesBuilder(character).build()
                # Phase 3: Class - HP, proficiencies, features, wealth
                ClassBuilder(character, klass).build()
            elif isinstance(form, SkillsSelectForm):
                for field in form.cleaned_data.keys():
                    character.skills.add(form.cleaned_data[field])
            elif isinstance(form, BackgroundForm):
                # Phase 4: Background - skill proficiencies, tools, feat, personality
                BackgroundBuilder(character).build()
                # Phase 5: Derived stats (after all modifiers are applied)
                DerivedStatsBuilder(character).build()
                # Phase 6: Spellcasting setup (if class is a spellcaster)
                if klass:
                    SpellcastingBuilder(character, klass).build()
            elif isinstance(form, EquipmentSelectForm):
                inventory = character.inventory
                for field in form.cleaned_data.keys():
                    # KeyError exception is caught because the form is different per class.
                    try:
                        equipment_name = form.cleaned_data[field]
                        # If the field is under the form "equipment_name1 & equipment_name2",
                        # each equipment must be added separately.
                        if re.match(MULTI_EQUIPMENT_REGEX, equipment_name):
                            names = equipment_name.split(" & ")
                            for name in names:
                                inventory.add(name)
                        else:
                            inventory.add(equipment_name)
                    except KeyError:
                        pass
                # Some equipment is added without selection, depending on character's class.
                if klass:
                    match klass.name:
                        case ClassName.CLERIC:
                            inventory.add(WeaponName.CROSSBOW_LIGHT)
                            inventory.add(GearName.CROSSBOW_BOLTS)
                            inventory.add(ArmorName.SHIELD)
                        case ClassName.ROGUE:
                            inventory.add(WeaponName.SHORTBOW)
                            inventory.add(GearName.QUIVER)
                            inventory.add(ArmorName.LEATHER)
                            inventory.add(WeaponName.DAGGER)
                            inventory.add(WeaponName.DAGGER)
                            inventory.add(ToolName.THIEVES_TOOLS)
                        case ClassName.WIZARD:
                            inventory.add(GearName.SPELLBOOK)
            else:
                raise NotImplementedError(f"{form=} is not implemented")
        return HttpResponseRedirect(character.get_absolute_url())
