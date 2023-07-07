from django.views.generic import DetailView

import master.models as mmodels


class DetailStoryView(DetailView):
    model = mmodels.Story
    template_name = "story.html"
