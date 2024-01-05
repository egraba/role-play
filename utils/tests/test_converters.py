import pytest
from django.db.models import IntegerChoices, TextChoices

from utils.converters import duplicate_choice


class SomeTextChoice(TextChoices):
    A_TEXT_CHOICE = "A text choice"
    ANOTHER_TEXT_CHOICE = "Another text choice"


class SomeIntegerChoice(IntegerChoices):
    AN_INTEGER_CHOICE = 1
    ANOTHER_INTEGER_CHOICE = 2


@pytest.fixture
def textchoice():
    return SomeTextChoice.A_TEXT_CHOICE


@pytest.fixture
def other_textchoice():
    return SomeTextChoice.ANOTHER_TEXT_CHOICE


@pytest.fixture
def integerchoice():
    return SomeIntegerChoice.AN_INTEGER_CHOICE


@pytest.fixture
def other_integerchoice():
    return SomeIntegerChoice.ANOTHER_INTEGER_CHOICE


def test_duplicate_choice_one_textchoice(textchoice):
    assert duplicate_choice(textchoice) == (textchoice.value, textchoice.value)


def test_duplicate_choice_two_textchoices(textchoice, other_textchoice):
    assert duplicate_choice(textchoice, other_textchoice) == (
        f"{textchoice} & {other_textchoice}",
        f"{textchoice} & {other_textchoice}",
    )


def test_duplicate_choice_one_integerchoice(integerchoice):
    assert duplicate_choice(integerchoice) == (integerchoice.value, integerchoice.value)


def test_duplicate_choice_two_integerchoices(integerchoice, other_integerchoice):
    assert duplicate_choice(integerchoice, other_integerchoice) == (
        f"{integerchoice} & {other_integerchoice}",
        f"{integerchoice} & {other_integerchoice}",
    )
