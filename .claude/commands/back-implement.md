---
description: "Backend: write minimal code to make tests pass. Run after /back-specify."
allowed-tools: Read, Write, Edit, Bash, Grep, grepai
---

# Implement

## Step 1: Check Makefile

```bash
cat Makefile 2>/dev/null | head -20 || echo "NO_MAKEFILE"
```

If no Makefile, stop and ask how to run tests.

## Step 2: Read failing tests

```bash
make test 2>&1 | tail -30
```

## Step 3: Read spec and contract for context

```bash
cat .claude/temp/spec.md 2>/dev/null || echo "No spec"
```

```bash
ls specs/api/*.yml specs/api/*.yaml 2>/dev/null && cat specs/api/*.yml 2>/dev/null || echo "No BFF contract"
```

## Step 4: Find related code

```bash
grepai search "related concepts" 2>/dev/null | head -10 || true
```

## Step 5: Implement domain + application

**Write ONLY what's needed to make tests pass.**

Follow architecture:
- Entity → `src/domain/{entity}/{entity}.py` (frozen dataclass)
- Rules → `src/domain/{entity}/{entity}_rules.py` (static methods)
- Repository → `src/domain/{entity}/{entity}_repository.py` (Protocol)
- Handler → `src/application/{entity}/{action}_{entity}/handler.py`

## Step 6: Run tests

```bash
make test 2>&1 | tail -30
```

**All tests must pass.**

If tests fail → fix code, not tests.

## Step 7: Implement API endpoint

**Tests don't cover HTTP endpoints, but the frontend needs them to work.**

After tests pass, check if this feature needs an API endpoint. If yes:

1. Find existing routes to follow the same pattern:

```bash
grepai search "API routes or endpoint registration" --json --compact 2>/dev/null || grep -rn "@router\|@app\." src/infrastructure/ --include="*.py" | head -10
```

2. Create or update the endpoint in `src/infrastructure/api/`:
   - Route calls the handler (dependency injection via FastAPI `Depends` or manual wiring)
   - Request/Response models (Pydantic) in the same file or next to it
   - **If a BFF contract exists**: the Pydantic response model MUST match the contract schema (same field names, types, required fields)
   - Proper HTTP status codes (201 for creation, 204 for deletion, etc.)

3. Inform the user:
> Endpoint créé : `{METHOD} /api/{resource}`
> Request body / Query params : {describe}
> Response : {describe}

**If unsure whether an endpoint is needed, ask.**

## Step 8: Verify contract

If a BFF contract exists in `specs/api/`:

```bash
make check-contract 2>&1 | tail -20
```

**Contract MUST pass.** If it fails:
- Missing field → add it to the Pydantic response model
- Type mismatch → fix the response model type
- Missing required → add the field to the model (not Optional)

**Do NOT modify the contract to match the code. Fix the code to match the contract.**

## Step 9: Verify intent

Re-read the spec. Ask yourself:
- Does the code do what the user wanted?
- Or does it just pass the tests by accident?
- Can the frontend actually call this feature?

If doubt:
> Le code fait passer les tests, mais je vérifie :
> [describe what code does]
> C'est bien ça ?

## Step 10: Seeders (if needed)

If the endpoint needs data to be testable manually (dev environment), check if seeders exist:

```bash
grepai search "seed data or seeders" --json --compact 2>/dev/null || grep -rn "seed\|fixture" scripts/ src/ --include="*.py" | head -10
```

If no seeder exists for the entities involved, create one in `scripts/seed/`:

```bash
mkdir -p scripts/seed
```

Create `scripts/seed/{entity}.py` with **realistic domain data** (same vocabulary as the mockups and contract). The seeder should:
- Be idempotent (safe to run multiple times)
- Use the repository implementations directly
- Create enough data to exercise all states from the flow spec

Add a `make seed` target to the Makefile if it doesn't exist.

**Only create seeders if the feature needs data to be usable.** Pure stateless endpoints don't need seeders.

## Step 11: Done

> Implémentation terminée. Tests passent.
>
> Fichiers créés :
> - {list}
>
> Endpoint : `{METHOD} /api/{resource}` (si applicable)
> Contract check : ✅ (si BFF)
> Seeder : `scripts/seed/{entity}.py` (si applicable)
>
> Tu peux `git commit` ou `/clear` puis `/back-refactor` si besoin.
