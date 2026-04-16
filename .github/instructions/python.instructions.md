---
applyTo: "**/*.py"
---

# Python Conventions

## Style

- Python 3.13+ with type hints
- Use `pydantic` for settings and data models
- Async where beneficial (Azure SDK calls)
- `snake_case` for functions/variables, `PascalCase` for classes

## Testing

- Use `pytest` with `pytest-asyncio` for async tests
- Test files: `tests/test_{module}.py`
- Run: `python -m pytest tests/ -v`

## Azure SDK

- Use `azure-identity` `DefaultAzureCredential` for auth
- Use `azure-mgmt-*` SDKs for resource management
- Use `azure-mgmt-resourcegraph` for Resource Graph queries

## Security

- Never hardcode credentials, subscription IDs, or tenant IDs
- Use environment variables via `pydantic_settings`
- Reference `src/config/settings.py` for the settings pattern
