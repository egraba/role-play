from django.test import TestCase

from character.utils import abilities


class AbilitiesTest(TestCase):
    def test_compute_ability_modifier(self):
        self.assertEqual(abilities.compute_modifier(1), -5)
        self.assertEqual(abilities.compute_modifier(2), -4)
        self.assertEqual(abilities.compute_modifier(3), -4)
        self.assertEqual(abilities.compute_modifier(4), -3)
        self.assertEqual(abilities.compute_modifier(5), -3)
        self.assertEqual(abilities.compute_modifier(6), -2)
        self.assertEqual(abilities.compute_modifier(7), -2)
        self.assertEqual(abilities.compute_modifier(8), -1)
        self.assertEqual(abilities.compute_modifier(9), -1)
        self.assertEqual(abilities.compute_modifier(10), 0)
        self.assertEqual(abilities.compute_modifier(11), 0)
        self.assertEqual(abilities.compute_modifier(12), 1)
        self.assertEqual(abilities.compute_modifier(13), 1)
        self.assertEqual(abilities.compute_modifier(14), 2)
        self.assertEqual(abilities.compute_modifier(15), 2)
        self.assertEqual(abilities.compute_modifier(16), 3)
        self.assertEqual(abilities.compute_modifier(17), 3)
        self.assertEqual(abilities.compute_modifier(18), 4)
        self.assertEqual(abilities.compute_modifier(19), 4)
        self.assertEqual(abilities.compute_modifier(20), 5)
        self.assertEqual(abilities.compute_modifier(21), 5)
        self.assertEqual(abilities.compute_modifier(22), 6)
        self.assertEqual(abilities.compute_modifier(23), 6)
        self.assertEqual(abilities.compute_modifier(24), 7)
        self.assertEqual(abilities.compute_modifier(25), 7)
        self.assertEqual(abilities.compute_modifier(26), 8)
        self.assertEqual(abilities.compute_modifier(27), 8)
        self.assertEqual(abilities.compute_modifier(28), 9)
        self.assertEqual(abilities.compute_modifier(29), 9)
        self.assertEqual(abilities.compute_modifier(30), 10)
