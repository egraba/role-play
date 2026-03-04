"""AI content generation service for adventure planning."""

from typing import TYPE_CHECKING

import anthropic

from adventure.exceptions import AIGenerationError
from adventure.models import Act, Campaign, Encounter, Location, NPC, Scene

if TYPE_CHECKING:
    from user.models import User


def _get_api_key(user: "User") -> str:
    """Get the Anthropic API key for the user. Raises AIGenerationError if not set."""
    key = getattr(user, "anthropic_api_key", "")
    if not key:
        raise AIGenerationError("No Anthropic API key configured.")
    return key


def _call_claude(api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Call Claude API and return the response text."""
    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
        )
        return message.content[0].text
    except anthropic.APIError as exc:
        raise AIGenerationError(f"Claude API error: {exc}") from exc


def generate_campaign_synopsis(user: "User", campaign: Campaign) -> str:
    """Generate a synopsis for a campaign based on its title, conflict, and objective."""
    system = "You are a creative D&D campaign writer. Write vivid, engaging content for tabletop RPG campaigns following SRD 5.2.1 conventions."
    prompt = f"""Write a compelling 2-3 paragraph campaign synopsis for:

Title: {campaign.title}
Main Conflict: {campaign.main_conflict or "(not set)"}
Objective: {campaign.objective or "(not set)"}
Tone: {campaign.get_tone_display()}
Party Level: {campaign.party_level}

Write the synopsis in second person ("The players will...") suitable for a DM overview."""
    return _call_claude(_get_api_key(user), system, prompt)


def generate_act_summary(user: "User", act: Act) -> str:
    """Generate a summary for an act."""
    campaign = act.campaign
    system = "You are a creative D&D campaign writer. Write concise, action-focused act summaries for tabletop RPG campaigns."
    prompt = f"""Write a 1-2 paragraph act summary for Act {act.order}: "{act.title}"

Campaign: {campaign.title}
Campaign Conflict: {campaign.main_conflict or "(not set)"}
Act Goal: {act.goal or "(not set)"}

Write the summary from a DM perspective, describing what happens in this act."""
    return _call_claude(_get_api_key(user), system, prompt)


def generate_scene_description(user: "User", scene: Scene) -> str:
    """Generate a description for a scene."""
    act = scene.act
    campaign = act.campaign
    system = "You are a creative D&D encounter and scene designer. Write evocative scene descriptions for tabletop RPG play."
    prompt = f"""Write a rich 2-3 paragraph scene description for "{scene.title}" (Scene {scene.order}, {scene.get_scene_type_display()}).

Campaign: {campaign.title}
Act: {act.title}
Hook: {scene.hook or "(not set)"}

Write the description in present tense from the DM perspective, describing the environment, atmosphere, and key elements."""
    return _call_claude(_get_api_key(user), system, prompt)


def generate_npc_personality(user: "User", npc: NPC) -> str:
    """Generate personality details for an NPC."""
    campaign = npc.campaign
    system = "You are a creative D&D storyteller. Create memorable, consistent NPC personalities for tabletop RPG campaigns."
    prompt = f"""Generate personality, motivation, and appearance details for NPC "{npc.name}" in campaign "{campaign.title}".

Role: {npc.role or "(not set)"}
Campaign Tone: {campaign.get_tone_display()}

Provide:
1. Personality (2-3 sentences)
2. Motivation (1-2 sentences)
3. Appearance (1-2 sentences)

Format as plain text, label each section."""
    return _call_claude(_get_api_key(user), system, prompt)


def generate_location_description(user: "User", location: Location) -> str:
    """Generate a description for a location."""
    campaign = location.campaign
    system = "You are a creative D&D worldbuilder. Write vivid location descriptions for tabletop RPG settings."
    prompt = f"""Write a 2-3 paragraph description for "{location.name}" ({location.get_region_display()}) in campaign "{campaign.title}".

Campaign Tone: {campaign.get_tone_display()}
Campaign Setting: {campaign.setting or "(not set)"}

Describe the location's atmosphere, key features, and what makes it memorable."""
    return _call_claude(_get_api_key(user), system, prompt)


def generate_encounter_description(user: "User", encounter: Encounter) -> str:
    """Generate a description for an encounter."""
    scene = encounter.scene
    campaign = scene.act.campaign
    system = "You are a creative D&D encounter designer. Write engaging encounter descriptions for tabletop RPG play."
    prompt = f"""Write a 2-paragraph encounter description for "{encounter.title}" ({encounter.get_encounter_type_display()}, {encounter.get_difficulty_display()}).

Campaign: {campaign.title}
Scene: {scene.title}

Paragraph 1: What is happening / the immediate situation.
Paragraph 2: Tactical notes and key elements for the DM."""
    return _call_claude(_get_api_key(user), system, prompt)
