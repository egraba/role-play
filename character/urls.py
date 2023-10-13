from django.urls import path

from character.views import CharacterCreateView, CharacterDetailView, CharacterListView

urlpatterns = [
    path(
        "character/<int:pk>",
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
]
