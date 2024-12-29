from django.urls import path

from .views.backgrounds import BackgroundCompleteView
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
        "<int:character_id>/complete_background",
        BackgroundCompleteView.as_view(),
        name="background-complete",
    ),
    path(
        "glossary",
        GlossaryView.as_view(),
        name="glossary",
    ),
]
