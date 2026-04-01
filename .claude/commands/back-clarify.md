---
description: "Backend: clarify requirements → spec. Reads BFF contract as input if it exists. Verifies existing code and architecture."
allowed-tools: Read, Grep, Bash, grepai
---

# Clarify: $ARGUMENTS

## Step 1: Check what exists in the codebase

Before asking anything, understand the current state of the project:

```bash
grepai search "$ARGUMENTS" --json --compact 2>/dev/null | head -20 || grep -rn "$ARGUMENTS" src/ --include="*.py" | head -10
```

```bash
# Existing domain entities and rules
ls src/domain/*/  2>/dev/null
grep -rn "class.*:" src/domain/ --include="*.py" | head -20
```

```bash
# Existing application handlers
ls src/application/*/ 2>/dev/null
grep -rn "class.*Handler" src/application/ --include="*.py" | head -10
```

```bash
# Existing infrastructure (repos, endpoints)
grep -rn "class.*Repository" src/infrastructure/ --include="*.py" | head -10
grep -rn "@router\|@app\." src/infrastructure/ --include="*.py" | head -10
```

```bash
# Existing shared errors and types
cat src/shared/*.py 2>/dev/null | head -30
```

## Step 2: Check BFF contract

```bash
ls specs/api/ 2>/dev/null && cat specs/api/*.yml 2>/dev/null | head -80
```

If a contract exists in `specs/api/`, **read it carefully**. It defines what the front expects: paths, response shapes, required fields. This is your input — the front has already decided what data it needs.

## Step 3: Verify architecture fit

**Before asking user questions, verify how this feature fits into existing architecture:**

- **Which existing entities are involved?** Does this feature extend an existing entity or require a new one?
- **Which existing rules apply?** Are there business rules already implemented that affect this feature?
- **Which existing repositories can be reused?** Don't create new repos if an existing one covers the data access.
- **Which existing handlers are related?** Is there a handler doing something similar that should be extended or composed with?
- **Does the BFF contract ask for data that crosses multiple existing entities?** → This means a query/read-model, not CRUD.

Present your architecture assessment:

> **État de l'existant :**
> - Entités en place : {list or "aucune"}
> - Règles métier existantes : {list or "aucune"}
> - Repos/Handlers réutilisables : {list or "aucun"}
>
> **Impact architecture :**
> - {New entity needed / Extend existing entity X / Read-model across X and Y}
> - {New handler / Extend existing handler}

## Step 4: Conversation to clarify

**Ask questions until the need is crystal clear.**

Start with:
> Explique-moi ce que tu veux, dans tes mots.

Then ask what's missing — focus on **backend concerns**:
- **Modèle ?** - Quelles entités sont impliquées ? Relations entre elles ?
- **Règles métier ?** - Quelles conditions, calculs, validations ?
- **Source de données ?** - D'où viennent les données ? Quelles jointures ?
- **Performance ?** - Volume attendu ? Besoin de pagination, cache ?
- **Erreurs ?** - Qu'est-ce qui peut mal tourner côté back ?

**If a BFF contract exists, don't re-demander les champs de réponse — c'est déjà fixé.**

**Cross-check with existing code:** If the user describes behavior that overlaps with existing rules or entities, point it out explicitly:
> ⚠️ Attention, `{ExistingEntity}Rules.{method}` fait déjà {description}. On le réutilise ou on a un cas différent ?

**Don't ask questions already answered.**

## Step 5: Reformulate and confirm

> Si je comprends bien :
> - [Qui] fait [Quoi]
> - Les données viennent de [source]
> - Règles métier : [conditions, calculs]
> - Erreurs possibles : [cas d'erreur]
>
> **Cohérence architecture :**
> - S'intègre avec : {existing entities/rules/repos}
> - Nouveau à créer : {new entities/rules}
> - Naming : {EntityName, action_entity for handler, etc.}
>
> C'est correct ?

**Wait for explicit confirmation.**

## Step 6: Write spec

```bash
mkdir -p .claude/temp
```

Create `.claude/temp/spec.md`:

```markdown
# Feature: {name}

## Intent
{User's exact words, quoted}

## BFF Contract
{Reference to specs/api/{page}-view.yml if applicable, or "N/A"}

## Existing Code Involved
- Entities: {list with file paths, or "none"}
- Rules: {list with file paths, or "none"}
- Repositories: {list with file paths, or "none"}
- Handlers: {list with file paths, or "none"}

## Behavior
- Actor: {who}
- Action: {what}
- Data sources: {entities, joins, aggregations}
- Business rules: {conditions, calculations}
- Success when: {conditions}
- Failure when: {conditions} → {error/behavior}

## Architecture Decision
- {New entity X / Extend entity Y}
- {New handler ActionXHandler / Extend existing}
- Naming: {EntityName, entity_rules.py, action_entity/handler.py}

## Confirmed by user
```

## Step 7: Next step

> Spec écrite dans `.claude/temp/spec.md`
>
> Prochaine étape : `/clear` puis `/back-specify`
