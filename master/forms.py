from django import forms

import master.models as mmodels


class CreateStoryForm(forms.ModelForm):
    class Meta:
        model = mmodels.Story
        exclude = ["slug"]

    def clean_title(self):
        title = self.cleaned_data["title"]
        if mmodels.Story.objects.filter(title=title).exists():
            raise forms.ValidationError(
                "A story with the same title already exists... Please find another title."
            )
        return title
