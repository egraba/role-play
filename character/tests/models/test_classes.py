import pytest

from character.models.classes import ClassAdvancement, ClassFeature, HitPoints


@pytest.mark.django_db
class TestClassFeatureModel:
    class_feature = None

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
    hit_points = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.hit_points = HitPoints.objects.last()

    def test_creation(self):
        assert isinstance(self.hit_points, HitPoints)

    def test_str(self):
        assert str(self.hit_points) == f"{self.hit_points.class_feature} hit points"


@pytest.mark.django_db
class TestClassAdvancementModel:
    class_advancement = None

    @pytest.fixture(autouse=True)
    def setup(self):
        # Fixtures are automatically loaded during the test session initialization.
        self.class_advancement = ClassAdvancement.objects.last()

    def test_creation(self):
        assert isinstance(self.class_advancement, ClassAdvancement)

    def test_str(self):
        assert str(self.class_advancement) == str(self.class_advancement.level)
