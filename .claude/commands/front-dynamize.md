---
description: "Frontend: connect mockups to real API endpoints. Replace hardcoded data. Phase 5 BFF."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, grepai
---

# Front Dynamize: $ARGUMENTS

## Step 1: Check prerequisites

All 3 previous phases must be done and the backend must be implemented.

```bash
cat specs/flows/$ARGUMENTS.md 2>/dev/null || echo "NO_FLOW"
```

```bash
ls maquettes/$ARGUMENTS/*.vue 2>/dev/null || echo "NO_MOCKUPS"
```

```bash
cat specs/api/$ARGUMENTS-view.yml 2>/dev/null || echo "NO_CONTRACT"
```

```bash
cat openapi.yaml 2>/dev/null | head -20 || echo "No OpenAPI — backend not implemented?"
```

If anything is missing, stop:
> Prérequis manquants :
> - Flow spec (`/front-clarify`) ✓/✗
> - Maquettes (`/front-maquette`) ✓/✗
> - Contrat API (`/front-contract`) ✓/✗
> - Backend implémenté (`/back-implement`) ✓/✗

## Step 2: Read contract and mockups

```bash
cat specs/api/$ARGUMENTS-view.yml
```

```bash
cat maquettes/$ARGUMENTS/$ARGUMENTS--*.vue
```

## Step 3: Plan the dynamization

For each mockup, identify:
- **Hardcoded data to replace** with the API response
- **UX flow logic to implement** (state transitions, conditional display, navigation)
- **Business logic to REMOVE from front** (calculations, joins, aggregations that the back now handles via BFF)

Present the plan:

> Pour dynamiser `{page}` :
>
> **Brancher sur l'API :**
> - `GET /api/{page}-view/{id}` → remplace les données en dur
>
> **Logique UX front à implémenter :**
> - {flow logic — ex: navigation entre états, onglet actif}
>
> **À supprimer du front :**
> - {old business logic — ex: calcul de prix, jointures manuelles}
>
> Ça te va ?

**Wait for confirmation.**

## Step 4: Create dynamic component

Transform the mockups into the real component. Use `frontend-design` to maintain design quality.

### What to keep from mockups
- HTML structure
- CSS / visual design
- Component decomposition

### What to replace
- Hardcoded `const data = { ... }` → API fetch
- Inline calculations → use pre-computed values from API response
- Manual joins → use nested/grouped objects from API response

### What to add
- Loading state (from flow spec)
- Error state (from flow spec)
- UX flow logic (front's own business — navigation, conditional display, ephemeral state)

### What to delete
- Any business logic that the back now handles (calculations, grouping, sorting, aggregations)
- Cascade fetches (fetchA → fetchB → fetchC) replaced by single BFF call

## Step 5: Verify

Check that no old business logic remains in the front:

```bash
grepai search "business calculations or manual joins in frontend" --json --compact 2>/dev/null || true
```

> Dynamisation terminée pour `{page}`.
>
> Composant : `{path}`
> Endpoint : `GET /api/{page}-view/{id}`
>
> Supprimé du front :
> - {old logic removed}
>
> Logique UX front conservée :
> - {flow logic kept}
>
> Tu peux tester et `git commit`.
