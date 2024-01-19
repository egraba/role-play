from django.views.generic import TemplateView


class GlossaryView(TemplateView):
    template_name = "character/glossary.html"
