from django import forms

from .models import Act, Campaign, Encounter, Location, NPC, Scene


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = [
            "title",
            "synopsis",
            "main_conflict",
            "objective",
            "party_level",
            "tone",
            "setting",
        ]


class ActForm(forms.ModelForm):
    class Meta:
        model = Act
        fields = ["title", "order", "summary", "goal"]


class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = ["title", "order", "scene_type", "description", "hook", "resolution"]


class NPCForm(forms.ModelForm):
    class Meta:
        model = NPC
        fields = ["name", "role", "motivation", "personality", "appearance", "notes"]


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name", "description", "region"]


class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        fields = [
            "title",
            "order",
            "encounter_type",
            "description",
            "difficulty",
            "rewards",
        ]
