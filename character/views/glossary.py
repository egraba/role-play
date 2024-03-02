from django.core.cache import cache
from django.views.generic import TemplateView

from ..models.abilities import AbilityType
from ..models.skills import Skill
from ..utils.cache import ABILITY_TYPES_KEY


class GlossaryView(TemplateView):
    template_name = "character/glossary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ability_types = cache.get_or_set(ABILITY_TYPES_KEY, AbilityType.objects.all())
        context["ability_types"] = ability_types

        skills = cache.get_or_set("skills", Skill.objects.all())
        context["skills"] = skills

        return context
