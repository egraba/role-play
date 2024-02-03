from django import forms

from .models import Campaign


class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        exclude = ["slug"]


class CampaignUpdateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        exclude = ["title", "slug"]
