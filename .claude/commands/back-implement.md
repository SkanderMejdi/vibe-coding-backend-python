---
description: "Backend: write minimal code to make tests pass. Run after /back-specify."
allowed-tools: Read, Write, Edit, Bash, Grep, grepai
---

# Implement

## HARD RULES — NO EXCEPTIONS

**You MUST follow these rules. Violating any of them is a blocking failure.**

1. **NEVER disable or bypass hooks** — no `--no-verify`, no commenting out hook config, no skipping pre-commit checks
2. **NEVER bypass architecture constraints** — domain MUST NOT import infrastructure or application. If the architecture hook blocks you, your code is wrong. Fix the code, not the hook.
3. **NEVER ignore lint/type errors** — no `# type: ignore` unless there is a genuine mypy bug (explain why in a comment). No `# noqa` unless the rule is genuinely wrong for this line. No `# pragma: no cover` on code that should be tested.
4. **NEVER use workarounds to make checks pass** — if `make lint` fails, fix the code. If `make typecheck` fails, fix the types. If `make check-contract` fails, fix the response model. Do not game the system.
5. **Write EXPLICIT code** — no magic, no implicit behavior, no "clever" tricks. Every variable has a clear name. Every function does one thing. Every branch is visible. Prefer verbose and obvious over short and cryptic.

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
grepai search "related concepts" --json --compact 2>/dev/null | head -10 || true
```

Check existing code identified in the spec:

```bash
# Read existing entities, rules, repos mentioned in spec
grep -rn "class " src/domain/ --include="*.py" | head -20
grep -rn "class " src/application/ --include="*.py" | head -20
```

## Step 5: Implement domain + application

**Write ONLY what's needed to make tests pass.**

Follow architecture:
- Entity → `src/domain/{entity}/{entity}.py` (frozen dataclass)
- Rules → `src/domain/{entity}/{entity}_rules.py` (static methods)
- Repository → `src/domain/{entity}/{entity}_repository.py` (Protocol)
- Handler → `src/application/{entity}/{action}_{entity}/handler.py`

### Code quality requirements

- **Explicit naming**: `calculate_total_price` not `calc`, `is_order_cancellable` not `check`
- **No abbreviations** in public APIs: `quantity` not `qty`, `description` not `desc`
- **Type everything**: all function signatures, all variables where the type isn't obvious from the assignment
- **One responsibility per function**: if a function has "and" in its description, split it
- **Visible flow**: handler steps (VALIDATE → FETCH → RULES → PERSIST → EVENTS) must be readable top-to-bottom without jumping to base classes
- **Reuse existing code**: if the spec mentions existing entities/rules/repos, import and use them. Do NOT duplicate.

## Step 6: Run tests

```bash
make test 2>&1 | tail -30
```

**All tests must pass.**

If tests fail → fix code, not tests.

## Step 7: Run ALL checks proactively

**Do not wait for the pre-commit hook to catch issues. Run checks NOW:**

```bash
make lint 2>&1 | tail -20
```

```bash
make typecheck 2>&1 | tail -20
```

**Fix any issue immediately.** Do not proceed with lint or type errors.

## Step 8: Implement API endpoint

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

## Step 9: Verify contract

If a BFF contract exists in `specs/api/`:

```bash
make check-contract 2>&1 | tail -20
```

**Contract MUST pass.** If it fails:
- Missing field → add it to the Pydantic response model
- Type mismatch → fix the response model type
- Missing required → add the field to the model (not Optional)

**Do NOT modify the contract to match the code. Fix the code to match the contract.**

## Step 10: Verify intent

Re-read the spec. Ask yourself:
- Does the code do what the user wanted?
- Or does it just pass the tests by accident?
- Can the frontend actually call this feature?

If doubt:
> Le code fait passer les tests, mais je vérifie :
> [describe what code does]
> C'est bien ça ?

## Step 11: Seeders (if needed)

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

## Step 12: Done

> Implémentation terminée. Tests passent.
>
> Fichiers créés :
> - {list}
>
> Checks :
> - ✅ `make test` — all pass
> - ✅ `make lint` — clean
> - ✅ `make typecheck` — no errors
> - ✅ `make check-contract` — matches (si BFF)
>
> Endpoint : `{METHOD} /api/{resource}` (si applicable)
> Seeder : `scripts/seed/{entity}.py` (si applicable)
>
> Tu peux `git commit` ou `/clear` puis `/back-refactor` si besoin.
