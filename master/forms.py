from django import forms

import master.models as mmodels


class StoryCreateForm(forms.ModelForm):
    class Meta:
        model = mmodels.Story
        exclude = ["slug"]


class StoryUpdateForm(forms.ModelForm):
    class Meta:
        model = mmodels.Story
        exclude = ["title", "slug"]
