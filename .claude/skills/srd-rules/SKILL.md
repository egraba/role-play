---
name: srd-rules
description: >
  Load when implementing any D&D game mechanic: attack rolls, damage, saving throws,
  ability checks, spell casting, conditions, initiative, action economy, proficiency
  bonus, or any other SRD 5.2.1 rule. Ensures consistent and correct rule implementation.
user-invocable: false
---

# SRD 5.2.1 Rules Reference

## Ability Scores & Modifiers

- 6 abilities: STR, DEX, CON, INT, WIS, CHA
- Modifier = `(score - 10) // 2` (floor division)
- Scores 8–15 available at character creation (point buy)

## Proficiency Bonus

| Levels | Bonus |
|--------|-------|
| 1–4    | +2    |
| 5–8    | +3    |
| 9–12   | +4    |
| 13–16  | +5    |
| 17–20  | +6    |

## Ability Checks

- Roll: `d20 + ability_modifier (+ proficiency_bonus if proficient)`
- Difficulty Classes: Very Easy 5 / Easy 10 / Medium 15 / Hard 20 / Very Hard 25 / Nearly Impossible 30
- Meet or beat DC = success

## Saving Throws

- Roll: `d20 + ability_modifier (+ proficiency_bonus if proficient in that save)`
- Triggered by spells, traps, hazards
- Common: CON save vs concentration, DEX save vs area effects, WIS save vs charm/fear

## Attack Rolls

- Roll: `d20 + ability_modifier + proficiency_bonus (if proficient with weapon)`
- Melee: usually STR modifier; Finesse weapons can use DEX
- Ranged: usually DEX modifier
- Spell attacks: spellcasting ability modifier + proficiency_bonus
- Compare to **target AC** — meet or beat = hit

### Critical Hit (Natural 20)
- Automatic hit regardless of AC
- Roll damage dice **twice**, then add modifiers once
- e.g., `2d6 + STR_mod` becomes `4d6 + STR_mod`

### Critical Miss (Natural 1)
- Automatic miss regardless of modifiers

## Damage

- On hit: `damage_dice + ability_modifier`
- Damage types: Bludgeoning, Piercing, Slashing (physical); Acid, Cold, Fire, Force,
  Lightning, Necrotic, Poison, Psychic, Radiant, Thunder (elemental/magical)
- Resistance: half damage; Immunity: no damage; Vulnerability: double damage

## Action Economy (per turn)

| Type         | Count | Examples |
|--------------|-------|---------|
| Action       | 1     | Attack, Cast Spell, Dash, Disengage, Dodge, Help, Hide, Ready, Search, Use Object |
| Bonus Action | 1     | Class features, some spells, off-hand attack |
| Reaction     | 1     | Opportunity attack, some spells (e.g., Shield) |
| Movement     | Speed | Up to speed in feet |

## Initiative

- At combat start: everyone rolls `d20 + DEX_modifier`
- Highest goes first; ties broken by DM discretion
- Surprised creatures skip their first turn

## Spellcasting

- **Spell save DC** = `8 + proficiency_bonus + spellcasting_ability_modifier`
- **Spell attack bonus** = `proficiency_bonus + spellcasting_ability_modifier`
- Spellcasting abilities by class:
  - INT: Wizard
  - WIS: Cleric, Druid, Ranger
  - CHA: Bard, Paladin, Sorcerer, Warlock

### Spell Slots
- Slots are spent to cast spells; higher-slot casting can upcast
- Cantrips cost no slots
- Concentration spells: only one at a time; broken by taking damage (CON save DC = 10 or half damage, whichever is higher)

## Conditions

| Condition    | Key Effect |
|-------------|-----------|
| Blinded      | Auto-fail sight checks; attacks against = advantage; own attacks = disadvantage |
| Charmed      | Can't attack charmer; charmer has advantage on social checks |
| Deafened     | Auto-fail hearing checks |
| Exhaustion   | 6 levels; each adds cumulative penalties; level 6 = death |
| Frightened   | Disadvantage on checks/attacks while source is visible; can't move closer |
| Grappled     | Speed = 0 |
| Incapacitated| Can't take actions or reactions |
| Invisible    | Attacks against = disadvantage; own attacks = advantage |
| Paralyzed    | Incapacitated + can't move/speak; attacks against = advantage; melee hits = critical |
| Petrified    | Transformed to stone; incapacitated; resistance to all damage |
| Poisoned     | Disadvantage on attack rolls and ability checks |
| Prone        | Can only crawl; attacks against = advantage if attacker within 5 ft, else disadvantage |
| Restrained   | Speed = 0; attacks against = advantage; own attacks = disadvantage |
| Stunned      | Incapacitated; attacks against = advantage |
| Unconscious  | Incapacitated + prone; attacks against = advantage; melee hits = critical |

## Death Saving Throws

- At 0 HP: roll d20 each turn (no modifiers)
- 10+: success; below 10: failure
- 3 successes: stable; 3 failures: dead
- Natural 20: regain 1 HP; Natural 1: counts as 2 failures

## Weapon Mastery (SRD 5.2.1)

Each weapon has a mastery property usable once per turn if proficient:
- **Cleave**: On hit, attack another creature within reach (no bonus to attack)
- **Graze**: On a miss, deal STR or DEX modifier as damage (minimum 0)
- **Nick**: Off-hand attack as part of the Attack action (not bonus action)
- **Push**: On hit, push target up to 10 ft away
- **Sap**: On hit, target has disadvantage on next attack roll
- **Slow**: On hit, target's speed -10 ft until start of your next turn
- **Topple**: On hit, target makes CON save (DC = spell save DC) or falls prone
- **Vex**: On hit, you have advantage on next attack roll against that target

## Classes in This Codebase

Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard
