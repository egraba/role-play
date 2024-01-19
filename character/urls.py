from django.urls import path

from character.views.character import (
    CharacterCreateView,
    CharacterDetailView,
    CharacterListView,
)
from character.views.equipment import EquipmentSelectView
from character.views.glossary import GlossaryView
from character.views.skills import SkillsSelectView

urlpatterns = [
    path(
        "<int:pk>",
        CharacterDetailView.as_view(),
        name="character-detail",
    ),
    path(
        "characters",
        CharacterListView.as_view(),
        name="character-list",
    ),
    path(
        "create_character",
        CharacterCreateView.as_view(),
        name="character-create",
    ),
    path(
        "<int:character_id>/select_equipment",
        EquipmentSelectView.as_view(),
        name="equipment-select",
    ),
    path(
        "<int:character_id>/select_skills",
        SkillsSelectView.as_view(),
        name="skills-select",
    ),
    path(
        "glossary",
        GlossaryView.as_view(),
        name="glossary",
    ),
]
