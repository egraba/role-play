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
]
