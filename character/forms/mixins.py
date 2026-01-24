from django.forms import Form, ValidationError


class NoDuplicateValuesFormMixin(Form):
    """
    Mixin to forbid duplicate values in a form.

    Subclasses can define `duplicate_check_fields` as a list of field names
    to check for duplicates. If not defined, all fields are checked.
    Empty/falsy values are excluded from the duplicate check.
    """

    # Override in subclass to limit which fields are checked for duplicates
    duplicate_check_fields: list[str] | None = None

    def clean(self):
        cleaned_data = super().clean()

        # Determine which fields to check
        fields_to_check = self.duplicate_check_fields or list(cleaned_data.keys())

        # Filter to only non-empty values for the specified fields
        field_values = {
            field_name: value
            for field_name, value in cleaned_data.items()
            if field_name in fields_to_check and value not in (None, "")
        }

        values = list(field_values.values())
        if len(values) != len(set(values)):
            # Find which fields have duplicate values
            seen = {}
            duplicates = {}
            for field_name, value in field_values.items():
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

        return cleaned_data
