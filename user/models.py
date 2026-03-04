from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # TODO: Encrypt at rest using django-encrypted-model-fields before production deployment.
    anthropic_api_key = models.CharField(max_length=200, blank=True)
