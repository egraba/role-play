import pytest

from character.models.classes import (
    ClassAdvancement,
    ClassFeature,
    HitPoints,
    Proficiencies,
)


@pytest.mark.django_db
class TestClassFeatureModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.class_feature = ClassFeature.objects.last()

    def test_creation(self):
        assert isinstance(self.class_feature, ClassFeature)

    def test_str(self):
        assert (
            str(self.class_feature)
            == f"{self.class_feature.get_class_name_display()}'s feature"
        )


@pytest.mark.django_db
class TestHitPointsModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.hit_points = HitPoints.objects.last()

    def test_creation(self):
        assert isinstance(self.hit_points, HitPoints)

    def test_verbose_name_plural(self):
        assert self.hit_points._meta.verbose_name_plural == "hit points"

    def test_str(self):
        assert str(self.hit_points) == f"{self.hit_points.class_feature} hit points"


@pytest.mark.django_db
class TestProficienciesModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.proficiencies = Proficiencies.objects.last()

    def test_creation(self):
        assert isinstance(self.proficiencies, Proficiencies)

    def test_verbose_name_plural(self):
        assert self.proficiencies._meta.verbose_name_plural == "proficiencies"

    def test_str(self):
        assert (
            str(self.proficiencies)
            == f"{self.proficiencies.class_feature} proficiencies"
        )


@pytest.mark.django_db
class TestClassAdvancementModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.class_advancement = ClassAdvancement.objects.last()

    def test_creation(self):
        assert isinstance(self.class_advancement, ClassAdvancement)

    def test_str(self):
        assert str(self.class_advancement) == str(self.class_advancement.level)