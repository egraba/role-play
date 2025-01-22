from ai.generators import TextGenerator


def test_singleton_instance():
    instance1 = TextGenerator()
    instance2 = TextGenerator()
    assert instance1 is instance2
