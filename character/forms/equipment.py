from django import forms

from character.utils.equipment import (
    ClericEquipmentChoicesProvider,
    FighterEquipmentChoicesProvider,
    RogueEquipmentChoicesProvider,
    WizardEquipmentChoicesProvider,
)


class FirstWeaponForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("first_weapon_provider")
        super().__init__(*args, **kwargs)

        self.fields["first_weapon"] = forms.ChoiceField(
            choices=equipment_provider.get_first_weapon_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class SecondWeaponForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("second_weapon_provider")
        super().__init__(*args, **kwargs)

        self.fields["second_weapon"] = forms.ChoiceField(
            choices=equipment_provider.get_second_weapon_choices(),
            widget=forms.Select(attrs={"class": "rpgui-dropdown"}),
        )


class ThirdWeaponForm(forms.Form):
    def __init__(self, *args, **kwargs):
        equipment_provider = kwargs.pop("third_weapon_provider")
        super().__init__(*args, **kwargs)

        self.fields["third_weapon"] = forms.ChoiceField(
            choices=equipment_provider.get_third_weapon_choices(),
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

        self.order_fields(["first_weapon", "second_weapon", "armor", "gear", "pack"])


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

        self.order_fields(["first_weapon", "second_weapon", "third_weapon", "pack"])


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

        self.order_fields(["first_weapon", "second_weapon", "pack"])


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

        self.order_fields(["first_weapon", "gear", "pack"])
