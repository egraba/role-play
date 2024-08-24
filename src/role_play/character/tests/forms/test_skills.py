from character.forms.skills import ExtendedSkillsSelectForm, SkillsSelectForm


class TestSkillsSelectForm:
    form = SkillsSelectForm(initial={"klass": None})

    def test_first_skill_field_exists(self):
        assert "first_skill" in self.form.fields

    def test_second_skill_field_exists(self):
        assert "second_skill" in self.form.fields


class TestExtendedSkillsSelectForm:
    form = ExtendedSkillsSelectForm(initial={"klass": None})

    def test_first_skill_field_exists(self):
        assert "first_skill" in self.form.fields

    def test_second_skill_field_exists(self):
        assert "second_skill" in self.form.fields

    def test_third_skill_field_exists(self):
        assert "third_skill" in self.form.fields

    def test_fourth_skill_field_exists(self):
        assert "fourth_skill" in self.form.fields
