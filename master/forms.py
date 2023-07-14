from django import forms

import master.models as mmodels


class CreateStoryForm(forms.ModelForm):
    class Meta:
        model = mmodels.Story
        exclude = ["slug"]
