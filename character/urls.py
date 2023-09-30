from django.urls import path

from character.views.character import (
    CharacterCreateView,
    CharacterDetailView,
    CharacterListView,
)
from character.views.creation import ChoseEquipmentView

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
        "<int:character_id>/chose_equipment",
        ChoseEquipmentView.as_view(),
        name="chose-equipment",
    ),
]
