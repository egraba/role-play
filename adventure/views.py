from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponseBase
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import (
    ActForm,
    CampaignForm,
    EncounterForm,
    LocationForm,
    NPCForm,
    SceneForm,
)
from .models import Act, Campaign, Encounter, Location, NPC, Scene


# ---------------------------------------------------------------------------
# Campaign views
# ---------------------------------------------------------------------------


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = "adventure/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = "adventure/campaign_detail.html"
    context_object_name = "campaign"

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user).prefetch_related("acts")


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "adventure/campaign_form.html"

    def form_valid(self, form: CampaignForm) -> HttpResponseBase:
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "adventure/campaign_form.html"

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    template_name = "adventure/campaign_confirm_delete.html"
    success_url = reverse_lazy("adventure:campaign-list")

    def get_queryset(self) -> QuerySet[Campaign]:
        return Campaign.objects.filter(owner=self.request.user)


# ---------------------------------------------------------------------------
# Act views
# ---------------------------------------------------------------------------


class ActDetailView(LoginRequiredMixin, DetailView):
    model = Act
    template_name = "adventure/act_detail.html"
    context_object_name = "act"

    def get_queryset(self) -> QuerySet[Act]:
        return Act.objects.filter(campaign__owner=self.request.user).select_related(
            "campaign"
        )


class ActCreateView(LoginRequiredMixin, CreateView):
    model = Act
    form_class = ActForm
    template_name = "adventure/act_form.html"

    def get_campaign(self) -> Campaign:
        return get_object_or_404(
            Campaign, slug=self.kwargs["slug"], owner=self.request.user
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.get_campaign()
        return context

    def form_valid(self, form: ActForm) -> HttpResponseBase:
        form.instance.campaign = self.get_campaign()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


class ActUpdateView(LoginRequiredMixin, UpdateView):
    model = Act
    form_class = ActForm
    template_name = "adventure/act_form.html"

    def get_queryset(self) -> QuerySet[Act]:
        return Act.objects.filter(campaign__owner=self.request.user).select_related(
            "campaign"
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


class ActDeleteView(LoginRequiredMixin, DeleteView):
    model = Act
    template_name = "adventure/act_confirm_delete.html"

    def get_queryset(self) -> QuerySet[Act]:
        return Act.objects.filter(campaign__owner=self.request.user).select_related(
            "campaign"
        )

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


# ---------------------------------------------------------------------------
# Scene views
# ---------------------------------------------------------------------------


class SceneDetailView(LoginRequiredMixin, DetailView):
    model = Scene
    template_name = "adventure/scene_detail.html"
    context_object_name = "scene"

    def get_queryset(self) -> QuerySet[Scene]:
        return Scene.objects.filter(
            act__campaign__owner=self.request.user,
            act__pk=self.kwargs["act_pk"],
        ).select_related("act__campaign")


class SceneCreateView(LoginRequiredMixin, CreateView):
    model = Scene
    form_class = SceneForm
    template_name = "adventure/scene_form.html"

    def get_act(self) -> Act:
        return get_object_or_404(
            Act,
            pk=self.kwargs["act_pk"],
            campaign__slug=self.kwargs["slug"],
            campaign__owner=self.request.user,
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        act = self.get_act()
        context["act"] = act
        context["campaign"] = act.campaign
        return context

    def form_valid(self, form: SceneForm) -> HttpResponseBase:
        form.instance.act = self.get_act()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.act.campaign.get_absolute_url()


class SceneUpdateView(LoginRequiredMixin, UpdateView):
    model = Scene
    form_class = SceneForm
    template_name = "adventure/scene_form.html"

    def get_queryset(self) -> QuerySet[Scene]:
        return Scene.objects.filter(
            act__campaign__owner=self.request.user,
            act__pk=self.kwargs["act_pk"],
        ).select_related("act__campaign")

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["act"] = self.object.act
        context["campaign"] = self.object.act.campaign
        return context

    def get_success_url(self) -> str:
        return self.object.act.campaign.get_absolute_url()


class SceneDeleteView(LoginRequiredMixin, DeleteView):
    model = Scene
    template_name = "adventure/scene_confirm_delete.html"

    def get_queryset(self) -> QuerySet[Scene]:
        return Scene.objects.filter(
            act__campaign__owner=self.request.user,
            act__pk=self.kwargs["act_pk"],
        ).select_related("act__campaign")

    def get_success_url(self) -> str:
        return self.object.act.campaign.get_absolute_url()


# ---------------------------------------------------------------------------
# NPC views
# ---------------------------------------------------------------------------


class NPCCreateView(LoginRequiredMixin, CreateView):
    model = NPC
    form_class = NPCForm
    template_name = "adventure/npc_form.html"

    def get_campaign(self) -> Campaign:
        return get_object_or_404(
            Campaign, slug=self.kwargs["slug"], owner=self.request.user
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.get_campaign()
        return context

    def form_valid(self, form: NPCForm) -> HttpResponseBase:
        form.instance.campaign = self.get_campaign()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


class NPCUpdateView(LoginRequiredMixin, UpdateView):
    model = NPC
    form_class = NPCForm
    template_name = "adventure/npc_form.html"

    def get_queryset(self) -> QuerySet[NPC]:
        return NPC.objects.filter(campaign__owner=self.request.user).select_related(
            "campaign"
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


class NPCDeleteView(LoginRequiredMixin, DeleteView):
    model = NPC
    template_name = "adventure/npc_confirm_delete.html"

    def get_queryset(self) -> QuerySet[NPC]:
        return NPC.objects.filter(campaign__owner=self.request.user).select_related(
            "campaign"
        )

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


# ---------------------------------------------------------------------------
# Location views
# ---------------------------------------------------------------------------


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "adventure/location_form.html"

    def get_campaign(self) -> Campaign:
        return get_object_or_404(
            Campaign, slug=self.kwargs["slug"], owner=self.request.user
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.get_campaign()
        return context

    def form_valid(self, form: LocationForm) -> HttpResponseBase:
        form.instance.campaign = self.get_campaign()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "adventure/location_form.html"

    def get_queryset(self) -> QuerySet[Location]:
        return Location.objects.filter(
            campaign__owner=self.request.user
        ).select_related("campaign")

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["campaign"] = self.object.campaign
        return context

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


class LocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = "adventure/location_confirm_delete.html"

    def get_queryset(self) -> QuerySet[Location]:
        return Location.objects.filter(
            campaign__owner=self.request.user
        ).select_related("campaign")

    def get_success_url(self) -> str:
        return self.object.campaign.get_absolute_url()


# ---------------------------------------------------------------------------
# Encounter views
# ---------------------------------------------------------------------------


class EncounterCreateView(LoginRequiredMixin, CreateView):
    model = Encounter
    form_class = EncounterForm
    template_name = "adventure/encounter_form.html"

    def get_scene(self) -> Scene:
        return get_object_or_404(
            Scene,
            pk=self.kwargs["scene_pk"],
            act__pk=self.kwargs["act_pk"],
            act__campaign__slug=self.kwargs["slug"],
            act__campaign__owner=self.request.user,
        )

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        scene = self.get_scene()
        context["scene"] = scene
        context["act"] = scene.act
        context["campaign"] = scene.act.campaign
        return context

    def form_valid(self, form: EncounterForm) -> HttpResponseBase:
        form.instance.scene = self.get_scene()
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.object.scene.act.campaign.get_absolute_url()


class EncounterUpdateView(LoginRequiredMixin, UpdateView):
    model = Encounter
    form_class = EncounterForm
    template_name = "adventure/encounter_form.html"

    def get_queryset(self) -> QuerySet[Encounter]:
        return Encounter.objects.filter(
            scene__act__campaign__owner=self.request.user
        ).select_related("scene__act__campaign")

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["scene"] = self.object.scene
        context["act"] = self.object.scene.act
        context["campaign"] = self.object.scene.act.campaign
        return context

    def get_success_url(self) -> str:
        return self.object.scene.act.campaign.get_absolute_url()


class EncounterDeleteView(LoginRequiredMixin, DeleteView):
    model = Encounter
    template_name = "adventure/encounter_confirm_delete.html"

    def get_queryset(self) -> QuerySet[Encounter]:
        return Encounter.objects.filter(
            scene__act__campaign__owner=self.request.user
        ).select_related("scene__act__campaign")

    def get_success_url(self) -> str:
        return self.object.scene.act.campaign.get_absolute_url()
