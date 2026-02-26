---
description: "Frontend: create static mockups per state from flow spec. Hardcoded data, no fetch. Phase 2 BFF."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Front Maquette: $ARGUMENTS

**IMPORTANT: Always use the `frontend-design` skill for every mockup. Design quality is not optional — it's central to this phase.**

## Step 1: Read flow spec

```bash
cat specs/flows/$ARGUMENTS.md 2>/dev/null || echo "NO_FLOW"
```

If no flow spec, stop: "Pas de flux. Lance `/front-clarify {page}` d'abord."

## Step 2: Identify states to mock

From the scenario diagram, extract the **distinct visual states** the user can see. Each leaf/outcome in the diagram is a potential mockup.

> D'après le diagramme, voici les états visuels à maquetter :
>
> 1. `{page}--{état1}` — {description en termes métier}
> 2. `{page}--{état2}` — {description}
> ...
>
> Je commence par lequel ?

**Wait for user direction** (or propose starting with the main/default state).

## Step 3: Design conversation

Before coding, **discuss the UX with the user**. This is a creative conversation, not just implementation:

- **Quelle ambiance ?** — Minimaliste, dense, ludique, pro ?
- **Quel feeling ?** — Rapide et efficace ? Agréable à parcourir ? Satisfaisant à utiliser ?
- **Quelles micro-interactions ?** — Transitions, feedback visuel, animations subtiles ?
- **Inspiration ?** — Une app qu'il aime utiliser ? Un style qui lui plaît ?

L'objectif : une UX **fluide, adaptée au métier, presque addictive**. Pas un formulaire CRUD générique.

**Carry this design vision across ALL mockups.**

## Step 4: Create mockup with frontend-design

```bash
mkdir -p maquettes/{page}
```

**Invoke `frontend-design` for EVERY mockup.** The design must be distinctive, polished, and adapted to the domain.

Check existing components for design consistency:

```bash
ls maquettes/components/ 2>/dev/null
```

### Rules

- **Valeurs en dur** — pas de fetch, pas de mock, pas de store, pas de props dynamiques
- **Données réalistes du métier** — utiliser des vraies valeurs métier (noms de recettes, poids en grammes, vrais prix), pas "Lorem ipsum"
- **Un fichier = un état** — chaque état est autonome et complet visuellement
- **Design cohérent** — même direction artistique sur tous les états

Output: `maquettes/{page}/{page}--{état}.vue`

## Step 5: Iterate on design

After creating the mockup, take a screenshot and iterate:

> Maquette créée : `maquettes/{page}/{page}--{état}.vue`
>
> Qu'est-ce que tu en penses ? On ajuste quoi ?

**Iterate on both UX and visual design until the user is satisfied.** The mockup should feel like the real app, not a wireframe.

Continue to use `frontend-design` on each iteration.

## Step 6: Factorize shared components

If patterns repeat across mockups, extract shared components to `maquettes/components/`.

**Only factorize when asked or when the duplication is obvious.**

## Step 7: Next step

> Maquettes terminées pour {page} :
> - `{page}--{état1}.vue`
> - `{page}--{état2}.vue`
> ...
>
> Prochaine étape : `/clear` puis `/front-contract {page}`
