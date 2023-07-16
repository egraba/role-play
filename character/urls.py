from django.urls import path

import character.views as cviews

urlpatterns = [
    path(
        "character/<int:pk>",
        cviews.CharacterDetailView.as_view(),
        name="character-detail",
    ),
    path(
        "characters",
        cviews.CharacterListView.as_view(),
        name="character-list",
    ),
    path(
        "create_character",
        cviews.CharacterCreateView.as_view(),
        name="character-create",
    ),
]
