from django import forms

import master.models as mmodels


class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = mmodels.Campaign
        exclude = ["slug"]


class CampaignUpdateForm(forms.ModelForm):
    class Meta:
        model = mmodels.Campaign
        exclude = ["title", "slug"]
