---
description: Clarify requirements through conversation. Output is a clear spec. FIRST STEP for any new feature.
allowed-tools: Read, Grep, Bash, grepai
---

# Clarify: $ARGUMENTS

## Step 1: Check what exists

```bash
grepai search "$ARGUMENTS" 2>/dev/null | head -10 || grep -rn "$ARGUMENTS" src/ --include="*.py" | head -5
```

Check if a BFF contract exists for this feature:

```bash
ls specs/api/ 2>/dev/null && cat specs/api/*.yml 2>/dev/null | head -60
```

## Step 2: Read BFF contract (if it exists)

If a contract exists in `specs/api/`, **read it carefully**. It defines what the front expects: paths, response shapes, required fields. This is your input — the front has already decided what data it needs.

Your job: figure out **how** to produce this data from the backend (domain model, rules, queries, aggregations).

## Step 3: Conversation to clarify

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

**Don't ask questions already answered.**

## Step 4: Reformulate and confirm

> Si je comprends bien :
> - [Qui] fait [Quoi]
> - Les données viennent de [source]
> - Règles métier : [conditions, calculs]
> - Erreurs possibles : [cas d'erreur]
>
> C'est correct ?

**Wait for explicit confirmation.**

## Step 5: Write spec

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

## Behavior
- Actor: {who}
- Action: {what}
- Data sources: {entities, joins, aggregations}
- Business rules: {conditions, calculations}
- Success when: {conditions}
- Failure when: {conditions} → {error/behavior}

## Confirmed by user
```

## Step 6: Next step

> Spec écrite dans `.claude/temp/spec.md`
>
> Prochaine étape : `/clear` puis `/specify`
