import pytest

from master.forms import CampaignCreateForm, CampaignUpdateForm

from .factories import CampaignFactory


pytestmark = pytest.mark.django_db


class TestCampaignCreateForm:
    @pytest.fixture
    def valid_data(self):
        return {
            "title": "The Lost Kingdom",
            "synopsis": "A tale of heroes in a forgotten realm.",
            "main_conflict": "An ancient evil has awakened.",
            "objective": "Defeat the dark lord and restore peace.",
        }

    def test_form_has_expected_fields(self):
        form = CampaignCreateForm()
        assert "title" in form.fields
        assert "synopsis" in form.fields
        assert "main_conflict" in form.fields
        assert "objective" in form.fields

    def test_form_excludes_slug_field(self):
        form = CampaignCreateForm()
        assert "slug" not in form.fields

    def test_valid_form(self, valid_data):
        form = CampaignCreateForm(data=valid_data)
        assert form.is_valid(), form.errors

    def test_form_creates_campaign(self, valid_data):
        form = CampaignCreateForm(data=valid_data)
        assert form.is_valid()
        campaign = form.save()
        assert campaign.pk is not None
        assert campaign.title == "The Lost Kingdom"
        assert campaign.slug == "the-lost-kingdom"

    def test_title_is_required(self, valid_data):
        valid_data.pop("title")
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_synopsis_is_required(self, valid_data):
        valid_data.pop("synopsis")
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "synopsis" in form.errors

    def test_main_conflict_is_required(self, valid_data):
        valid_data.pop("main_conflict")
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "main_conflict" in form.errors

    def test_objective_is_required(self, valid_data):
        valid_data.pop("objective")
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "objective" in form.errors

    def test_title_max_length(self, valid_data):
        valid_data["title"] = "x" * 51  # Max is 50
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_synopsis_max_length(self, valid_data):
        valid_data["synopsis"] = "x" * 3001  # Max is 3000
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "synopsis" in form.errors

    def test_main_conflict_max_length(self, valid_data):
        valid_data["main_conflict"] = "x" * 1001  # Max is 1000
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "main_conflict" in form.errors

    def test_objective_max_length(self, valid_data):
        valid_data["objective"] = "x" * 501  # Max is 500
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "objective" in form.errors

    def test_duplicate_title_fails(self, valid_data):
        CampaignFactory(title="The Lost Kingdom")
        form = CampaignCreateForm(data=valid_data)
        assert not form.is_valid()
        assert "title" in form.errors


class TestCampaignUpdateForm:
    @pytest.fixture
    def campaign(self):
        return CampaignFactory(
            title="Original Title",
            synopsis="Original synopsis.",
            main_conflict="Original conflict.",
            objective="Original objective.",
        )

    @pytest.fixture
    def update_data(self):
        return {
            "synopsis": "Updated synopsis with more details.",
            "main_conflict": "A new threat emerges.",
            "objective": "Save the realm from destruction.",
        }

    def test_form_excludes_title_and_slug(self):
        form = CampaignUpdateForm()
        assert "title" not in form.fields
        assert "slug" not in form.fields

    def test_form_has_editable_fields(self):
        form = CampaignUpdateForm()
        assert "synopsis" in form.fields
        assert "main_conflict" in form.fields
        assert "objective" in form.fields

    def test_valid_update_form(self, campaign, update_data):
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert form.is_valid(), form.errors

    def test_form_updates_campaign(self, campaign, update_data):
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert form.is_valid()
        updated = form.save()
        assert updated.synopsis == "Updated synopsis with more details."
        assert updated.main_conflict == "A new threat emerges."
        assert updated.objective == "Save the realm from destruction."
        # Title should remain unchanged
        assert updated.title == "Original Title"

    def test_synopsis_is_required(self, campaign, update_data):
        update_data.pop("synopsis")
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert not form.is_valid()
        assert "synopsis" in form.errors

    def test_main_conflict_is_required(self, campaign, update_data):
        update_data.pop("main_conflict")
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert not form.is_valid()
        assert "main_conflict" in form.errors

    def test_objective_is_required(self, campaign, update_data):
        update_data.pop("objective")
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert not form.is_valid()
        assert "objective" in form.errors

    def test_synopsis_max_length(self, campaign, update_data):
        update_data["synopsis"] = "x" * 3001
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert not form.is_valid()
        assert "synopsis" in form.errors

    def test_title_cannot_be_changed_via_form(self, campaign, update_data):
        """Even if title is submitted, it should be ignored."""
        update_data["title"] = "Hacked Title"
        form = CampaignUpdateForm(instance=campaign, data=update_data)
        assert form.is_valid()
        updated = form.save()
        assert updated.title == "Original Title"
