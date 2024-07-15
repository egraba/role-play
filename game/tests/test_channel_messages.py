from game.channel_messages import display


def test_display():
    some_message = "some message"
    assert display(some_message) == some_message
