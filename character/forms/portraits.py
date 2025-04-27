import logging
from django import forms
from django.utils.safestring import mark_safe
from ai.generators import ImageGenerator

logger = logging.getLogger(__name__)


class ImageRadioSelect(forms.RadioSelect):
    """
    A custom widget that displays images as radio options.
    """

    template_name = "character/widgets/image_radio_select.html"


class PortraitSelectForm(forms.Form):
    """
    Form for selecting a character portrait from generated images.
    """

    portrait = forms.ChoiceField(
        widget=ImageRadioSelect(),
        required=True,
        label="Select a portrait for your character",
        help_text="Choose one of the generated portraits for your character.",
    )

    regenerate = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, portrait_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        character = self.initial["character"]

        # Check if the form is being submitted (POST method)
        if self.is_bound and "portrait" in self.data:
            # If form is being submitted, use the submitted portrait value
            submitted_url = self.data.get("portrait")
            choices = [
                (
                    submitted_url,
                    mark_safe(
                        f'<img src="{submitted_url}" alt="Character Portrait" class="portrait-option">'
                    ),
                )
            ]
        else:
            # If showing the form for the first time, provide a button to generate images
            self.fields["generate_portraits"] = forms.BooleanField(
                required=False,
                widget=forms.HiddenInput(),
                initial=False,
            )

            # Only generate images if the generate button was clicked
            if (
                "generate_portraits" in self.data
                and self.data.get("generate_portraits") == "True"
            ) or ("regenerate" in self.data and self.data.get("regenerate") == "True"):
                try:
                    generator = ImageGenerator()

                    # Use the enhanced portrait generation method
                    images = generator.generate_character_portraits(
                        race=str(character.race),
                        klass=str(character.klass),
                        background=str(character.background),
                        gender=str(character.gender)
                        if hasattr(character, "gender")
                        else None,
                        count=3,
                    )

                    # Handle the case where we have fewer images than expected
                    if not images:
                        logger.warning("No portraits were generated")
                        choices = self._get_error_choices(
                            "Failed to generate portraits. Please try again."
                        )
                    else:
                        choices = [
                            (
                                image,
                                mark_safe(
                                    f'<img src="{image}" alt="Character Portrait" class="portrait-option">'
                                ),
                            )
                            for image in images
                        ]

                        # Add regenerate button
                        choices.append(
                            (
                                "",
                                mark_safe(
                                    '<div class="portrait-action"><button type="submit" name="regenerate" value="True" class="btn btn-secondary">Generate New Options</button></div>'
                                ),
                            )
                        )
                except Exception as e:
                    logger.error(f"Error generating portraits: {str(e)}")
                    choices = self._get_error_choices(
                        "An error occurred while generating portraits. Please try again later."
                    )
            else:
                # Provide a placeholder and generate button when images haven't been generated yet
                choices = [
                    (
                        "",
                        mark_safe(
                            '<div class="portrait-placeholder"><button type="submit" name="generate_portraits" value="True" class="btn btn-primary">Generate Portraits</button></div>'
                        ),
                    )
                ]

        self.fields["portrait"].choices = choices

    def _get_error_choices(self, error_message):
        """
        Helper method to return choices with an error message.
        """
        return [
            (
                "",
                mark_safe(
                    f'<div class="portrait-error"><p class="text-danger">{error_message}</p>'
                    '<button type="submit" name="generate_portraits" value="True" class="btn btn-primary">Try Again</button></div>'
                ),
            )
        ]
