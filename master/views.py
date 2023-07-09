from django.views.generic import CreateView, DetailView, UpdateView

import master.forms as mforms
import master.models as mmodels


class DetailStoryView(DetailView):
    model = mmodels.Story
    template_name = "master/story.html"


class CreateStoryView(CreateView):
    form_class = mforms.CreateStoryForm
    template_name = "master/createstory.html"


class UpdateStoryView(UpdateView):
    model = mmodels.Story
    fields = ["synopsis", "main_conflict", "objective"]
    template_name = "master/updatestory.html"
