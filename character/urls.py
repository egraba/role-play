from django.urls import path

from .views.character import CharacterCreateView, CharacterDetailView
from .views.hp import (
    AddTempHPView,
    DeathSaveView,
    HealView,
    HPBarView,
    RemoveTempHPView,
    ResetDeathSavesView,
    TakeDamageView,
)
from .views.skills import SkillRollView, SkillsPanelView
from .views.spells import (
    BreakConcentrationView,
    CastSpellView,
    RestoreAllSlotsView,
    RestoreSpellSlotView,
    SpellCardModalView,
    SpellsPanelView,
    UseSpellSlotView,
)

urlpatterns = [
    path(
        "<int:pk>",
        CharacterDetailView.as_view(),
        name="character-detail",
    ),
    path(
        "create_character",
        CharacterCreateView.as_view(),
        name="character-create",
    ),
    # HTMX HP Bar endpoints
    path(
        "<int:pk>/hp/",
        HPBarView.as_view(),
        name="character-hp-bar",
    ),
    path(
        "<int:pk>/hp/damage/",
        TakeDamageView.as_view(),
        name="character-take-damage",
    ),
    path(
        "<int:pk>/hp/heal/",
        HealView.as_view(),
        name="character-heal",
    ),
    path(
        "<int:pk>/hp/temp/add/",
        AddTempHPView.as_view(),
        name="character-add-temp-hp",
    ),
    path(
        "<int:pk>/hp/temp/remove/",
        RemoveTempHPView.as_view(),
        name="character-remove-temp-hp",
    ),
    path(
        "<int:pk>/hp/death-save/",
        DeathSaveView.as_view(),
        name="character-death-save",
    ),
    path(
        "<int:pk>/hp/death-save/reset/",
        ResetDeathSavesView.as_view(),
        name="character-reset-death-saves",
    ),
    # HTMX Skills Panel endpoints
    path(
        "<int:pk>/skills/",
        SkillsPanelView.as_view(),
        name="character-skills-panel",
    ),
    path(
        "<int:pk>/skills/roll/",
        SkillRollView.as_view(),
        name="character-skill-roll",
    ),
    # HTMX Spells Panel endpoints
    path(
        "<int:pk>/spells/",
        SpellsPanelView.as_view(),
        name="character-spells-panel",
    ),
    path(
        "<int:pk>/spells/slot/use/",
        UseSpellSlotView.as_view(),
        name="character-use-spell-slot",
    ),
    path(
        "<int:pk>/spells/slot/restore/",
        RestoreSpellSlotView.as_view(),
        name="character-restore-spell-slot",
    ),
    path(
        "<int:pk>/spells/slots/restore-all/",
        RestoreAllSlotsView.as_view(),
        name="character-restore-all-slots",
    ),
    path(
        "<int:pk>/spells/cast/",
        CastSpellView.as_view(),
        name="character-cast-spell",
    ),
    path(
        "<int:pk>/spells/concentration/break/",
        BreakConcentrationView.as_view(),
        name="character-break-concentration",
    ),
    path(
        "<int:pk>/spells/<str:spell_name>/",
        SpellCardModalView.as_view(),
        name="character-spell-card",
    ),
]
