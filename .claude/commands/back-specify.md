---
description: "Backend: generate tests from spec. Tests MUST fail. Run after /back-clarify."
allowed-tools: Read, Write, Bash, grepai
---

# Specify

## Step 1: Check Makefile exists

```bash
cat Makefile 2>/dev/null | head -20 || echo "NO_MAKEFILE"
```

If no Makefile, stop and ask:
> Pas de Makefile trouvé. Comment lances-tu les tests ?
> Je peux générer un Makefile si tu me dis quelle commande utiliser (docker, python, etc.)

## Step 2: Read spec and contract

```bash
cat .claude/temp/spec.md
```

If no spec, stop: "Pas de spec. Lance `/back-clarify` d'abord."

Check for BFF contract referenced in the spec:

```bash
ls specs/api/*.yml specs/api/*.yaml 2>/dev/null && cat specs/api/*.yml 2>/dev/null
```

## Step 3: Check existing test infrastructure

**Before writing any test, understand what already exists to avoid duplication:**

```bash
# Existing test helpers, builders, fixtures
find tests/ -name "conftest*" -o -name "*builder*" -o -name "*factory*" -o -name "*helper*" -o -name "*fixture*" 2>/dev/null
```

```bash
# Read all conftest files (shared fixtures)
find tests/ -name "conftest.py" -exec cat {} \; 2>/dev/null
```

```bash
# Read existing builders/helpers
find tests/helpers/ -name "*.py" -exec cat {} \; 2>/dev/null || true
```

```bash
# Existing test structure (to mirror)
find tests/ -type f -name "*.py" | head -30
```

**Identify reusable infrastructure:**
- Database session fixtures → reuse from conftest
- Entity builders → reuse existing builders in `tests/helpers/`
- Common assertions → reuse existing patterns

## Step 4: List test cases

From the spec, identify:
- **Success cases** - conditions met → expected outcome
- **Failure cases** - conditions not met → expected error

**Focus on business logic**: rules, calculations, state transitions, data aggregation. NOT on HTTP response formatting — that's validated by `make check-contract`.

## Step 5: Verify with user

> D'après la spec, voici les cas que je vais tester :
>
> ✓ Succès :
> - {case 1}
> - {case 2}
>
> ✗ Échec :
> - {case 3} → {error}
>
> Il manque des cas ?

**Wait for confirmation.**

## Step 6: Write tests

### File location — MUST mirror source code structure

Test files MUST follow the same directory structure as the source code, so that navigating tests is predictable:

```
src/domain/{entity}/{entity}_rules.py
  → tests/unit/domain/{entity}/test_{entity}_rules.py

src/application/{entity}/{action}_{entity}/handler.py
  → tests/integration/application/{entity}/test_{action}_{entity}_handler.py
```

**The naming MUST be consistent across layers.** If the entity is `Order`, use `order` everywhere:
- `src/domain/order/` → `tests/unit/domain/order/`
- `src/application/order/create_order/` → `tests/integration/application/order/test_create_order_handler.py`

This consistency lets the AI (and humans) navigate by convention: knowing the entity name is enough to find all related code and tests.

### NEVER mock repositories

**Do not use `Mock()`, `MagicMock()`, or `patch()` for repositories.** Mocked repos hide real bugs (wrong queries, missing saves, broken constraints).

Tests run against a **real database** (Postgres via docker-compose.test.yml). The DB is reset at each run (`alembic downgrade base && alembic upgrade head`). Use the real repository implementations and rely on fixtures/builders to set up test data.

### Test maintainability — MANDATORY

**Do NOT duplicate test infrastructure.** Follow these rules:

1. **Shared fixtures go in `conftest.py`** — database session, common entities used across tests. Place conftest at the appropriate level:
   - `tests/conftest.py` — global fixtures (db session, cleanup)
   - `tests/unit/domain/{entity}/conftest.py` — entity-specific fixtures (if shared across rule test files)
   - `tests/integration/application/{entity}/conftest.py` — handler-specific fixtures

2. **Builders go in `tests/helpers/builders/`** — one builder per entity. A builder is a function or class that creates a valid entity with sensible defaults, letting tests override only what they care about:
   ```python
   # tests/helpers/builders/order_builder.py
   def build_order(**overrides) -> Order:
       defaults = {
           "id": uuid4(),
           "customer_id": uuid4(),
           "status": OrderStatus.PENDING,
           "total": Decimal("100.00"),
           "created_at": datetime.now(UTC),
       }
       return Order(**(defaults | overrides))
   ```
   **Reuse existing builders. Only create new ones if no builder exists for this entity.**

3. **Common test helpers go in `tests/helpers/`** — assertion helpers, data setup functions shared across test files.

4. **Do NOT duplicate builder logic inside test files** — import from `tests/helpers/builders/`. If a test needs a slightly different entity, use builder overrides, not a new inline factory.

### Prefer testing behavior over implementation

When possible, assert on **observable behavior** (results, side effects, errors) rather than internal details (which method was called, in what order). This makes tests more resilient to refactors.

That said, complex business logic sometimes requires detailed unit tests that are tightly coupled to implementation — that's fine when the logic justifies it.

### Don't test response formatting

The BFF contract (`specs/api/*.yml`) defines the response shape. `make check-contract` validates that the generated OpenAPI matches the contract. **Don't write integration tests for field names, JSON structure, or HTTP formatting** — the contract check covers that.

Test the **handler output** (business data is correct), not the **endpoint output** (JSON shape is correct).

### Test template

```python
"""
Tests for {feature}.

Intent (user's words):
{paste from spec}
"""

import pytest
from tests.helpers.builders.{entity}_builder import build_{entity}


class Test{Feature}:

    # --- SUCCESS CASES ---

    def test_should_{outcome}_when_{condition}(self):
        # Arrange — use builders to create test data
        entity = build_{entity}(status="active")
        ...
        # Act
        ...
        # Assert
        assert ...

    # --- FAILURE CASES ---

    def test_should_fail_when_{condition}(self):
        # Arrange
        ...
        # Act & Assert
        with pytest.raises({Error}) as exc:
            ...
        assert "{message}" in str(exc.value)
```

## Step 7: Verify tests fail

```bash
make test 2>&1 | tail -20
```

**Tests MUST fail.** If they pass, something is wrong.

## Step 8: Next step

> Tests créés. Ils échouent (normal).
>
> Infrastructure de test :
> - Builders réutilisés : {list or "aucun — premiers builders créés"}
> - Fixtures réutilisées : {list or "aucune — premières fixtures créées"}
> - Nouveaux builders créés : {list or "aucun"}
>
> Structure des tests :
> - `tests/unit/domain/{entity}/test_{entity}_rules.py`
> - `tests/integration/application/{entity}/test_{action}_{entity}_handler.py`
>
> Prochaine étape : `/clear` puis `/back-implement`
