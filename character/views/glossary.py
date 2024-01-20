from django.views.generic import TemplateView

from character.models.abilities import AbilityType
from character.models.skills import Skill


class GlossaryView(TemplateView):
    template_name = "character/glossary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ability_types"] = AbilityType.objects.all()
        context["skills"] = Skill.objects.all()
        return context
