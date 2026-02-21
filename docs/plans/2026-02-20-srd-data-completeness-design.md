# SRD Data Completeness Design

**Date:** 2026-02-20
**Status:** Approved
**Scope:** Data completeness only — no mechanical changes

## Problem

The role-play app is missing the majority of SRD 5.2.1 content. Only 4 of 9 species, 4 of 17 backgrounds, 4 of ~30 feats, 14 of ~190 spells, and 17 of ~450 monsters are currently populated in fixtures.

## Approach

Four incremental PRs, each independently reviewable and mergeable. Ordered by character creation dependency (species/backgrounds → feats → spells → monsters).

All work is **data only** — no new models, no mechanical enforcement, no migrations required for PRs 2–4. PR 1 requires no migration changes either (species/background enums expand existing choices).

---

## PR 1: Species & Backgrounds

### Species (5 new)

Add to `character/constants/species.py`:
- `SpeciesName`: DRAGONBORN, GNOME, GOLIATH, ORC, TIEFLING
- `SpeciesTraitName`: new values per species (Draconic Ancestry, Breath Weapon, Damage Resistance for Dragonborn; Gnomish Cunning, Darkvision for Gnome; Giant Ancestry, Large Form, Powerful Build for Goliath; Adrenaline Rush, Darkvision, Relentless Endurance for Orc; Fiendish Legacy, Otherworldly Presence for Tiefling)

Add to fixtures:
- `character/fixtures/species_traits.yaml`: new trait entries
- `character/fixtures/species.yaml`: 5 new species entries

### Backgrounds (13 new)

Add to `character/constants/backgrounds.py`:
- `Background` enum: ARTISAN, CHARLATAN, ENTERTAINER, FARMER, GUARD, GUIDE, HERMIT, MERCHANT, NOBLE, PILGRIM, SAILOR, SCRIBE, WAYFARER
- `BACKGROUNDS` dict: entries for each with skill_proficiencies, tool_proficiency, origin_feat references, personality_traits (1–8), ideals (1–6), bonds (1–6), flaws (1–6)

Origin feats referenced by new backgrounds (stubs added to `FeatName` now, fleshed out in PR 2):
- Artisan → Crafter
- Charlatan → Skilled
- Entertainer → Musician
- Farmer → Tough
- Guard → Alert (already exists)
- Guide → Magic Initiate (Druid)
- Hermit → Magic Initiate (Cleric) (already exists)
- Merchant → Lucky
- Noble → Skilled
- Pilgrim → Healer
- Sailor → Tavern Brawler
- Scribe → Skilled
- Wayfarer → Lucky

**Note:** Stub `FeatName` entries (Crafter, Lucky, Musician, Tough, Tavern Brawler, Healer, Magic Initiate Druid, Magic Initiate Bard, etc.) added to constants now so backgrounds resolve correctly. Full feat descriptions come in PR 2.

---

## PR 2: Feats

### Origin Feats (new)

| Feat | Background(s) |
|------|--------------|
| Crafter | Artisan |
| Healer | Pilgrim |
| Lucky | Merchant, Wayfarer |
| Magic Initiate (Bard) | — |
| Magic Initiate (Druid) | Guide |
| Magic Initiate (Sorcerer) | — |
| Magic Initiate (Warlock) | — |
| Musician | Entertainer |
| Skilled | Charlatan, Noble, Scribe |
| Tavern Brawler | Sailor |
| Tough | Farmer |

### General Feats (new, ~25)

Ability Score Improvement, Actor, Athlete, Charger, Chef, Crossbow Expert, Crusher, Defensive Duelist, Dual Wielder, Durable, Great Weapon Master, Heavy Armor Master, Inspiring Leader, Mage Slayer, Mounted Combatant, Observant, Polearm Master, Resilient, Sentinel, Sharpshooter, Shield Master, Skulker, Spell Sniper, War Caster, Weapon Master

### Files changed

- `character/constants/feats.py`: add all new `FeatName` values
- `character/fixtures/feats.yaml`: new entries with feat_type, description, prerequisite

---

## PR 3: Spells (~100 total, ~86 new)

### Selection Criteria

- All SRD cantrips for each class
- Levels 1–5: iconic spells per school ensuring each class has options
- Coverage of all action types: action, bonus action, reaction
- Coverage of key mechanics: concentration, ritual, saving throw, attack roll, healing

### Representative Spell Set (additions)

**Cantrips (~15 new):** Blade Ward, Chill Touch, Dancing Lights, Eldritch Blast, Friends, Guidance, Mending, Message, Minor Illusion, Poison Spray, Ray of Frost, Resistance, Sacred Flame, Shillelagh, Shocking Grasp, Spare the Dying, Thaumaturgy, Toll the Dead, True Strike, Vicious Mockery

**Level 1 (~15 new):** Alarm, Animal Friendship, Bane, Bless, Burning Hands, Charm Person, Command, Comprehend Languages, Detect Magic, Disguise Self, Entangle, Expeditious Retreat, Faerie Fire, False Life, Feather Fall, Fog Cloud, Goodberry, Grease, Healing Word, Heroism, Hideous Laughter, Hunter's Mark, Identify, Inflict Wounds, Jump, Longstrider, Protection from Evil and Good, Sanctuary, Silent Image, Speak with Animals, Thunderwave, Unseen Servant, Witch Bolt

**Level 2 (~15 new):** Aid, Alter Self, Animal Messenger, Arcane Lock, Augury, Barkskin, Blindness/Deafness, Blur, Calm Emotions, Cloud of Daggers, Crown of Madness, Darkness, Darkvision, Detect Thoughts, Enhance Ability, Enlarge/Reduce, Enthrall, Find Traps, Flaming Sphere, Gentle Repose, Heat Metal, Hold Person (exists), Knock, Lesser Restoration, Levitate, Locate Animals or Plants, Locate Object, Magic Mouth, Magic Weapon, Mirror Image, Moonbeam, Nystul's Magic Aura, Pass without Trace, Prayer of Healing, Protection from Poison, Ray of Enfeeblement, Rope Trick, See Invisibility, Silence, Spider Climb, Spiritual Weapon, Suggestion, Warding Bond, Web, Zone of Truth

**Level 3 (~10 new):** Animate Dead, Bestow Curse, Blink, Call Lightning, Clairvoyance, Conjure Animals, Conjure Barrage, Counterspell (exists), Daylight, Dispel Magic, Fear, Feign Death, Gaseous Form, Glyph of Warding, Haste, Hypnotic Pattern, Leomund's Tiny Hut, Lightning Bolt, Mass Healing Word, Meld into Stone, Nondetection, Phantom Steed, Plant Growth, Protection from Energy, Remove Curse, Revivify, Sending, Sleet Storm, Slow, Speak with Dead, Speak with Plants, Spirit Guardians, Stinking Cloud, Tongues, Vampiric Touch, Water Breathing, Water Walk, Wind Wall

**Level 4 (~8 new):** Arcane Eye, Banishment, Black Tentacles, Blight, Compulsion, Confusion, Conjure Minor Elementals, Conjure Woodland Beings, Control Water, Death Ward, Dimension Door, Divination, Dominate Beast, Fabricate, Fire Shield, Freedom of Movement, Giant Insect, Greater Invisibility, Guardian of Faith, Hallucinatory Terrain, Ice Storm, Leomund's Secret Chest, Locate Creature, Mordenkained's Faithful Hound, Mordenkained's Private Sanctum, Otiluke's Resilient Sphere, Phantasmal Killer, Polymorph, Stone Shape, Stoneskin, Wall of Fire (keep), Watery Sphere

**Level 5 (~8 new):** Animate Objects, Antilife Shell, Awaken, Bigby's Hand, Circle of Power, Cloudkill, Commune, Commune with Nature, Cone of Cold, Conjure Elemental, Conjure Volley, Contact Other Plane, Contagion, Creation, Dispel Evil and Good, Dominate Person, Dream, Geas, Greater Restoration, Hold Monster, Insect Plague, Legend Lore, Mass Cure Wounds, Mislead, Modify Memory, Passwall, Planar Binding, Raise Dead, Scrying, Seeming, Swift Quiver, Telekinesis, Telepathic Bond, Teleportation Circle, Tree Stride, Wall of Stone, Wall of Force, Wrath of Nature

### Files changed

- `magic/fixtures/spells.yaml`: ~86 new `magic.spellsettings` entries (no constants changes needed)

---

## PR 4: Monsters (~100 total, ~83 new)

### Selection Criteria

- All CR ranges represented (CR 0 through CR 24)
- All 14 creature types represented
- Humanoid variety: multiple archetypes for encounter building
- Dragon family: all 5 colours × 4 age stages (wyrmling, young, adult, ancient)
- Iconic encounters: every DM's "starter kit"

### Creature Type Coverage

| Type | Count | Examples |
|------|-------|---------|
| Beast | ~15 | Ape, Lion, Tiger, Brown Bear, Giant Spider, Warhorse, Poisonous Snake |
| Humanoid | ~12 | Guard, Bandit Captain, Priest, Knight, Veteran, Gladiator, Cultist, Spy |
| Undead | ~6 | Specter, Wight, Wraith, Ghost, Vampire, Mummy |
| Dragon | ~18 | All 5 colours × wyrmling/young/adult/ancient (Adult Red done) |
| Fiend | ~8 | Imp, Quasit, Dretch, Bearded Devil, Barbed Devil, Erinyes, Balor, Vrock |
| Elemental | +3 | Earth Elemental, Fire Elemental, Water Elemental |
| Giant | +6 | Hill, Stone, Frost, Fire, Cloud, Storm Giant |
| Monstrosity | ~8 | Basilisk, Griffon, Harpy, Hydra, Medusa, Phase Spider, Roc, Winter Wolf |
| Construct | +1 | Stone Golem (Animated Armor) |
| Ooze | +2 | Gelatinous Cube, Black Pudding |
| Aberration | +1 | Aboleth |
| Celestial | +1 | Couatl |
| Plant | +2 | Treant, Shambling Mound |
| Fey | — | (none in core SRD beyond descriptions) |

### Files changed

- `bestiary/fixtures/monsters.yaml`: ~83 new `bestiary.monstersettings` entries
- `bestiary/fixtures/monster_attributes.yaml`: corresponding speed, senses, actions, damage relations for each new monster

---

## What This Plan Does NOT Cover

The following are explicitly out of scope:

- **Mechanics**: Rest mechanics, subclass system, class feature enforcement, opportunity attacks, condition enforcement in combat
- **Levels 6–9 spells**: Can be added later with identical fixture pattern
- **All ~450 SRD monsters**: Remaining ~350 can be added in follow-on PRs
- **Feat mechanical effects**: Feats are descriptive data only; code enforcement is a separate mechanics effort
