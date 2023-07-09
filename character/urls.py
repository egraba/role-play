from django.urls import path

import character.views as cviews

urlpatterns = [
    path(
        "character/<int:pk>",
        cviews.DetailCharacterView.as_view(),
        name="character-detail",
    ),
    path(
        "characters",
        cviews.ListCharacterView.as_view(),
        name="character-list",
    ),
    path(
        "create_character",
        cviews.CreateCharacterView.as_view(),
        name="character-create",
    ),
]
