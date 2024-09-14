from django.urls import path

from .forms.character import CharacterCreateForm
from .views.backgrounds import BackgroundCompleteView
from .views.character import CharacterCreateView, CharacterDetailView, CharacterListView
from .views.equipment import EquipmentSelectView
from .views.glossary import GlossaryView
from .views.skills import SkillsSelectView

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
        CharacterCreateView.as_view([CharacterCreateForm]),
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
