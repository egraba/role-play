from django import forms

from .models import Campaign


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
