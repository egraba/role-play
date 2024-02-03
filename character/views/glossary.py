from django.core.cache import cache
from django.views.generic import TemplateView

from character.models.abilities import AbilityType
from character.models.skills import Skill


class GlossaryView(TemplateView):
    template_name = "character/glossary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ability_types = cache.get_or_set("ability_types", AbilityType.objects.all())
        context["ability_types"] = ability_types

        skills = cache.get_or_create("skills", Skill.objects.all())
        context["skills"] = skills

        return context
