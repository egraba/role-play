from django.forms import Form, ValidationError


class NoDuplicateValuesFormMixin(Form):
    """
    Mixin to forbid duplicate values in a form.
    """

    def clean(self):
        self.cleaned_data = super().clean()
        if len(self.cleaned_data) != len(set(self.cleaned_data.values())):
            raise ValidationError("the entered values must be different")
