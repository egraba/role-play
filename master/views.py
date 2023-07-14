from django.views.generic import CreateView, DetailView, ListView, UpdateView

import master.forms as mforms
import master.models as mmodels


class StoryDetailView(DetailView):
    model = mmodels.Story
    template_name = "master/story.html"


class StoryListView(ListView):
    model = mmodels.Story
    paginate_by = 20
    template_name = "master/story_list.html"


class StoryCreateView(CreateView):
    form_class = mforms.CreateStoryForm
    template_name = "master/story_create.html"


class StoryUpdateView(UpdateView):
    model = mmodels.Story
    fields = ["synopsis", "main_conflict", "objective"]
    template_name = "master/story_update.html"
