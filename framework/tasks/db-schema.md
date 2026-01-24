# Task: DB Schema + RLS

## Goal
Define the database schema and migrations with RLS.

## Inputs
- framework/docs/orchestrator-plan-ru.md (section 1.3)
- framework/docs/definition-of-done-ru.md

## Outputs
- Migration files or SQL snippets
- Short summary of changes

## Constraints
- Include project_id in all tables
- Use versioning fields (version, is_current)
- Do not overwrite existing data

## Done When
- Schema and RLS rules are documented
- Migrations are ready to apply
