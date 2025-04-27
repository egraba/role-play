# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- Run server: `uv run invoke dev.run`
- Run tests: `uv run invoke test.run`
- Single test: `uv run invoke test.run --test-label=path/to/test_file.py::TestClass::test_method`
- Coverage: `uv run invoke test.run --coverage && uv run invoke test.coverage-report`
- DB migration: `uv run invoke db.migrate`
- Reset DB: `uv run invoke db.reset`

## Lint/Format Commands
- Check code style: `pre-commit run --all-files`
- Lint Python: `ruff check`
- Format code: `ruff format`
- Type check: `mypy`

## Code Style Guidelines
- Imports: stdlib first, third-party second, project modules last, alphabetically within groups
- Use absolute imports for external modules, relative imports for internal modules
- Naming: PascalCase for classes, snake_case for functions/variables, UPPER_SNAKE_CASE for constants
- Type hints: Use for all function parameters and return values
- Error handling: Define custom exceptions in exceptions.py, use Django's model validation
- Django: Organize models by domain in subdirectories, constants in enum-like classes
- Tests: Pytest with Django plugin, follow test_ naming convention, use factory pattern
