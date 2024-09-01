from viewflow import fsm

from .constants.character import CreationState
from .exceptions import CharacterAttributeError


class CreationFlow:
    state = fsm.State(CreationState, default=CreationState.BASE_ATTRIBUTES_SELECTION)

    def __init__(self, character):
        self.character = character

    @state.setter()
    def _set_creation_state(self, value):
        self.character.creation_state = value

    @state.getter()
    def _get_creation_state(self):
        return self.character.creation_state

    @state.on_success()
    def _on_transition_success(self, descriptor, source, target):
        self.character.save()

    def _check_attributes_exist(self, fields: list[str]) -> None:
        for field in fields:
            try:
                assert getattr(self.character, field) is not None
            except AttributeError as exc:
                raise CharacterAttributeError from exc

    def are_base_attributes_selected(self):
        try:
            self._check_attributes_exist(
                [
                    "name",
                    "race",
                    "klass",
                    "background",
                    "strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma",
                ]
            )
        except CharacterAttributeError:
            return False
        return True

    @state.transition(
        source=CreationState.BASE_ATTRIBUTES_SELECTION,
        target=CreationState.SKILLS_SELECTION,
        conditions=[are_base_attributes_selected],
    )
    def select_skills(self):
        pass

    def are_skills_selected(self):
        try:
            self._check_attributes_exist(
                [
                    "first_skill",
                    "second_skill",
                ]
            )
        except CharacterAttributeError:
            return False
        return True

    @state.transition(
        source=CreationState.SKILLS_SELECTION,
        target=CreationState.BACKGROUND_COMPLETION,
        conditions=[are_skills_selected],
    )
    def complete_background(self):
        pass
