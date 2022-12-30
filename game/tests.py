from django.test import TestCase
from django.urls import reverse

class IndexViewTests(TestCase):
    def test_no_game(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available...")
