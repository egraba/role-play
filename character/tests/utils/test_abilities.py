from character.utils.abilities import compute_modifier


def test_compute_modifier():
    assert compute_modifier(1) == -5
    assert compute_modifier(2) == -4
    assert compute_modifier(3) == -4
    assert compute_modifier(4) == -3
    assert compute_modifier(5) == -3
    assert compute_modifier(6) == -2
    assert compute_modifier(7) == -2
    assert compute_modifier(8) == -1
    assert compute_modifier(9) == -1
    assert compute_modifier(10) == 0
    assert compute_modifier(11) == 0
    assert compute_modifier(12) == 1
    assert compute_modifier(13) == 1
    assert compute_modifier(14) == 2
    assert compute_modifier(15) == 2
    assert compute_modifier(16) == 3
    assert compute_modifier(17) == 3
    assert compute_modifier(18) == 4
    assert compute_modifier(19) == 4
    assert compute_modifier(20) == 5
    assert compute_modifier(21) == 5
    assert compute_modifier(22) == 6
    assert compute_modifier(23) == 6
    assert compute_modifier(24) == 7
    assert compute_modifier(25) == 7
    assert compute_modifier(26) == 8
    assert compute_modifier(27) == 8
    assert compute_modifier(28) == 9
    assert compute_modifier(29) == 9
    assert compute_modifier(30) == 10
