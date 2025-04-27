from django import forms
from django.utils.safestring import mark_safe
from ai.generators import ImageGenerator


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
            ):
                generator = ImageGenerator()
                images = [
                    generator.generate(f"""Generate the portrait of a role play character of {character.race} race
                    and {character.klass} class, and {character.background} background.
                    There is no text displayed on the generated image.
                    I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS.""")
                    for _ in range(3)
                ]
                choices = [
                    (
                        image,
                        mark_safe(
                            f'<img src="{image}" alt="Character Portrait" class="portrait-option">'
                        ),
                    )
                    for image in images
                ]
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
