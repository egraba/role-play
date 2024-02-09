from typing import Any

from django.db.models import Choices


def duplicate_choice(choice: Choices, other_choice: Choices = None) -> tuple[Any, Any]:
    """
    Duplicate a Choice and convert it into a tuple.

    Tuples of Choices are used in Django forms.
    If other_choice is passed as parameter, the function concatenates
    both Choice instances and duplicate them.

    Args:
        choice (Choice): Django Choice.
        other_choice (Choice): Django Choice.

    Returns:
        tuple[Any, Any]: Tuple with duplicate Choice instances.
    """

    if other_choice is None:
        return (choice.value, choice.value)
    return (
        f"{choice.value} & {other_choice.value}",
        f"{choice.value} & {other_choice.value}",
    )
