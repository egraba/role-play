from django.urls import path

from .views.character import CharacterCreateView, CharacterDetailView
from .views.glossary import GlossaryView

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
    path(
        "glossary",
        GlossaryView.as_view(),
        name="glossary",
    ),
]
