from django import forms


class SkillsSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = self.initial["choices"]

        self.fields["first_skill"] = forms.ChoiceField(
            choices=choices, widget=forms.Select(attrs={"class": "rpgui-dropdown"})
        )

        self.fields["second_skill"] = forms.ChoiceField(
            choices=choices, widget=forms.Select(attrs={"class": "rpgui-dropdown"})
        )

    def clean(self):
        self.cleaned_data = super().clean()
        if len(self.cleaned_data) != len(set(self.cleaned_data.values())):
            raise forms.ValidationError("The selected skills must be unique...")


class ExtendedSkillsSelectForm(SkillsSelectForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = self.initial["choices"]

        self.fields["third_skill"] = forms.ChoiceField(
            choices=choices, widget=forms.Select(attrs={"class": "rpgui-dropdown"})
        )

        self.fields["fourth_skill"] = forms.ChoiceField(
            choices=choices, widget=forms.Select(attrs={"class": "rpgui-dropdown"})
        )
