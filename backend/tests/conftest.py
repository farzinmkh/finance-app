"""
Root Test Configuration
========================
Fixtures defined here are available to ALL tests in the test suite
(unit, integration, and API tests).

conftest.py is a special pytest file. pytest automatically discovers and
loads it before running tests. You never import from conftest.py directly —
pytest injects fixtures by matching their name to test function parameters.

This root conftest stays intentionally minimal.
Layer-specific fixtures belong in the conftest.py closer to those tests:
  - tests/api/conftest.py       → FastAPI TestClient
  - tests/integration/conftest.py → Database session with real SQLite
"""

# Shared fixtures will be added here as the project grows.
# For now, the root conftest is intentionally empty.
