---
description: "Frontend: connect mockups to real API endpoints. Replace hardcoded data. Clean up maquettes and specs. Phase 5 BFF."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, grepai
---

# Front Dynamize: $ARGUMENTS

## Step 1: Check prerequisites

All 3 previous phases must be done and the backend must be implemented.

```bash
cat specs/flows/$ARGUMENTS.md 2>/dev/null || echo "NO_FLOW"
```

```bash
# Find maquette files (in real app structure)
find src/ -path "*maquette*$ARGUMENTS*" -name "*.vue" 2>/dev/null || echo "NO_MOCKUPS"
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

## Step 2: Analyze existing app architecture

Before touching anything, understand the full frontend architecture:

```bash
# Design system / shared CSS
find src/ -name "*.css" -o -name "*.scss" -o -name "variables*" -o -name "tokens*" 2>/dev/null | head -20
cat src/assets/styles/*.css 2>/dev/null | head -40 || true

# Existing composables / stores / services
find src/ -name "use*.ts" -o -name "use*.js" -o -name "*.store.*" -o -name "*.service.*" 2>/dev/null | head -20

# Existing API layer
find src/ -name "api*" -o -name "http*" -o -name "fetch*" 2>/dev/null | head -10

# Router structure
cat src/router/index.* 2>/dev/null || cat src/router.* 2>/dev/null | head -60
```

## Step 3: Read contract and mockups

```bash
cat specs/api/$ARGUMENTS-view.yml
```

```bash
# Read all maquette files for this page
find src/ -path "*maquette*$ARGUMENTS*" -name "*.vue" -exec cat {} \;
```

## Step 4: Plan the dynamization

For each mockup, identify:
- **Hardcoded data to replace** with the API response
- **UX flow logic to implement** (state transitions, conditional display, navigation)
- **Business logic to REMOVE from front** (calculations, joins, aggregations that the back now handles via BFF)
- **CSS to factorize** — identify duplicated styles across maquettes that should become shared classes, CSS variables, or component styles

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
> **Factorisation CSS :**
> - {shared styles to extract — ex: card styles used in 3 maquettes → shared component or CSS class}
>
> **Intégration dans l'app :**
> - Route finale : `/{page}` (remplace `/maquette/{page}--*`)
> - Layout : {existing layout used}
> - Navigation : {add to sidebar/menu/nav}
>
> Ça te va ?

**Wait for confirmation.**

## Step 5: Create dynamic component — INTEGRATED into the app

**This is NOT just "add fetch calls to maquettes". You are building the final production page.**

### Architecture integration

1. **Create the final page component** in the proper location (`src/views/{page}/` or `src/pages/{page}/`), NOT in a maquettes subfolder
2. **Use the project's existing API layer** (composables, services, HTTP client) — do NOT create one-off fetch calls
3. **Use existing shared components** from the design system
4. **Follow the project's existing patterns** for loading states, error handling, data fetching

### CSS factorization — MANDATORY

Before writing CSS:
- **Check existing CSS variables/tokens** and reuse them
- **Extract repeated styles** from maquettes into shared classes or component styles
- **Do NOT copy-paste CSS from each maquette** — identify common patterns first, create shared styles, then compose
- If multiple maquettes share a card/list/table style → extract as a component or shared class
- Use the design system's spacing, colors, typography — do NOT hardcode values that already exist as variables

### What to keep from mockups
- HTML structure (adapted to use real components)
- Visual design intent
- Component decomposition

### What to replace
- Hardcoded `const data = { ... }` → API fetch via project's API layer
- Inline calculations → use pre-computed values from API response
- Manual joins → use nested/grouped objects from API response
- One-off CSS → design system tokens and shared styles

### What to add
- Loading state (from flow spec)
- Error state (from flow spec)
- UX flow logic (front's own business — navigation, conditional display, ephemeral state)
- **Permanent route** in the router (replacing temporary maquette routes)
- **Navigation entry** (sidebar, menu, breadcrumb — wherever other pages are linked)

### What to delete
- Any business logic that the back now handles (calculations, grouping, sorting, aggregations)
- Cascade fetches (fetchA → fetchB → fetchC) replaced by single BFF call

## Step 6: Verify

Check that no old business logic remains in the front:

```bash
grepai search "business calculations or manual joins in frontend" --json --compact 2>/dev/null || true
```

Check for duplicated CSS:

```bash
# Look for repeated style blocks
grep -rn "style.*scoped" src/views/$ARGUMENTS/ src/pages/$ARGUMENTS/ --include="*.vue" 2>/dev/null | head -10
```

## Step 7: Clean up maquettes and specs

**Once the user validates the dynamic page works correctly:**

### Remove maquette files
```bash
# Delete maquette page files
find src/ -path "*maquette*$ARGUMENTS*" -name "*.vue" 2>/dev/null
```

Remove these files after user confirmation.

### Remove temporary routes
Remove all routes marked `// MAQUETTE — temporary route` for this page from the router.

### Clean up specs (optional, ask user)
> Les specs ont servi de contrat pendant le développement :
> - `specs/flows/$ARGUMENTS.md`
> - `specs/api/$ARGUMENTS-view.yml`
>
> On les garde comme documentation ou on les supprime ?
> (Le contrat est maintenant garanti par les tests backend + `make check-contract`)

**Wait for user decision on spec cleanup.**

## Step 8: Final verification

> Dynamisation terminée pour `{page}`.
>
> **Page finale :** `{path}`
> **Route :** `/{page}` (permanente)
> **Endpoint :** `GET /api/{page}-view/{id}`
>
> **Factorisation CSS :**
> - {shared styles created/reused}
>
> **Nettoyage effectué :**
> - ✅ Maquettes supprimées : {list}
> - ✅ Routes temporaires supprimées
> - {Specs: kept/removed per user choice}
>
> **Logique supprimée du front :**
> - {old logic removed}
>
> **Logique UX front conservée :**
> - {flow logic kept}
>
> Tu peux `git commit`.
