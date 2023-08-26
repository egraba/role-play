from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

import master.forms as mforms
import master.models as mmodels


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = mmodels.Campaign
    template_name = "master/campaign.html"


class CampaignListView(LoginRequiredMixin, ListView):
    model = mmodels.Campaign
    paginate_by = 20
    ordering = ["title"]
    template_name = "master/campaign_list.html"


class CampaignCreateView(LoginRequiredMixin, CreateView):
    form_class = mforms.CampaignCreateForm
    template_name = "master/campaign_create.html"


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = mmodels.Campaign
    form_class = mforms.CampaignUpdateForm
    template_name = "master/campaign_update.html"
