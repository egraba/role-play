from django.db import models
from django.test import TestCase
from django.utils import timezone

import chat.models as cmodels


class MessageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cmodels.Message.objects.create()

    def test_date_type(self):
        message = cmodels.Message.objects.last()
        date = message._meta.get_field("date")
        self.assertTrue(date, models.DateTimeField)

    def test_date_default_value(self):
        message = cmodels.Message.objects.last()
        self.assertEqual(message.date.second, timezone.now().second)

    def test_user_type(self):
        message = cmodels.Message.objects.last()
        user = message._meta.get_field("user")
        self.assertTrue(user, models.ForeignKey)

    def test_content_type(self):
        message = cmodels.Message.objects.last()
        content = message._meta.get_field("content")
        self.assertTrue(content, models.CharField)

    def test_content_max_length(self):
        message = cmodels.Message.objects.last()
        max_length = message._meta.get_field("content").max_length
        self.assertEqual(max_length, 200)
