from django.core.cache import cache
from django.views.generic import TemplateView

from character.models.abilities import AbilityType
from character.models.skills import Skill


class GlossaryView(TemplateView):
    template_name = "character/glossary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ability_types = cache.get("ability_types")
        if not ability_types:
            ability_types = AbilityType.objects.all()
            cache.set("ability_types", ability_types)
        context["ability_types"] = ability_types

        skills = cache.get("skills")
        if not skills:
            skills = Skill.objects.all()
            cache.set("skills", skills)
        context["skills"] = skills

        return context
