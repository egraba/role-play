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

    def _check_all_attributes_exist(self, fields: list[str]) -> None:
        for field in fields:
            try:
                assert getattr(self.character, field) is not None
            except AttributeError as exc:
                raise CharacterAttributeError from exc

    def _check_one_attribute_exists(self, fields: list[str]) -> None:
        is_found = False
        for field in fields:
            try:
                assert getattr(self.character, field) is not None
                is_found = True
                break
            except AttributeError:
                pass
        if not is_found:
            raise CharacterAttributeError(f"No field found among {fields}")

    def are_base_attributes_selected(self):
        try:
            self._check_all_attributes_exist(
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
        if self.character.skills.all() is None:
            return False
        return True

    @state.transition(
        source=CreationState.SKILLS_SELECTION,
        target=CreationState.BACKGROUND_COMPLETION,
        conditions=[are_skills_selected],
    )
    def complete_background(self):
        pass

    def is_background_completed(self):
        try:
            self._check_one_attribute_exists(
                [
                    "equipment",
                    "language",
                    "first_language",
                    "second_language",
                    "tool_proficiency",
                ]
            )
        except CharacterAttributeError:
            return False
        return True

    @state.transition(
        source=CreationState.BACKGROUND_COMPLETION,
        target=CreationState.EQUIPMENT_SELECTION,
        conditions=[is_background_completed],
    )
    def select_equipment(self):
        pass

    def is_equipment_selected(self):
        # Only pack field is checked, as all characters have a pack.
        if self.character.inventory.pack_set.all() is None:
            return False
        return True

    @state.transition(
        source=CreationState.EQUIPMENT_SELECTION,
        target=CreationState.COMPLETE,
        conditions=[is_equipment_selected],
    )
    def complete(self):
        pass
