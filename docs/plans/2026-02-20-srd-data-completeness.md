# SRD Data Completeness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fill all SRD 5.2.1 content gaps across species, backgrounds, feats, spells, and monsters via four incremental PRs.

**Architecture:** Pure data additions — new constants enum values + YAML fixture entries. No new models, no migrations (except PR 1 which may need a migration if SpeciesName/Background choices expand a constrained field). Each PR is independently mergeable.

**Tech Stack:** Django fixtures (YAML), Python TextChoices enums, pytest-django

---

## PR 1: Species & Backgrounds

Branch: `feat/srd-species-backgrounds`

---

### Task 1: Create branch

**Step 1: Create and switch to feature branch**

```bash
git checkout -b feat/srd-species-backgrounds
```

---

### Task 2: Add 5 new species to constants

**Files:**
- Modify: `character/constants/species.py`

**Step 1: Add new SpeciesName and SpeciesTraitName values**

Open `character/constants/species.py` and extend both enums:

```python
class SpeciesName(TextChoices):
    DRAGONBORN = "dragonborn", "Dragonborn"
    DWARF = "dwarf", "Dwarf"
    ELF = "elf", "Elf"
    GNOME = "gnome", "Gnome"
    GOLIATH = "goliath", "Goliath"
    HALFLING = "halfling", "Halfling"
    HUMAN = "human", "Human"
    ORC = "orc", "Orc"
    TIEFLING = "tiefling", "Tiefling"


class SpeciesTraitName(TextChoices):
    # Dragonborn traits
    DRACONIC_ANCESTRY = "draconic_ancestry", "Draconic Ancestry"
    BREATH_WEAPON = "breath_weapon", "Breath Weapon"
    DAMAGE_RESISTANCE = "damage_resistance", "Damage Resistance"
    # Dwarf traits (existing)
    DWARVEN_RESILIENCE = "dwarven_resilience", "Dwarven Resilience"
    DWARVEN_TOUGHNESS = "dwarven_toughness", "Dwarven Toughness"
    STONECUNNING = "stonecunning", "Stonecunning"
    # Elf traits (existing)
    FEY_ANCESTRY = "fey_ancestry", "Fey Ancestry"
    KEEN_SENSES = "keen_senses", "Keen Senses"
    TRANCE = "trance", "Trance"
    # Gnome traits
    GNOMISH_CUNNING = "gnomish_cunning", "Gnomish Cunning"
    # Goliath traits
    GIANT_ANCESTRY = "giant_ancestry", "Giant Ancestry"
    LARGE_FORM = "large_form", "Large Form"
    POWERFUL_BUILD = "powerful_build", "Powerful Build"
    # Halfling traits (existing)
    BRAVE = "brave", "Brave"
    HALFLING_NIMBLENESS = "halfling_nimbleness", "Halfling Nimbleness"
    LUCKY = "lucky", "Lucky"
    # Human traits (existing)
    RESOURCEFUL = "resourceful", "Resourceful"
    SKILLFUL = "skillful", "Skillful"
    VERSATILE = "versatile", "Versatile"
    # Orc traits
    ADRENALINE_RUSH = "adrenaline_rush", "Adrenaline Rush"
    RELENTLESS_ENDURANCE = "relentless_endurance", "Relentless Endurance"
    # Tiefling traits
    FIENDISH_LEGACY = "fiendish_legacy", "Fiendish Legacy"
    OTHERWORLDLY_PRESENCE = "otherworldly_presence", "Otherworldly Presence"
```

**Step 2: Run existing species tests to verify constants don't break anything**

```bash
doppler run -- uv run pytest character/tests/models/test_species.py -v
```

Expected: All tests pass (no model or fixture changes yet, constants only).

**Step 3: Commit**

```bash
git add character/constants/species.py
git commit -m "feat: add species constants for Dragonborn, Gnome, Goliath, Orc, Tiefling"
```

---

### Task 3: Add species trait and species fixtures

**Files:**
- Modify: `character/fixtures/species_traits.yaml`
- Modify: `character/fixtures/species.yaml`

**Step 1: Add new trait entries to `species_traits.yaml`**

Append after the existing human traits section:

```yaml
# Dragonborn traits
- model: character.speciestrait
  pk: draconic_ancestry
  fields:
    name: draconic_ancestry
    description: |
      You have a draconic origin tied to one type of dragon. Choose the dragon
      type from the Draconic Ancestry table; this determines the damage type for
      your Breath Weapon and Damage Resistance traits.

- model: character.speciestrait
  pk: breath_weapon
  fields:
    name: breath_weapon
    description: |
      When you take the Attack action on your turn, you can replace one of your
      attacks with an exhalation of magical energy in either a 15-foot Cone or a
      30-foot Line that is 5 feet wide (your choice). Each creature in that area
      must make a Dexterity saving throw (DC 8 + your Constitution modifier +
      your Proficiency Bonus). On a failed save, a creature takes 1d10 damage of
      the type determined by your Draconic Ancestry. On a successful save, it
      takes half as much damage. This damage increases by 1d10 when you reach
      5th level (2d10), 11th level (3d10), and 17th level (4d10). You can use
      this Breath Weapon a number of times equal to your Proficiency Bonus, and
      you regain all expended uses when you finish a Long Rest.

- model: character.speciestrait
  pk: damage_resistance
  fields:
    name: damage_resistance
    description: |
      You have Resistance to the damage type determined by your Draconic
      Ancestry trait.

# Gnome traits
- model: character.speciestrait
  pk: gnomish_cunning
  fields:
    name: gnomish_cunning
    description: |
      You have Advantage on Intelligence, Wisdom, and Charisma saving throws.

# Goliath traits
- model: character.speciestrait
  pk: giant_ancestry
  fields:
    name: giant_ancestry
    description: |
      You are descended from Giants. Choose one of the following benefits,
      which reflects the nature of your giant heritage. You can use the chosen
      benefit a number of times equal to your Proficiency Bonus, and you regain
      all expended uses when you finish a Long Rest.
      Cloud Giant: You have a Fly Speed equal to your Speed while you are not
      wearing Medium or Heavy armor.
      Fire Giant: On a hit with a weapon, you can cause the attack to deal
      extra Fire damage equal to your Proficiency Bonus.
      Frost Giant: On a hit with a weapon, you can cause the attack to deal
      extra Cold damage equal to your Proficiency Bonus.
      Hill Giant: When you succeed on a Strength saving throw, you can move
      a creature within 5 feet of you up to 15 feet in a direction of your choice.
      Stone Giant: As a Reaction when you take Bludgeoning, Piercing, or
      Slashing damage, you can halve the damage (rounded down).
      Storm Giant: Immediately after you take Lightning or Thunder damage, you
      can use a Reaction to deal Lightning damage to a creature within 60 feet
      equal to your Proficiency Bonus.

- model: character.speciestrait
  pk: large_form
  fields:
    name: large_form
    description: |
      Starting at 5th level, you can change your size to Large as a Bonus
      Action if you're in a big enough space. This transformation lasts for
      10 minutes or until you end it (no action required). For that duration,
      you have Advantage on Strength checks, and your Speed increases by 10
      feet. Once you use this trait, you can't use it again until you finish
      a Long Rest.

- model: character.speciestrait
  pk: powerful_build
  fields:
    name: powerful_build
    description: |
      You have Advantage on any saving throw you make to end the Grappled
      condition. You also count as one size larger when determining your
      carrying capacity.

# Orc traits
- model: character.speciestrait
  pk: adrenaline_rush
  fields:
    name: adrenaline_rush
    description: |
      You can take the Dash action as a Bonus Action. When you do so, you gain
      a number of Temporary Hit Points equal to your Proficiency Bonus. You can
      use this trait a number of times equal to your Proficiency Bonus, and you
      regain all expended uses when you finish a Short or Long Rest.

- model: character.speciestrait
  pk: relentless_endurance
  fields:
    name: relentless_endurance
    description: |
      When you are reduced to 0 Hit Points but not killed outright, you can
      drop to 1 Hit Point instead. Once you use this trait, you can't do so
      again until you finish a Long Rest.

# Tiefling traits
- model: character.speciestrait
  pk: fiendish_legacy
  fields:
    name: fiendish_legacy
    description: |
      You are the recipient of a legacy of magic that an ancestor received from
      a fiend. Choose a legacy from the Fiendish Legacies table. You gain the
      level 1 benefit of the chosen legacy. Starting at 3rd level and again at
      5th level, you gain higher-level benefits of the chosen legacy. Once you
      cast a spell with this trait, you can't cast that spell with it again
      until you finish a Long Rest; however, you can cast the spell using any
      spell slots you have of the appropriate level.
      Intelligence, Wisdom, or Charisma is your spellcasting ability for the
      spells you cast with this trait (choose when you select this species).

- model: character.speciestrait
  pk: otherworldly_presence
  fields:
    name: otherworldly_presence
    description: |
      You know the Thaumaturgy cantrip. When you cast it with this trait, the
      spell uses the same spellcasting ability you use for your Fiendish Legacy
      spells.
```

**Step 2: Add new species entries to `species.yaml`**

Append after the existing human entry:

```yaml
- model: character.species
  pk: dragonborn
  fields:
    name: dragonborn
    size: M
    speed: 30
    darkvision: 0
    traits:
      - draconic_ancestry
      - breath_weapon
      - damage_resistance
    languages:
      - 1  # Common
      - 4  # Draconic
    description: |
      Dragonborn walk proudly through a world that greets them with fearful
      incomprehension. They are shaped by draconic magic and bear the mark of
      their dragon ancestor.

- model: character.species
  pk: gnome
  fields:
    name: gnome
    size: S
    speed: 30
    darkvision: 60
    traits:
      - gnomish_cunning
      - keen_senses
    languages:
      - 1  # Common
      - 6  # Gnomish
    description: |
      Gnomes are small, curious people who delight in invention and discovery.
      They have 60 feet of Darkvision and advantage on Intelligence, Wisdom,
      and Charisma saving throws.

- model: character.species
  pk: goliath
  fields:
    name: goliath
    size: M
    speed: 35
    darkvision: 0
    traits:
      - giant_ancestry
      - large_form
      - powerful_build
    languages:
      - 1  # Common
      - 5  # Giant
    description: |
      Goliaths are massive folk who dwell at the peaks of the highest mountains.
      They possess Giant blood and can channel extraordinary physical power.

- model: character.species
  pk: orc
  fields:
    name: orc
    size: M
    speed: 30
    darkvision: 120
    traits:
      - adrenaline_rush
      - relentless_endurance
    languages:
      - 1  # Common
      - 8  # Orc
    description: |
      Orcs are a fierce and survivalist people who live in lands ravaged by
      conflict. They have 120 feet of Darkvision and can draw on bursts of
      adrenaline.

- model: character.species
  pk: tiefling
  fields:
    name: tiefling
    size: M
    speed: 30
    darkvision: 60
    traits:
      - fiendish_legacy
      - otherworldly_presence
    languages:
      - 1  # Common
      - 9  # Infernal
    description: |
      Tieflings bear the mark of a fiendish ancestor. They have 60 feet of
      Darkvision and innate magical abilities tied to their infernal heritage.
```

**Step 3: Add missing languages to `languages.yaml`**

Check `character/fixtures/languages.yaml` — it needs entries for Draconic (pk: 4), Giant (pk: 5), Gnomish (pk: 6), Orc (pk: 8), Infernal (pk: 9) if not already present. If the file uses sequential PKs, verify and add only what's missing.

```bash
grep -n "name:" character/fixtures/languages.yaml
```

Add any missing language entries following the existing pattern:
```yaml
- model: character.language
  pk: 4
  fields:
    name: draconic
    language_type: S
```

**Step 4: Run tests**

```bash
doppler run -- uv run pytest character/tests/models/test_species.py -v
```

Expected: All tests pass.

**Step 5: Commit**

```bash
git add character/fixtures/species_traits.yaml character/fixtures/species.yaml character/fixtures/languages.yaml
git commit -m "feat: add species fixtures for Dragonborn, Gnome, Goliath, Orc, Tiefling"
```

---

### Task 4: Add new background constants and stub feats

**Files:**
- Modify: `character/constants/backgrounds.py`
- Modify: `character/constants/feats.py`

The 13 new backgrounds reference origin feats that don't exist yet. Add stub `FeatName` entries now so backgrounds can reference them. Full feat descriptions come in PR 2.

**Step 1: Add stub FeatName entries to `character/constants/feats.py`**

```python
class FeatName(TextChoices):
    # Existing
    ALERT = "alert", "Alert"
    MAGIC_INITIATE_CLERIC = "magic_initiate_cleric", "Magic Initiate (Cleric)"
    MAGIC_INITIATE_WIZARD = "magic_initiate_wizard", "Magic Initiate (Wizard)"
    SAVAGE_ATTACKER = "savage_attacker", "Savage Attacker"
    # New origin feats (stubs — full descriptions added in PR 2)
    CRAFTER = "crafter", "Crafter"
    HEALER = "healer", "Healer"
    LUCKY = "lucky", "Lucky"
    MAGIC_INITIATE_BARD = "magic_initiate_bard", "Magic Initiate (Bard)"
    MAGIC_INITIATE_DRUID = "magic_initiate_druid", "Magic Initiate (Druid)"
    MAGIC_INITIATE_SORCERER = "magic_initiate_sorcerer", "Magic Initiate (Sorcerer)"
    MAGIC_INITIATE_WARLOCK = "magic_initiate_warlock", "Magic Initiate (Warlock)"
    MUSICIAN = "musician", "Musician"
    SKILLED = "skilled", "Skilled"
    TAVERN_BRAWLER = "tavern_brawler", "Tavern Brawler"
    TOUGH = "tough", "Tough"
```

**Step 2: Add new Background enum values and BACKGROUNDS dict entries**

Open `character/constants/backgrounds.py` and add to the `Background` enum:

```python
class Background(TextChoices):
    ACOLYTE = "acolyte", "Acolyte"
    ARTISAN = "artisan", "Artisan"
    CHARLATAN = "charlatan", "Charlatan"
    CRIMINAL = "criminal", "Criminal"
    ENTERTAINER = "entertainer", "Entertainer"
    FARMER = "farmer", "Farmer"
    GUARD = "guard", "Guard"
    GUIDE = "guide", "Guide"
    HERMIT = "hermit", "Hermit"
    MERCHANT = "merchant", "Merchant"
    NOBLE = "noble", "Noble"
    PILGRIM = "pilgrim", "Pilgrim"
    SAGE = "sage", "Sage"
    SAILOR = "sailor", "Sailor"
    SCRIBE = "scribe", "Scribe"
    SOLDIER = "soldier", "Soldier"
    WAYFARER = "wayfarer", "Wayfarer"
```

Then add each new entry to the `BACKGROUNDS` dict following the exact pattern of existing entries (skill_proficiencies, tool_proficiency, origin_feat, personality_traits 1–8, ideals 1–6, bonds 1–6, flaws 1–6). Source all text verbatim from SRD 5.2.1.

Background → origin feat mapping:
- Artisan → `FeatName.CRAFTER`
- Charlatan → `FeatName.SKILLED`
- Entertainer → `FeatName.MUSICIAN`
- Farmer → `FeatName.TOUGH`
- Guard → `FeatName.ALERT`
- Guide → `FeatName.MAGIC_INITIATE_DRUID`
- Hermit → `FeatName.MAGIC_INITIATE_CLERIC`
- Merchant → `FeatName.LUCKY`
- Noble → `FeatName.SKILLED`
- Pilgrim → `FeatName.HEALER`
- Sailor → `FeatName.TAVERN_BRAWLER`
- Scribe → `FeatName.SKILLED`
- Wayfarer → `FeatName.LUCKY`

Background → skill proficiencies mapping (verify against SRD 5.2.1):
- Artisan: Insight, Persuasion
- Charlatan: Deception, Sleight of Hand
- Entertainer: Acrobatics, Performance
- Farmer: Animal Handling, Nature
- Guard: Athletics, Perception
- Guide: Athletics, Survival
- Hermit: Medicine, Religion
- Merchant: Animal Handling, Persuasion
- Noble: History, Persuasion
- Pilgrim: Insight, Religion
- Sailor: Acrobatics, Perception
- Scribe: Investigation, Perception
- Wayfarer: Insight, Stealth

**Step 3: Add new tool names if missing**

Check `equipment/constants/equipment.py` for `ToolName`. New backgrounds reference tools that may not exist yet:
- Artisan's Tools (various — use a generic or pick one; SRD gives "Artisan's Tools of your choice")
- Forgery Kit (Charlatan)
- Musical Instrument (Entertainer — "Musical Instrument of your choice")
- Carpenter's Tools (Farmer)
- Gaming Set (Guard, Noble — "Gaming Set of your choice")
- Cartographer's Tools (Guide)
- Herbalism Kit (Hermit, Pilgrim)
- Navigator's Tools (Merchant, Sailor)
- Calligrapher's Supplies (Scribe)
- Thieves' Tools (Wayfarer)

Add any missing entries to `ToolName` in `equipment/constants/equipment.py`. Use `tool_proficiency: None` for "choice" tools.

**Step 4: Run the background form tests**

```bash
doppler run -- uv run pytest character/tests/forms/test_backgrounds.py -v
```

Expected: Existing tests pass. No new tests yet for new backgrounds — those come in Task 5.

**Step 5: Commit**

```bash
git add character/constants/feats.py character/constants/backgrounds.py equipment/constants/equipment.py
git commit -m "feat: add background and stub feat constants for 13 new SRD backgrounds"
```

---

### Task 5: Add stub feat fixtures and background fixtures

**Files:**
- Modify: `character/fixtures/feats.yaml`
- Modify: `character/fixtures/backgrounds.yaml` (this file does not exist yet — backgrounds are in constants only, not in fixtures; check if backgrounds are stored in DB or only as Python dict)

**Step 1: Check if backgrounds need fixtures**

```bash
grep -r "Background" character/migrations/ | grep "choices" | head -5
```

Backgrounds are stored as a `ChoiceField` on `Character`, not as a separate model. **No fixture needed** for backgrounds — the `BACKGROUNDS` dict in constants is the source of truth used at runtime. Skip fixture creation for backgrounds.

**Step 2: Add stub fixture entries for new feats**

Append to `character/fixtures/feats.yaml` for each new stub FeatName:

```yaml
- model: character.feat
  pk: crafter
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You gain proficiency with three different Artisan's Tools of your choice.
      Whenever you finish a Long Rest, you can make a product of one of the
      Artisan's Tools you're proficient with. The product can be sold for up to
      5 GP or used as a spellcasting focus if applicable. The product is nonmagical.

- model: character.feat
  pk: healer
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You gain the ability to stabilize the dying and use a Healer's Kit to
      restore Hit Points. As an action, you can expend one use of a Healer's
      Kit to tend to a creature and restore 1d6 + 4 Hit Points to it, plus
      additional Hit Points equal to the creature's maximum number of Hit Dice.
      The creature can't regain Hit Points from this feat again until it
      finishes a Short or Long Rest.

- model: character.feat
  pk: lucky
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You have inexplicable luck that seems to kick in at just the right moment.
      You have 3 Luck Points. Whenever you make an attack roll, an ability check,
      or a saving throw, you can spend one Luck Point to roll an additional d20.
      You can choose to spend one of your Luck Points after you roll the die,
      but before the outcome is determined. You choose which of the d20s is used
      for the attack roll, ability check, or saving throw. You can also spend
      one Luck Point when an attack roll is made against you. Roll a d20, and
      then choose whether the attack uses the attacker's roll or yours.
      You regain your expended Luck Points when you finish a Long Rest.

- model: character.feat
  pk: magic_initiate_bard
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You learn two Bard cantrips of your choice. You also learn one 1st-level
      Bard spell of your choice. You can cast this spell without a spell slot
      once per Long Rest. You can also cast it using any spell slots you have.
      Charisma is your spellcasting ability for these spells.

- model: character.feat
  pk: magic_initiate_druid
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You learn two Druid cantrips of your choice. You also learn one 1st-level
      Druid spell of your choice. You can cast this spell without a spell slot
      once per Long Rest. You can also cast it using any spell slots you have.
      Wisdom is your spellcasting ability for these spells.

- model: character.feat
  pk: magic_initiate_sorcerer
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You learn two Sorcerer cantrips of your choice. You also learn one
      1st-level Sorcerer spell of your choice. You can cast this spell without
      a spell slot once per Long Rest. You can also cast it using any spell
      slots you have. Charisma is your spellcasting ability for these spells.

- model: character.feat
  pk: magic_initiate_warlock
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You learn two Warlock cantrips of your choice. You also learn one
      1st-level Warlock spell of your choice. You can cast this spell without
      a spell slot once per Long Rest. You can also cast it using any spell
      slots you have. Charisma is your spellcasting ability for these spells.

- model: character.feat
  pk: musician
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You gain proficiency with three Musical Instruments of your choice.
      Whenever you finish a Short or Long Rest, you can play a song on a
      Musical Instrument you're proficient with. Any friendly creature within
      60 feet of you who hears the performance regains 1 Exhaustion level.

- model: character.feat
  pk: skilled
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      You gain proficiency in any combination of three skills or tools of
      your choice.

- model: character.feat
  pk: tavern_brawler
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      Increase your Strength or Constitution score by 1, to a maximum of 20.
      You are proficient with improvised weapons. Your unarmed strike uses a
      d4 for damage. When you hit a creature with an unarmed strike or an
      improvised weapon on your turn, you can use a Bonus Action to attempt
      to grapple the target.

- model: character.feat
  pk: tough
  fields:
    feat_type: O
    prerequisite: ""
    description: |
      Your Hit Point maximum increases by an amount equal to twice your level
      when you gain this feat. Whenever you gain a level thereafter, your Hit
      Point maximum increases by an additional 2 Hit Points.
```

**Step 3: Run feat model tests**

```bash
doppler run -- uv run pytest character/tests/models/test_feats.py -v
```

Expected: All tests pass (the `test_all_feats_valid` test will now cover new feat names since they're in both constants and fixtures).

**Step 4: Commit**

```bash
git add character/fixtures/feats.yaml
git commit -m "feat: add stub feat fixtures for origin feats referenced by new backgrounds"
```

---

### Task 6: Write new species tests, run full suite, open PR

**Files:**
- Modify: `character/tests/models/test_species.py`

**Step 1: Add tests for new species**

Add a new test class to `character/tests/models/test_species.py`:

```python
@pytest.mark.django_db
class TestNewSRDSpecies:
    """Verify all 5 new SRD 5.2.1 species load from fixtures correctly."""

    def test_all_nine_species_exist(self):
        from character.models.species import Species
        assert Species.objects.count() == 9

    def test_dragonborn_loaded(self):
        from character.models.species import Species
        species = Species.objects.get(name=SpeciesName.DRAGONBORN)
        assert species.size == "M"
        assert species.speed == 30
        assert species.darkvision == 0
        assert species.traits.count() == 3

    def test_gnome_loaded(self):
        from character.models.species import Species
        species = Species.objects.get(name=SpeciesName.GNOME)
        assert species.size == "S"
        assert species.darkvision == 60
        assert species.traits.count() == 2

    def test_goliath_loaded(self):
        from character.models.species import Species
        species = Species.objects.get(name=SpeciesName.GOLIATH)
        assert species.speed == 35
        assert species.traits.count() == 3

    def test_orc_loaded(self):
        from character.models.species import Species
        species = Species.objects.get(name=SpeciesName.ORC)
        assert species.darkvision == 120
        assert species.traits.count() == 2

    def test_tiefling_loaded(self):
        from character.models.species import Species
        species = Species.objects.get(name=SpeciesName.TIEFLING)
        assert species.darkvision == 60
        assert species.traits.count() == 2

    def test_all_species_name_choices_have_fixture(self):
        from character.models.species import Species
        for name, _ in SpeciesName.choices:
            assert Species.objects.filter(name=name).exists(), \
                f"Missing fixture for species: {name}"
```

**Step 2: Run full test suite**

```bash
doppler run -- uv run poe test
```

Expected: All tests pass.

**Step 3: Run pre-commit**

```bash
pre-commit run --all-files
```

Fix any issues.

**Step 4: Update CHANGELOG.md**

Add under `## Unreleased` → `### Added`:
```
- Species: Dragonborn, Gnome, Goliath, Orc, Tiefling (SRD 5.2.1)
- Backgrounds: Artisan, Charlatan, Entertainer, Farmer, Guard, Guide, Hermit, Merchant, Noble, Pilgrim, Sailor, Scribe, Wayfarer (SRD 5.2.1)
- Stub origin feats: Crafter, Healer, Lucky, Magic Initiate (Bard/Druid/Sorcerer/Warlock), Musician, Skilled, Tavern Brawler, Tough
```

**Step 5: Commit and push**

```bash
git add character/tests/models/test_species.py CHANGELOG.md
git commit -m "test: verify new SRD species fixtures load correctly"
git push -u origin feat/srd-species-backgrounds
```

**Step 6: Open PR**

```bash
gh pr create --title "feat: add SRD 5.2.1 species and backgrounds" --body "$(cat <<'EOF'
## Summary
- Adds 5 new species: Dragonborn, Gnome, Goliath, Orc, Tiefling
- Adds 13 new backgrounds: Artisan, Charlatan, Entertainer, Farmer, Guard, Guide, Hermit, Merchant, Noble, Pilgrim, Sailor, Scribe, Wayfarer
- Adds stub origin feats (full descriptions in follow-up PR)

## Test plan
- [ ] All species tests pass
- [ ] `test_all_species_name_choices_have_fixture` confirms 9 species loaded
- [ ] Full test suite passes
- [ ] Pre-commit passes
EOF
)"
```

---

## PR 2: Feats

Branch: `feat/srd-feats`

---

### Task 7: Create branch and add general feat constants

**Step 1: Create branch**

```bash
git checkout main && git pull && git checkout -b feat/srd-feats
```

**Step 2: Add general FeatName entries to `character/constants/feats.py`**

Append after the origin feats (already have ALERT, CRAFTER, HEALER, LUCKY, MAGIC_INITIATE_*, MUSICIAN, SAVAGE_ATTACKER, SKILLED, TAVERN_BRAWLER, TOUGH from PR 1):

```python
    # General feats (4th level+)
    ABILITY_SCORE_IMPROVEMENT = "ability_score_improvement", "Ability Score Improvement"
    ACTOR = "actor", "Actor"
    ATHLETE = "athlete", "Athlete"
    CHARGER = "charger", "Charger"
    CHEF = "chef", "Chef"
    CROSSBOW_EXPERT = "crossbow_expert", "Crossbow Expert"
    CRUSHER = "crusher", "Crusher"
    DEFENSIVE_DUELIST = "defensive_duelist", "Defensive Duelist"
    DUAL_WIELDER = "dual_wielder", "Dual Wielder"
    DURABLE = "durable", "Durable"
    ELEMENTAL_ADEPT = "elemental_adept", "Elemental Adept"
    FEY_TOUCHED = "fey_touched", "Fey-Touched"
    GREAT_WEAPON_MASTER = "great_weapon_master", "Great Weapon Master"
    GRAPPLER = "grappler", "Grappler"
    HEAVY_ARMOR_MASTER = "heavy_armor_master", "Heavy Armor Master"
    INSPIRING_LEADER = "inspiring_leader", "Inspiring Leader"
    MAGE_SLAYER = "mage_slayer", "Mage Slayer"
    MOUNTED_COMBATANT = "mounted_combatant", "Mounted Combatant"
    OBSERVANT = "observant", "Observant"
    POLEARM_MASTER = "polearm_master", "Polearm Master"
    RESILIENT = "resilient", "Resilient"
    SENTINEL = "sentinel", "Sentinel"
    SHADOW_TOUCHED = "shadow_touched", "Shadow-Touched"
    SHARPSHOOTER = "sharpshooter", "Sharpshooter"
    SHIELD_MASTER = "shield_master", "Shield Master"
    SKULKER = "skulker", "Skulker"
    SLASHER = "slasher", "Slasher"
    SPELL_SNIPER = "spell_sniper", "Spell Sniper"
    WAR_CASTER = "war_caster", "War Caster"
    WEAPON_MASTER = "weapon_master", "Weapon Master"
```

**Step 3: Run feat tests**

```bash
doppler run -- uv run pytest character/tests/models/test_feats.py -v
```

Expected: All pass (no fixtures yet, `test_all_feats_valid` uses factories and won't fail on missing fixtures).

**Step 4: Commit**

```bash
git add character/constants/feats.py
git commit -m "feat: add general feat constants for SRD 5.2.1"
```

---

### Task 8: Add general feat fixtures

**Files:**
- Modify: `character/fixtures/feats.yaml`

**Step 1: Append general feat entries**

Add one entry per feat. Source descriptions verbatim from SRD 5.2.1. Example entries:

```yaml
- model: character.feat
  pk: ability_score_improvement
  fields:
    feat_type: G
    prerequisite: "Level 4+"
    description: |
      Increase one ability score of your choice by 2, or increase two ability
      scores of your choice by 1 each. This feat can be taken multiple times.

- model: character.feat
  pk: actor
  fields:
    feat_type: G
    prerequisite: "Charisma 13+"
    description: |
      Increase your Charisma score by 1, to a maximum of 20.
      You have an Expertise in the Performance skill.
      You can also mimic the speech of another person or sounds made by other
      creatures. You must have heard the person speak, or heard the creature
      make the sound, for at least 1 minute. A successful Wisdom (Insight)
      check contested by your Charisma (Performance) check allows a listener
      to determine that the effect is faked.

- model: character.feat
  pk: war_caster
  fields:
    feat_type: G
    prerequisite: "Spellcasting or Pact Magic feature"
    description: |
      You have practiced casting spells in the midst of combat, learning
      techniques that grant you the following benefits.
      Concentration: You have Advantage on Constitution saving throws that
      you make to maintain Concentration.
      Reactive Spell: When a creature provokes an Opportunity Attack from you,
      you can use your Reaction to cast a spell at the creature, rather than
      making an Opportunity Attack. The spell must have a casting time of one
      action and must target only that creature.
      Somatic Components: You can perform the Somatic components of spells
      even when you have weapons or a Shield in one or both hands.
```

Add all remaining feats following this exact pattern. Every feat needs pk (matching FeatName value), feat_type (O or G), prerequisite (empty string if none), and description (from SRD 5.2.1).

**Step 2: Commit**

```bash
git add character/fixtures/feats.yaml
git commit -m "feat: add general feat fixtures for SRD 5.2.1"
```

---

### Task 9: Write feat tests, full suite, open PR

**Files:**
- Modify: `character/tests/models/test_feats.py`

**Step 1: Add fixture coverage test**

```python
@pytest.mark.django_db
class TestSRDFeatCompleteness:
    def test_all_feat_names_have_fixture(self):
        from character.models.feats import Feat
        for name, _ in FeatName.choices:
            assert Feat.objects.filter(name=name).exists(), \
                f"Missing fixture for feat: {name}"

    def test_origin_feat_count(self):
        from character.models.feats import Feat
        origin_count = Feat.objects.filter(feat_type=FeatType.ORIGIN).count()
        assert origin_count >= 15  # 4 existing + 11 new

    def test_general_feat_count(self):
        from character.models.feats import Feat
        general_count = Feat.objects.filter(feat_type=FeatType.GENERAL).count()
        assert general_count >= 25
```

**Step 2: Run full suite, pre-commit, update CHANGELOG, push, open PR**

```bash
doppler run -- uv run poe test
pre-commit run --all-files
```

Add to CHANGELOG `### Added`: `- Feats: complete SRD 5.2.1 origin and general feat list (~35 feats)`

```bash
git add character/tests/models/test_feats.py CHANGELOG.md
git commit -m "test: verify SRD feat completeness"
git push -u origin feat/srd-feats
gh pr create --title "feat: add complete SRD 5.2.1 feat list" --body "$(cat <<'EOF'
## Summary
- Adds ~25 general feats to constants and fixtures
- Completes stub origin feats added in PR 1 with full descriptions
- All FeatName choices covered by fixture entries

## Test plan
- [ ] `test_all_feat_names_have_fixture` passes
- [ ] Origin feat count >= 15, general feat count >= 25
- [ ] Full test suite passes
- [ ] Pre-commit passes
EOF
)"
```

---

## PR 3: Spells

Branch: `feat/srd-spells`

---

### Task 10: Create branch

```bash
git checkout main && git pull && git checkout -b feat/srd-spells
```

---

### Task 11: Add cantrips

**Files:**
- Modify: `magic/fixtures/spells.yaml`

**Step 1: Append ~20 cantrip entries**

Follow the exact structure of existing entries. Key cantrips to add:

| Spell | School | Classes |
|-------|--------|---------|
| Blade Ward | abjuration | bard, sorcerer, warlock, wizard |
| Chill Touch | necromancy | sorcerer, warlock, wizard |
| Dancing Lights | illusion | bard, sorcerer, wizard |
| Eldritch Blast | evocation | warlock |
| Friends | enchantment | bard, sorcerer, warlock, wizard |
| Guidance | divination | cleric, druid |
| Mending | transmutation | bard, cleric, druid, sorcerer, wizard |
| Message | transmutation | bard, sorcerer, wizard |
| Minor Illusion | illusion | bard, sorcerer, warlock, wizard |
| Poison Spray | conjuration | druid, sorcerer, warlock, wizard |
| Ray of Frost | evocation | sorcerer, wizard |
| Resistance | abjuration | cleric, druid |
| Sacred Flame | radiant | cleric |
| Shillelagh | transmutation | druid |
| Shocking Grasp | evocation | sorcerer, wizard |
| Spare the Dying | necromancy | cleric, druid |
| Thaumaturgy | transmutation | cleric |
| Toll the Dead | necromancy | cleric, warlock, wizard |
| True Strike | divination | bard, sorcerer, warlock, wizard |
| Vicious Mockery | enchantment | bard |

Example entry format:
```yaml
- model: magic.spellsettings
  fields:
    name: Eldritch Blast
    level: 0
    school: evocation
    casting_time: action
    range: 120_feet
    components: ["V", "S"]
    duration: instantaneous
    concentration: false
    ritual: false
    description: >
      A beam of crackling energy streaks toward a creature within range. Make a
      ranged spell attack against the target. On a hit, the target takes 1d10
      force damage. The spell creates more than one beam when you reach higher
      levels — two beams at 5th level, three beams at 11th level, and four
      beams at 17th level. You can direct the beams at the same target or at
      different ones. Make a separate attack roll for each beam.
    classes: ["warlock"]
```

Note: `SpellRange` choices already cover all needed values. Check `magic/constants/spells.py` before writing — if a range like `UNLIMITED` or `SPECIAL` is needed, add it first.

**Step 2: Commit**

```bash
git add magic/fixtures/spells.yaml
git commit -m "feat: add SRD cantrips (20 new)"
```

---

### Task 12: Add level 1 spells

**Files:**
- Modify: `magic/fixtures/spells.yaml`

**Step 1: Append ~20 level 1 spell entries**

Key level 1 spells (verify each against SRD 5.2.1):

| Spell | School | Conc | Key classes |
|-------|--------|------|-------------|
| Alarm | abjuration | N | ranger, wizard |
| Animal Friendship | enchantment | N | bard, druid, ranger |
| Bane | enchantment | Y | bard, cleric |
| Bless | enchantment | Y | cleric, paladin |
| Burning Hands | evocation | N | sorcerer, wizard |
| Charm Person | enchantment | N | bard, druid, sorcerer, warlock, wizard |
| Command | enchantment | N | cleric, paladin |
| Detect Magic | divination | Y | bard, cleric, druid, paladin, ranger, sorcerer, wizard |
| Entangle | conjuration | Y | druid |
| Faerie Fire | evocation | Y | bard, druid |
| False Life | necromancy | N | sorcerer, wizard |
| Feather Fall | transmutation | N | bard, sorcerer, wizard |
| Fog Cloud | conjuration | Y | druid, ranger, sorcerer, wizard |
| Goodberry | transmutation | N | druid, ranger |
| Healing Word | evocation | N | bard, cleric, druid |
| Heroism | enchantment | Y | bard, paladin |
| Hunter's Mark | divination | Y | ranger |
| Inflict Wounds | necromancy | N | cleric |
| Magic Missile | evocation | N | sorcerer, wizard (exists — skip) |
| Protection from Evil and Good | abjuration | Y | cleric, paladin, warlock, wizard |
| Sanctuary | abjuration | N | cleric |
| Silent Image | illusion | Y | bard, sorcerer, wizard |
| Sleep | enchantment | N | bard, sorcerer, wizard (exists — skip) |
| Thunderwave | evocation | N | bard, druid, sorcerer, wizard |
| Unseen Servant | conjuration | N | bard, warlock, wizard |
| Witch Bolt | evocation | Y | sorcerer, warlock, wizard |

**Step 2: Commit**

```bash
git add magic/fixtures/spells.yaml
git commit -m "feat: add SRD level 1 spells (~24 new)"
```

---

### Task 13: Add level 2 spells

**Files:**
- Modify: `magic/fixtures/spells.yaml`

**Step 1: Append ~18 level 2 spell entries**

Key level 2 spells:

| Spell | School | Conc | Key classes |
|-------|--------|------|-------------|
| Aid | abjuration | N | cleric, paladin |
| Arcane Lock | abjuration | N | wizard |
| Blindness/Deafness | necromancy | N | bard, cleric, sorcerer, wizard |
| Blur | illusion | Y | sorcerer, wizard |
| Calm Emotions | enchantment | Y | bard, cleric |
| Darkness | evocation | Y | sorcerer, warlock, wizard |
| Darkvision | transmutation | N | druid, ranger, sorcerer, wizard |
| Enhance Ability | transmutation | Y | bard, cleric, druid, sorcerer, wizard |
| Enlarge/Reduce | transmutation | Y | druid, sorcerer, wizard |
| Flaming Sphere | conjuration | Y | druid, wizard |
| Heat Metal | transmutation | Y | bard, druid |
| Invisibility | illusion | Y | bard, sorcerer, warlock, wizard (exists — skip) |
| Knock | transmutation | N | bard, sorcerer, wizard |
| Lesser Restoration | abjuration | N | bard, cleric, druid, paladin, ranger |
| Levitate | transmutation | Y | sorcerer, wizard |
| Mirror Image | illusion | N | sorcerer, warlock, wizard |
| Misty Step | conjuration | N | sorcerer, warlock, wizard (exists — skip) |
| Moonbeam | evocation | Y | druid |
| Pass without Trace | abjuration | Y | druid, ranger |
| Prayer of Healing | evocation | N | cleric, paladin |
| Ray of Enfeeblement | necromancy | Y | warlock, wizard |
| See Invisibility | divination | N | bard, sorcerer, wizard |
| Silence | illusion | Y | bard, cleric, ranger |
| Spider Climb | transmutation | Y | druid, ranger, sorcerer, warlock, wizard |
| Spiritual Weapon | evocation | N | cleric |
| Suggestion | enchantment | Y | bard, sorcerer, warlock, wizard |
| Web | conjuration | Y | sorcerer, wizard |
| Zone of Truth | enchantment | N | bard, cleric, paladin |

**Step 2: Commit**

```bash
git add magic/fixtures/spells.yaml
git commit -m "feat: add SRD level 2 spells (~26 new)"
```

---

### Task 14: Add levels 3–5 spells

**Files:**
- Modify: `magic/fixtures/spells.yaml`

**Step 1: Append level 3 spell entries (~15 new)**

Key level 3 spells (skip Counterspell, Fly — already exist):

Animate Dead, Bestow Curse, Blink, Call Lightning, Clairvoyance, Conjure Animals, Daylight, Dispel Magic, Fear, Gaseous Form, Haste, Hypnotic Pattern, Lightning Bolt, Mass Healing Word, Nondetection, Plant Growth, Protection from Energy, Remove Curse, Revivify, Sending, Sleet Storm, Slow, Speak with Dead, Spirit Guardians, Stinking Cloud, Tongues, Vampiric Touch, Water Breathing, Wind Wall

**Step 2: Append level 4 spell entries (~12 new)**

Arcane Eye, Banishment, Blight, Compulsion, Confusion, Death Ward, Dimension Door, Dominate Beast, Freedom of Movement, Greater Invisibility, Guardian of Faith, Ice Storm, Phantasmal Killer, Polymorph, Stoneskin, Wall of Fire (skip — exists)

**Step 3: Append level 5 spell entries (~12 new)**

Animate Objects, Cloudkill, Commune, Cone of Cold, Conjure Elemental, Contact Other Plane, Contagion, Dominate Person, Dream, Geas, Greater Restoration, Hold Monster, Insect Plague, Legend Lore, Mass Cure Wounds, Mislead, Modify Memory, Raise Dead, Scrying, Telekinesis, Teleportation Circle, Wall of Force, Wall of Stone

**Step 4: Commit each level separately**

```bash
git add magic/fixtures/spells.yaml
git commit -m "feat: add SRD level 3 spells"
# add level 4
git commit -m "feat: add SRD level 4 spells"
# add level 5
git commit -m "feat: add SRD level 5 spells"
```

---

### Task 15: Write spell tests, full suite, open PR

**Files:**
- Modify: `magic/tests/models/test_spells.py`

**Step 1: Add fixture coverage tests**

```python
@pytest.mark.django_db
class TestSRDSpellCompleteness:
    def test_total_spell_count(self):
        from magic.models.spells import SpellSettings
        assert SpellSettings.objects.count() >= 100

    def test_cantrip_count(self):
        from magic.models.spells import SpellSettings
        assert SpellSettings.objects.filter(level=0).count() >= 22

    def test_each_class_has_spells(self):
        from magic.models.spells import SpellSettings
        classes = ["barbarian", "bard", "cleric", "druid", "fighter",
                   "monk", "paladin", "ranger", "rogue", "sorcerer",
                   "warlock", "wizard"]
        for cls in classes:
            count = SpellSettings.objects.filter(classes__contains=[cls]).count()
            assert count >= 1, f"No spells found for class: {cls}"

    def test_all_spell_schools_represented(self):
        from magic.models.spells import SpellSettings
        from magic.constants.spells import SpellSchool
        for school, _ in SpellSchool.choices:
            assert SpellSettings.objects.filter(school=school).exists(), \
                f"No spells for school: {school}"
```

**Step 2: Run full suite, pre-commit, update CHANGELOG, push, open PR**

```bash
doppler run -- uv run poe test
pre-commit run --all-files
```

Add to CHANGELOG `### Added`: `- Spells: ~90 new SRD 5.2.1 spells (cantrips through level 5) covering all 12 classes`

```bash
git add magic/tests/models/test_spells.py CHANGELOG.md
git commit -m "test: verify SRD spell completeness"
git push -u origin feat/srd-spells
gh pr create --title "feat: add SRD 5.2.1 representative spell set (~100 spells)" --body "$(cat <<'EOF'
## Summary
- Adds ~90 new spells across cantrips and levels 1–5
- All 12 classes have spell options
- All 8 schools of magic represented

## Test plan
- [ ] Total spell count >= 100
- [ ] Each class has at least 1 spell
- [ ] All schools represented
- [ ] Full test suite passes
- [ ] Pre-commit passes
EOF
)"
```

---

## PR 4: Monsters

Branch: `feat/srd-monsters`

---

### Task 16: Create branch

```bash
git checkout main && git pull && git checkout -b feat/srd-monsters
```

---

### Task 17: Add beast and humanoid monsters

**Files:**
- Modify: `bestiary/fixtures/monsters.yaml`
- Modify: `bestiary/fixtures/monster_attributes.yaml`

**Step 1: Understand the attribute fixture structure**

```bash
head -60 bestiary/fixtures/monster_attributes.yaml
```

The attributes fixture has separate entries for each attribute type (speed, senses, saving_throws, skills, damage_relations, actions, traits, etc.) linked to the monster by name PK.

**Step 2: Add ~15 beast entries to `monsters.yaml`**

Key beasts (all CR ≤ 1): Ape (CR 1/2), Bat (CR 0), Black Bear (CR 1/2), Boar (CR 1/4), Brown Bear (CR 1), Cat (CR 0), Constrictor Snake (CR 1/4), Crocodile (CR 1/2), Hawk (CR 0), Lion (CR 1), Mastiff (CR 1/8), Poisonous Snake (CR 1/8), Rat (CR 0), Raven (CR 0), Riding Horse (CR 1/4), Tiger (CR 1), Warhorse (CR 1/2), Wolf (skip — exists)

Example entry:
```yaml
- model: bestiary.monstersettings
  fields:
    name: Lion
    size: large
    creature_type: beast
    subtype: ""
    alignment: U
    ac: 12
    ac_type: ""
    hit_dice: "4d10+8"
    hp_average: 26
    passive_perception: 13
    strength: 17
    dexterity: 15
    constitution: 13
    intelligence: 3
    wisdom: 12
    charisma: 8
    telepathy: 0
    challenge_rating: "1"
    proficiency_bonus: 2
    legendary_action_count: 0
    has_lair: false
    description: ""
```

**Step 3: Add corresponding monster_attributes entries**

For each new monster, add at minimum: walk speed, any special senses, and primary actions. Example:

```yaml
# Lion attributes
- model: bestiary.monsterspeed
  fields:
    monster: Lion
    movement_type: walk
    speed: 50

- model: bestiary.monsteraction
  fields:
    monster: Lion
    name: Bite
    action_type: melee_weapon
    description: >
      Melee Weapon Attack: +5 to hit, reach 5 ft., one target.
      Hit: 7 (1d8 + 3) piercing damage.
    attack_bonus: 5
    reach: 5
    range_normal: 0
    range_long: 0
    hit_dice: "1d8"
    hit_modifier: 3
    damage_type: piercing
    save_type: none
    save_dc: 0
    save_effect: none
    area_shape: none
    area_size: 0
    recharge: none
    targets: 1

- model: bestiary.monsteraction
  fields:
    monster: Lion
    name: Claw
    action_type: melee_weapon
    description: >
      Melee Weapon Attack: +5 to hit, reach 5 ft., one target.
      Hit: 6 (1d6 + 3) slashing damage.
    attack_bonus: 5
    reach: 5
    range_normal: 0
    range_long: 0
    hit_dice: "1d6"
    hit_modifier: 3
    damage_type: slashing
    save_type: none
    save_dc: 0
    save_effect: none
    area_shape: none
    area_size: 0
    recharge: none
    targets: 1
```

**Step 4: Add ~12 humanoid entries**

Key humanoids: Acolyte (CR 1/4), Bandit Captain (CR 2), Berserker (CR 2), Cultist (CR 1/8), Cult Fanatic (CR 2), Gladiator (CR 5), Guard (CR 1/8), Knight (CR 3), Noble (CR 1/8), Priest (CR 2), Scout (CR 1/2), Spy (CR 1), Thug (CR 1/2), Tribal Warrior (CR 1/8), Veteran (CR 3)

**Step 5: Commit**

```bash
git add bestiary/fixtures/monsters.yaml bestiary/fixtures/monster_attributes.yaml
git commit -m "feat: add SRD beast and humanoid monsters"
```

---

### Task 18: Add undead, fiend, and elemental monsters

**Files:**
- Modify: `bestiary/fixtures/monsters.yaml`
- Modify: `bestiary/fixtures/monster_attributes.yaml`

**Step 1: Add undead monsters (~6 new)**

Specter (CR 1), Wight (CR 3), Wraith (CR 5), Ghost (CR 4), Vampire (CR 13), Mummy (CR 3), Mummy Lord (CR 15)

Note: Zombie and Skeleton (CR 1/4) and Ghoul (CR 1) already exist.

**Step 2: Add fiend monsters (~6 new)**

Imp (CR 1), Quasit (CR 1), Dretch (CR 1/4), Bearded Devil (CR 3), Barbed Devil (CR 5), Erinyes (CR 12), Balor (CR 19), Vrock (CR 6)

**Step 3: Add remaining elementals (3 new)**

Earth Elemental (CR 5), Fire Elemental (CR 5), Water Elemental (CR 5)
Note: Air Elemental already exists.

**Step 4: Commit**

```bash
git add bestiary/fixtures/monsters.yaml bestiary/fixtures/monster_attributes.yaml
git commit -m "feat: add SRD undead, fiend, and elemental monsters"
```

---

### Task 19: Add dragons

**Files:**
- Modify: `bestiary/fixtures/monsters.yaml`
- Modify: `bestiary/fixtures/monster_attributes.yaml`

**Step 1: Add all remaining dragon entries (~17 new)**

Adult Red Dragon already exists. Add:

| Stage | Colours |
|-------|---------|
| Wyrmling (CR 2–4) | Black, Blue, Green, Red, White |
| Young (CR 7–10) | Black, Blue, Green, Red, White |
| Adult (CR 11–17) | Black, Blue, Green, White (Red exists) |
| Ancient (CR 20–24) | Black, Blue, Green, Red, White |

Each dragon has: Bite, Claw, Tail actions + Breath Weapon (recharge 5-6) + Frightful Presence (adult+) + Legendary Actions (adult+).

Commit after every 5 dragons to keep commits small:

```bash
git add bestiary/fixtures/monsters.yaml bestiary/fixtures/monster_attributes.yaml
git commit -m "feat: add SRD dragon wyrmlings"
# add young dragons
git commit -m "feat: add SRD young dragons"
# add remaining adults + ancients
git commit -m "feat: add SRD adult and ancient dragons"
```

---

### Task 20: Add giants, monstrosities, and remaining types

**Files:**
- Modify: `bestiary/fixtures/monsters.yaml`
- Modify: `bestiary/fixtures/monster_attributes.yaml`

**Step 1: Giants (~6 new)**

Hill Giant (CR 5), Stone Giant (CR 7), Frost Giant (CR 8), Fire Giant (CR 9), Cloud Giant (CR 9), Storm Giant (CR 13)

**Step 2: Monstrosities (~8 new)**

Basilisk (CR 3), Griffon (CR 2), Harpy (CR 1), Hydra (CR 8), Medusa (CR 6), Phase Spider (CR 3), Roc (CR 11), Winter Wolf (CR 3)
Note: Minotaur and Owlbear already exist.

**Step 3: Remaining types**

- Constructs: Stone Golem (CR 10) — Animated Armor not in existing set, add it (CR 1)
- Oozes: Gelatinous Cube (CR 2), Black Pudding (CR 4)
- Aberrations: Aboleth (CR 10)
- Celestials: Couatl (CR 4)
- Plants: Treant (CR 9), Shambling Mound (CR 5)

**Step 4: Commit by type**

```bash
git commit -m "feat: add SRD giant monsters"
git commit -m "feat: add SRD monstrosity monsters"
git commit -m "feat: add SRD construct, ooze, aberration, celestial, plant monsters"
```

---

### Task 21: Write monster tests, full suite, open PR

**Files:**
- Modify: `bestiary/tests/models/` (check existing test files)

**Step 1: Find existing monster tests**

```bash
ls bestiary/tests/models/
```

**Step 2: Add completeness tests**

```python
@pytest.mark.django_db
class TestSRDMonsterCompleteness:
    def test_total_monster_count(self):
        from bestiary.models.monsters import MonsterSettings
        assert MonsterSettings.objects.count() >= 100

    def test_all_creature_types_represented(self):
        from bestiary.models.monsters import MonsterSettings
        from bestiary.constants.monsters import CreatureType
        for creature_type, _ in CreatureType.choices:
            assert MonsterSettings.objects.filter(
                creature_type=creature_type
            ).exists(), f"No monsters for type: {creature_type}"

    def test_cr_range_represented(self):
        from bestiary.models.monsters import MonsterSettings
        low_cr = MonsterSettings.objects.filter(
            challenge_rating__in=["0", "1/8", "1/4", "1/2"]
        ).count()
        mid_cr = MonsterSettings.objects.filter(
            challenge_rating__in=["1", "2", "3", "4", "5"]
        ).count()
        high_cr = MonsterSettings.objects.filter(
            challenge_rating__in=["10", "15", "20"]
        ).count()
        assert low_cr >= 5
        assert mid_cr >= 10
        assert high_cr >= 3

    def test_dragons_have_breath_weapons(self):
        from bestiary.models.monsters import MonsterSettings, MonsterAction
        dragons = MonsterSettings.objects.filter(creature_type="dragon")
        assert dragons.count() >= 17
        for dragon in dragons:
            breath = MonsterAction.objects.filter(
                monster=dragon, recharge__in=["5-6", "6"]
            )
            # Wyrmlings and above should have breath weapons
            assert breath.exists(), f"{dragon.name} missing breath weapon"
```

**Step 3: Run full suite, pre-commit, update CHANGELOG, push, open PR**

```bash
doppler run -- uv run poe test
pre-commit run --all-files
```

Add to CHANGELOG `### Added`: `- Monsters: ~83 new SRD 5.2.1 monsters covering all 14 creature types and CR 0–24`

```bash
git add bestiary/tests/ CHANGELOG.md
git commit -m "test: verify SRD monster completeness"
git push -u origin feat/srd-monsters
gh pr create --title "feat: add SRD 5.2.1 monster set (~100 monsters)" --body "$(cat <<'EOF'
## Summary
- Adds ~83 new monsters from SRD 5.2.1
- All 14 creature types represented
- CR range 0–24 covered
- All dragons: 5 colours × 4 age stages (wyrmling/young/adult/ancient)

## Test plan
- [ ] Total monster count >= 100
- [ ] All creature types represented
- [ ] Low/mid/high CR ranges covered
- [ ] All dragons have breath weapons
- [ ] Full test suite passes
- [ ] Pre-commit passes
EOF
)"
```

---

## Important Notes for All PRs

**Running tests:** Always use `doppler run -- uv run poe test` (never bare pytest — environment secrets required).

**New fixture files:** If you add a new fixture file (e.g. a separate `backgrounds.yaml`), add it to the `FIXTURES` list in `conftest.py` in the correct dependency order.

**Language PKs:** The `languages.yaml` file uses integer PKs. Check the existing entries before adding new ones to avoid PK conflicts.

**SRD source:** All descriptions must be sourced from the D&D 5.2.1 Systems Reference Document, which is CC-BY-4.0 licensed. Do not copy from the PHB or other non-SRD sources.

**Checking existing fixture data:** Before adding any entry, grep to confirm it doesn't already exist:
```bash
grep "name: <SpellName>" magic/fixtures/spells.yaml
grep "name: <MonsterName>" bestiary/fixtures/monsters.yaml
```
