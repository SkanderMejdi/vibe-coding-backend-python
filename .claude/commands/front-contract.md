---
description: "Frontend: analyze mockups → write OpenAPI contract in specs/api/. Includes business context for backend. Phase 3 BFF."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, grepai
---

# Front Contract: $ARGUMENTS

## Step 1: Read flow spec and mockups

```bash
cat specs/flows/$ARGUMENTS.md 2>/dev/null || echo "NO_FLOW"
```

```bash
ls maquettes/$ARGUMENTS/*.vue 2>/dev/null || echo "NO_MOCKUPS"
```

If no flow or no mockups, stop:
> Prérequis manquants. Il faut d'abord :
> - Flow spec (`/front-clarify`) ✓/✗
> - Maquettes (`/front-maquette`) ✓/✗

Read each mockup:

```bash
cat maquettes/$ARGUMENTS/$ARGUMENTS--*.vue
```

## Step 2: Separate responsibilities

### Backend responsibility

**Domain rules** — the core business truth:
- Prices, totals, margins (source of truth for money)
- Validation rules (can this order be cancelled?)
- State transitions (draft → validated → completed)

**BFF adapter** — expose data formatted for this consumer:
- Grouping (pains by pâte, commandes by acheteur)
- Sorting (par date, par priorité)
- Nesting/structuring (data pre-joined, ready to display)
- Aggregations (totaux, compteurs)

→ **The contract tells the back HOW to expose its data. Grouping, sorting, formatting = the back's adapter job, driven by the contract.**

### Frontend responsibility

**UX flow logic** — interaction logic that exists only because of the UI:
- Conditional display based on user interaction (show step 2 after step 1)
- Navigation between states (quel écran après quel clic)
- Ephemeral client state (is this accordion open? which tab is active?)
- Optimistic updates, local animations, transitions

→ **The front owns this. No API call needed, no backend involved.**

### Rule of thumb
> If it's about WHAT data to show and in WHAT shape → back (via contract).
> If it's about WHEN/HOW the user interacts with it → front.

## Step 3: Extract data needs from mockups

For each mockup, identify every piece of data and the **format** the front needs it in:

- What fields are displayed?
- How are they grouped? Sorted? Nested?
- What calculations appear (totals, counts)?
- What structure matches the visual layout?

**The contract should mirror the visual structure of the mockups.** If the mockup groups items by category, the API response should return items grouped by category.

## Step 4: Understand existing domain

```bash
grepai search "domain entities and business rules" --json --compact 2>/dev/null || grep -rn "class.*dataclass\|class.*Rules" src/domain/ --include="*.py" | head -20
```

```bash
cat openapi.yaml 2>/dev/null | head -80 || echo "No existing OpenAPI"
```

## Step 5: Present contract to user

> D'après les maquettes, voici ce que le contrat va demander au back :
>
> **`GET /api/{page}-view/{id}`**
>
> | Champ | Type | Rôle |
> |-------|------|------|
> | {field} | {type} | {domain rule / formatted exposure} |
>
> **Contexte métier :**
> - {domain concepts in user's vocabulary}
> - {formulas: prix = max(tag.prix_au_kilo) × poids_cuit}
>
> **Le front gère seul :**
> - {UX flow logic — ex: navigation entre onglets, état local}
>
> Ça te va ?

**Wait for confirmation.**

## Step 6: Write OpenAPI contract

```bash
mkdir -p specs/api
```

Create `specs/api/{page}-view.yml`:

```yaml
openapi: "3.0.3"
info:
  title: "{Page} View API"
  version: "1.0.0"
  description: |
    BFF contract for {page}.

    Business context:
    - {domain concepts in user's vocabulary}
    - {calculations: formulas, rules}

    Frontend owns (NOT in this contract):
    - {UX flow logic only}
paths:
  /api/{page}-view/{id}:
    get:
      summary: "{description in domain terms}"
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: "Success"
          content:
            application/json:
              schema:
                type: object
                required:
                  - {field1}
                  - {field2}
                properties:
                  {field1}:
                    type: {type}
                    description: "{domain meaning}"
                  {field2}:
                    type: {type}
```

### Rules for the contract

- **Structure mirrors the mockups** — if the UI groups by category, the response groups by category
- **Back computes everything the front displays** — totals, groupings, sorts, joins
- **Front only owns UX interaction logic** — not data transformation
- **Business context in `info.description`** — domain vocabulary, formulas, rules
- **Precise types** — `number` for prices/weights, `string` for IDs, `array` for lists
- **`description` on non-obvious fields** — explain in domain terms

## Step 7: Next step

> Contrat API écrit dans `specs/api/{page}-view.yml`
>
> Le back peut maintenant implémenter :
> `/back-clarify` → `/back-specify` → `/back-implement`
>
> Validation automatique par `make check-contract`.
