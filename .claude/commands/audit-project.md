---
description: "Audit an existing project for compatibility with this workflow. Diagnoses architecture, tests, and proposes an adoption strategy."
allowed-tools: Read, Bash, Grep, Glob, grepai
---

# Audit Project

**Goal: Honest assessment of whether and how this workflow can be adopted on the current project. Never force a migration — inform the user and let them decide.**

## Step 1: Project overview

```bash
# Project structure
find src/ app/ lib/ -type f -name "*.py" 2>/dev/null | head -50 || find . -maxdepth 4 -name "*.py" -not -path "./.venv/*" -not -path "./node_modules/*" | head -50

# Framework detection
grep -rn "fastapi\|flask\|django\|starlette" requirements*.txt pyproject.toml setup.py setup.cfg 2>/dev/null | head -10

# Test framework
grep -rn "pytest\|unittest\|nose" requirements*.txt pyproject.toml setup.py setup.cfg 2>/dev/null | head -5

# DB / ORM
grep -rn "sqlalchemy\|django.db\|peewee\|tortoise\|prisma" requirements*.txt pyproject.toml 2>/dev/null | head -5

# Lines of code (rough)
find . -name "*.py" -not -path "./.venv/*" -not -path "./node_modules/*" | xargs wc -l 2>/dev/null | tail -1
```

```bash
# Existing Makefile / build system
cat Makefile 2>/dev/null | head -30 || cat justfile 2>/dev/null | head -30 || echo "No Makefile"

# Existing Docker setup
ls docker-compose*.yml Dockerfile 2>/dev/null

# Existing CI
ls .github/workflows/*.yml .gitlab-ci.yml Jenkinsfile 2>/dev/null | head -10
```

## Step 2: Architecture analysis

### Current layering

```bash
# Source structure
find src/ app/ lib/ -type d 2>/dev/null | head -30 || find . -maxdepth 3 -type d -not -path "./.venv/*" -not -path "./.git/*" -not -path "./node_modules/*" | head -30
```

```bash
# Import patterns — who imports who?
grep -rn "^from\|^import" src/ app/ lib/ --include="*.py" 2>/dev/null | head -40 || grep -rn "^from\|^import" *.py **/*.py --include="*.py" 2>/dev/null | head -40
```

Evaluate:
- **Is there a domain layer?** (entities, business rules separated from framework)
- **Is there an application layer?** (use cases, handlers, services)
- **Is there an infrastructure layer?** (DB, APIs, external services)
- **Or is it a mixed/flat structure?** (routes + business logic + DB in same files)

### Dependency direction

```bash
# Check if business logic imports framework code
grep -rn "from.*infrastructure\|from.*api\|from.*routes\|from.*views" src/domain/ src/core/ src/models/ app/domain/ app/models/ 2>/dev/null | head -10

# Check if business logic imports ORM directly
grep -rn "from sqlalchemy\|from django.db\|import models" src/domain/ src/core/ app/domain/ 2>/dev/null | head -10
```

### Entity patterns

```bash
# Are entities dataclasses, Pydantic models, ORM models, or plain classes?
grep -rn "@dataclass\|class.*BaseModel\|class.*Model\|class.*Base)" src/ app/ --include="*.py" 2>/dev/null | head -20

# Are entities mutable or immutable?
grep -rn "frozen=True" src/ app/ --include="*.py" 2>/dev/null | head -10
```

## Step 3: Test analysis

### Coverage

```bash
# Count test files
find tests/ test/ -name "test_*.py" -o -name "*_test.py" 2>/dev/null | wc -l

# Count source files
find src/ app/ lib/ -name "*.py" -not -name "__init__.py" 2>/dev/null | wc -l || find . -maxdepth 3 -name "*.py" -not -name "__init__.py" -not -path "./.venv/*" | wc -l
```

```bash
# Test structure
find tests/ test/ -type d 2>/dev/null | head -20

# Sample test content
find tests/ test/ -name "test_*.py" 2>/dev/null | head -5 | xargs head -30 2>/dev/null
```

### Test quality

```bash
# Mocking patterns — are repos mocked?
grep -rn "Mock\|MagicMock\|patch\|mock" tests/ test/ --include="*.py" 2>/dev/null | wc -l

# What's being mocked?
grep -rn "Mock\|patch" tests/ test/ --include="*.py" 2>/dev/null | head -15

# Real DB tests?
grep -rn "fixture\|conftest\|session\|engine\|database" tests/ test/ --include="*.py" 2>/dev/null | head -10

# Test builders / factories?
grep -rn "Builder\|factory\|build_\|create_" tests/ test/ --include="*.py" 2>/dev/null | head -10
```

### Test resilience

```bash
# Are tests testing behavior or implementation?
# Implementation-coupled: asserting on method calls, internal state, mock call counts
grep -rn "assert_called\|call_count\|assert_has_calls\|._" tests/ test/ --include="*.py" 2>/dev/null | wc -l

# Behavior-coupled: asserting on results, side effects, exceptions
grep -rn "assert.*==\|assert.*in\|pytest.raises" tests/ test/ --include="*.py" 2>/dev/null | wc -l
```

## Step 4: Compatibility assessment

Based on the analysis, classify the project:

### Architecture gap

Rate each dimension:

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Domain isolation** | ✅ Clean / ⚠️ Partial / ❌ Mixed | Business logic separated from framework? |
| **Dependency direction** | ✅ Clean / ⚠️ Partial / ❌ Inverted | Domain depends on nothing external? |
| **Entity immutability** | ✅ Frozen / ⚠️ Dataclass / ❌ ORM models | Can be made frozen? |
| **Use case pattern** | ✅ Handlers / ⚠️ Services / ❌ In routes | Extractable? |
| **Repository pattern** | ✅ Protocol / ⚠️ Abstract / ❌ Direct ORM | Can add protocol layer? |

### Test gap

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Coverage** | ✅ Good / ⚠️ Partial / ❌ Minimal | % of source files with tests |
| **Real DB tests** | ✅ Yes / ❌ All mocked | Can switch to real DB? |
| **Mock coupling** | ✅ Low / ⚠️ Medium / ❌ High | How many tests break on refactor? |
| **Test structure** | ✅ Mirrors code / ⚠️ Flat / ❌ Random | Easy to navigate? |
| **Builders/fixtures** | ✅ Shared / ⚠️ Inline / ❌ None | Reusable test data? |

### Infrastructure gap

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Makefile** | ✅ Exists / ❌ Missing | Test, lint, typecheck targets? |
| **Docker tests** | ✅ Yes / ❌ No | Isolated test DB? |
| **Type checking** | ✅ mypy strict / ⚠️ Partial / ❌ None | Typed codebase? |
| **Linting** | ✅ ruff+black / ⚠️ Other / ❌ None | Consistent formatting? |
| **CI** | ✅ Full / ⚠️ Partial / ❌ None | Automated checks? |

## Step 5: Recommendation

Based on the assessment, recommend ONE of three strategies:

### Strategy A: Full adoption (green field or very compatible)

> **Le projet est compatible.** L'architecture est proche de la cible, les tests sont solides, l'effort de migration est faible.
>
> Plan d'adoption :
> 1. {specific steps}
> 2. ...
>
> Effort estimé : {petit / moyen}
> Risque : faible

**Criteria:** Domain already isolated or easily extractable, tests exist and use real DB, codebase is small/medium.

### Strategy B: Adapt the skills to the existing architecture

> **Le projet a une architecture différente mais cohérente.** Plutôt que de forcer l'architecture hexagonale, on peut adapter les skills pour respecter l'architecture en place.
>
> Architecture actuelle : {describe — e.g. "MVC classique avec services", "clean architecture avec use cases"}
>
> Adaptations proposées :
> - `back-clarify` → {how to adapt — e.g. "cherche dans services/ au lieu de domain/"}
> - `back-specify` → {how to adapt — e.g. "tests dans tests/services/ au lieu de tests/unit/domain/"}
> - `back-implement` → {how to adapt — e.g. "crée des services au lieu de handlers"}
> - Architecture hook → {how to adapt — e.g. "vérifie que services n'importent pas routes"}
>
> Ce qu'on garde tel quel :
> - Le flow TDD (clarify → specify → implement → refactor)
> - Le BFF contract flow
> - Le pre-commit hook
> - La philosophie "pas de mocks, DB réelle"
>
> Effort : {moyen}
> Risque : faible — on ne casse rien, on formalise l'existant

**Criteria:** Existing architecture is consistent and intentional, but different from hexagonal. Team knows it well. Forcing a migration would break muscle memory without clear benefit.

### Strategy C: Not recommended (too risky)

> **⚠️ La migration est risquée.** Voici pourquoi :
>
> - {reason 1 — e.g. "les tests sont fortement couplés aux mocks, les réécrire est un gros chantier"}
> - {reason 2 — e.g. "la logique métier est mélangée avec le framework dans 50+ fichiers"}
> - {reason 3 — e.g. "pas de tests existants, impossible de vérifier qu'on ne casse rien"}
>
> **Alternatives :**
> - Adopter uniquement le flow BFF (front-clarify → front-contract) sans toucher au backend
> - Adopter le workflow sur les **nouvelles features** uniquement, sans refactorer l'existant
> - Commencer un nouveau module isolé avec l'architecture cible, sans toucher au code existant

**Criteria:** Large codebase with tight coupling, few/no tests, business logic mixed with framework everywhere, or heavy mock dependency.

## Step 6: If the user wants to proceed

If the user chooses Strategy A or B:

> Voici le plan détaillé. On y va étape par étape ?
>
> **Étape 1 :** {first safe, reversible step}
> **Étape 2 :** {next step}
> ...
>
> Je propose de commencer par l'étape 1. On valide à chaque étape avant de continuer.

**Never batch the whole migration. One step at a time, validate with user, commit after each step.**

If Strategy B (adapt skills):
- Create modified versions of the skills in `.claude/commands/`
- Adjust the architecture hook to match the existing architecture's rules
- Keep the same TDD workflow, just with different file paths and patterns

> Je vais adapter les fichiers suivants à ton architecture :
> - `.claude/commands/back-*.md` — adaptés pour {your architecture}
> - `.claude/hooks/check_architecture.py` — règles ajustées
> - `CLAUDE.md` — conventions mises à jour
>
> On commence ?
