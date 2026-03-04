---
name: new-migration
description: Create a new Django database migration for the role-play project
disable-model-invocation: true
---

# Create Django Migration

## 1. Generate the migration

```bash
doppler run -- uv run poe db-make-migrations
```

Review the generated file in the relevant app's `migrations/` directory.

## 2. Migration checklist

- [ ] Field types and constraints match the model
- [ ] `default=` provided for new non-nullable fields (required for zero-downtime deploy)
- [ ] No `RunPython` data migrations left as placeholders
- [ ] If adding/removing fixtures fields: update the YAML fixture file in `<app>/fixtures/`
- [ ] Migration name is descriptive (rename if Django auto-generated a vague name)
- [ ] No circular dependency in `dependencies = [...]`

## 3. Apply locally

```bash
doppler run -- uv run poe db-migrate
```

## 4. Update CHANGELOG.md

Add under `## Unreleased` → `### Changed`:
```
- Add/alter `<ModelName>` — description of what changed
```

## 5. Verify

```bash
doppler run -- uv run poe test
```
