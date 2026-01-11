from django.contrib import admin

from .models.advancement import Advancement
from .models.character import Character
from .models.feats import Feat
from .models.classes import Class, ClassFeature
from .models.species import Species, SpeciesTrait


class CharacterAdmin(admin.ModelAdmin):
    fields = ["name", "user", "species"]
    list_display = ["name", "user", "species", "level", "xp"]


class AdvancementAdmin(admin.ModelAdmin):
    fields = ["xp", "level", "proficiency_bonus"]
    list_display = ["xp", "level", "proficiency_bonus"]


class SpeciesAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "size",
        "speed",
        "darkvision",
        "traits",
        "languages",
        "description",
    ]
    list_display = ["name", "size", "speed", "darkvision"]
    filter_horizontal = ["traits", "languages"]


class SpeciesTraitAdmin(admin.ModelAdmin):
    fields = ["name", "description"]
    list_display = ["name", "description"]


class ClassFeatureInline(admin.TabularInline):
    model = ClassFeature
    extra = 1


class ClassAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "description",
        "hit_die",
        "hp_first_level",
        "hp_higher_levels",
        "primary_ability",
        "saving_throws",
        "armor_proficiencies",
        "weapon_proficiencies",
        "starting_wealth_dice",
    ]
    list_display = ["name", "hit_die", "primary_ability"]
    filter_horizontal = ["saving_throws"]
    inlines = [ClassFeatureInline]


class ClassFeatureAdmin(admin.ModelAdmin):
    fields = ["name", "klass", "level", "description"]
    list_display = ["name", "klass", "level"]
    list_filter = ["klass", "level"]
    ordering = ["klass", "level", "name"]


class FeatAdmin(admin.ModelAdmin):
    fields = ["name", "feat_type", "description", "prerequisite"]
    list_display = ["name", "feat_type", "prerequisite"]
    list_filter = ["feat_type"]


# Character
admin.site.register(Character, CharacterAdmin)

# Advancement
admin.site.register(Advancement, AdvancementAdmin)

# Species
admin.site.register(Species, SpeciesAdmin)
admin.site.register(SpeciesTrait, SpeciesTraitAdmin)

# Classes
admin.site.register(Class, ClassAdmin)
admin.site.register(ClassFeature, ClassFeatureAdmin)

# Feats
admin.site.register(Feat, FeatAdmin)
