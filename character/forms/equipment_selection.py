from django import forms

from character.utils.classes.equipment_choices import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)


class FirstWeaponForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("first_weapon_provider")
        super().__init__(*args, **kwargs)

        self.fields["weapon1"] = forms.ChoiceField(
            choices=equipment_provider.get_weapon1_choices(),
            label="First weapon",
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SecondWeaponForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("second_weapon_provider")
        super().__init__(*args, **kwargs)

        self.fields["weapon2"] = forms.ChoiceField(
            choices=equipment_provider.get_weapon2_choices(),
            label="Second weapon",
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class ThirdWeaponForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("third_weapon_provider")
        super().__init__(*args, **kwargs)

        self.fields["weapon3"] = forms.ChoiceField(
            choices=equipment_provider.get_weapon3_choices(),
            label="Third weapon",
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class ArmorForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("armor_provider")
        super().__init__(*args, **kwargs)

        self.fields["armor"] = forms.ChoiceField(
            choices=equipment_provider.get_armor_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class GearForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("gear_provider")
        super().__init__(*args, **kwargs)

        self.fields["gear"] = forms.ChoiceField(
            choices=equipment_provider.get_gear_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class PackForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("pack_provider")
        super().__init__(*args, **kwargs)

        self.fields["pack"] = forms.ChoiceField(
            choices=equipment_provider.get_pack_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class ClericEquipmentSelectForm(
    FirstWeaponForm, SecondWeaponForm, ArmorForm, GearForm, PackForm
):
    def __init__(self, *args, **kwargs):
        equipment_provider = ClericEquipmentChoicesProvider()
        data = kwargs.get("data")
        super().__init__(
            first_weapon_provider=equipment_provider,
            second_weapon_provider=equipment_provider,
            armor_provider=equipment_provider,
            gear_provider=equipment_provider,
            pack_provider=equipment_provider,
            data=data,
        )


class FighterEquipmentSelectForm(
    FirstWeaponForm, SecondWeaponForm, ThirdWeaponForm, PackForm
):
    def __init__(self, *args, **kwargs):
        equipment_provider = FighterEquipmentChoicesProvider()
        data = kwargs.get("data")
        super().__init__(
            first_weapon_provider=equipment_provider,
            second_weapon_provider=equipment_provider,
            third_weapon_provider=equipment_provider,
            pack_provider=equipment_provider,
            data=data,
        )


class RogueEquipmentSelectForm(FirstWeaponForm, SecondWeaponForm, PackForm):
    def __init__(self, *args, **kwargs):
        equipment_provider = RogueEquipmentChoicesProvider()
        data = kwargs.get("data")
        super().__init__(
            first_weapon_provider=equipment_provider,
            second_weapon_provider=equipment_provider,
            pack_provider=equipment_provider,
            data=data,
        )


class WizardEquipmentSelectForm(FirstWeaponForm, GearForm, PackForm):
    def __init__(self, *args, **kwargs):
        equipment_provider = WizardEquipmentChoicesProvider()
        data = kwargs.get("data")
        super().__init__(
            first_weapon_provider=equipment_provider,
            gear_provider=equipment_provider,
            pack_provider=equipment_provider,
            data=data,
        )
