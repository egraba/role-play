from django.views.generic import CreateView, DetailView

import master.forms as mforms
import master.models as mmodels


class DetailStoryView(DetailView):
    model = mmodels.Story
    template_name = "master/story.html"


class CreateStoryView(CreateView):
    form_class = mforms.CreateStoryForm
    template_name = "master/createstory.html"
