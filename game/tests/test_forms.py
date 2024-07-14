from django import forms

from game.forms import QuestCreateForm


class TestQuestCreateForm:
    def test_content_type(self):
        form = QuestCreateForm()
        assert isinstance(form.fields["content"].widget, forms.Textarea)

    def test_content_max_length(self):
        form = QuestCreateForm()
        assert form.fields["content"].max_length == 1000
