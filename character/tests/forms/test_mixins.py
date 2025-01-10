from django import forms
from character.forms.mixins import NoDuplicateValuesMixin


class MyForm(NoDuplicateValuesMixin):
    field1 = forms.CharField()
    field2 = forms.CharField()


def test_no_duplicate_values():
    form = MyForm(data={"field1": "value1", "field2": "value2"})
    assert form.is_valid()


def test_duplicate_values():
    form = MyForm(data={"field1": "value1", "field2": "value1"})
    assert not form.is_valid()
    assert form.errors == {"__all__": ["the entered values must be different"]}
