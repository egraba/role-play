from django.forms import Form, ValidationError


class NoDuplicateValuesFormMixin(Form):
    """
    Mixin to forbid duplicate values in a form.
    """

    def clean(self):
        self.cleaned_data = super().clean()
        values = list(self.cleaned_data.values())
        if len(values) != len(set(values)):
            # Find which fields have duplicate values
            seen = {}
            duplicates = {}
            for field_name, value in self.cleaned_data.items():
                if value in seen:
                    if value not in duplicates:
                        duplicates[value] = [seen[value]]
                    duplicates[value].append(field_name)
                else:
                    seen[value] = field_name

            # Build list of field names with duplicates
            duplicate_fields = []
            for fields in duplicates.values():
                duplicate_fields.extend(fields)

            # Get field labels for display
            field_labels = [
                str(self.fields[f].label or f.replace("_", " ").title())
                for f in duplicate_fields
            ]
            field_list = ", ".join(field_labels)
            raise ValidationError(f"{field_list} must have different values")
