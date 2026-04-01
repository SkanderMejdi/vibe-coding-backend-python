---
description: "Frontend: create static mockups per state from flow spec. Integrates into existing codebase. Hardcoded data on new elements. Phase 2 BFF."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Front Maquette: $ARGUMENTS

**CRITICAL: You MUST use the `frontend-design` skill for EVERY generation and EVERY iteration. No exception. Design quality is central to this phase. If you are about to write or edit a Vue file without invoking `frontend-design`, STOP and invoke it first.**

## Step 1: Read flow spec

```bash
cat specs/flows/$ARGUMENTS.md 2>/dev/null || echo "NO_FLOW"
```

If no flow spec, stop: "Pas de flux. Lance `/front-clarify {page}` d'abord."

## Step 2: Analyze existing codebase

Before creating anything, understand the existing project structure:

```bash
# Existing layouts
find src/ -name "*layout*" -o -name "*Layout*" 2>/dev/null | head -20
ls src/layouts/ 2>/dev/null || ls src/components/layouts/ 2>/dev/null || true

# Existing router
find src/ -name "router*" -o -name "routes*" 2>/dev/null | head -10
cat src/router/index.* 2>/dev/null || cat src/router.* 2>/dev/null | head -40 || true

# Existing components (design system)
ls src/components/ 2>/dev/null | head -30
find src/components/ -name "*.vue" 2>/dev/null | head -30

# Existing pages for structure reference
find src/pages/ src/views/ -name "*.vue" 2>/dev/null | head -20
```

Identify:
- **Layout(s)** to reuse (sidebar, header, navigation, etc.)
- **Shared components** to reuse (buttons, cards, tables, modals, form inputs, etc.)
- **Router structure** to follow (naming convention, nesting, guards)
- **Design tokens / CSS variables** in use (colors, spacing, typography)

## Step 3: Identify states to mock

From the scenario diagram, extract the **distinct visual states** the user can see. Each leaf/outcome in the diagram is a potential mockup.

> D'après le diagramme, voici les états visuels à maquetter :
>
> 1. `{page}--{état1}` — {description en termes métier}
> 2. `{page}--{état2}` — {description}
> ...
>
> Je commence par lequel ?

**Wait for user direction** (or propose starting with the main/default state).

## Step 4: Design conversation

Before coding, **discuss the UX with the user**. This is a creative conversation, not just implementation:

- **Quelle ambiance ?** — Minimaliste, dense, ludique, pro ?
- **Quel feeling ?** — Rapide et efficace ? Agréable à parcourir ? Satisfaisant à utiliser ?
- **Quelles micro-interactions ?** — Transitions, feedback visuel, animations subtiles ?
- **Inspiration ?** — Une app qu'il aime utiliser ? Un style qui lui plaît ?

L'objectif : une UX **fluide, adaptée au métier, presque addictive**. Pas un formulaire CRUD générique.

**Carry this design vision across ALL mockups.**

## Step 5: Create mockup with frontend-design — INSIDE the existing app

**MANDATORY: Invoke `frontend-design` skill NOW.** Every mockup generation must go through `frontend-design`.

### Integration rules

Mockups are integrated into the existing app, NOT isolated in a `maquettes/` folder:

1. **Use existing layout(s)** — the mockup page wraps inside the app's main layout (sidebar, header, nav). Do NOT recreate layout chrome.
2. **Use existing shared components** — buttons, cards, tables, inputs, modals from the design system. Only create new components if nothing existing fits.
3. **Add a temporary route** in the router:
   ```
   /maquette/{page}--{état}
   ```
   Mark it with a comment: `// MAQUETTE — temporary route, remove after /front-dynamize`
4. **Place files in the real pages/views directory** with a clear maquette prefix:
   - `src/views/maquettes/{page}/{Page}{État}.vue` or
   - `src/pages/maquettes/{page}/{Page}{État}.vue`
   (follow the project's existing convention for pages vs views)

### Data rules for NEW elements

- **Valeurs en dur sur les nouveaux éléments** — pas de fetch, pas de mock, pas de store, pas de props dynamiques. Les éléments spécifiques à cette maquette utilisent des données hardcodées.
- **Données réalistes du métier** — utiliser des vraies valeurs métier (noms de recettes, poids en grammes, vrais prix), pas "Lorem ipsum"
- **Un fichier = un état** — chaque état est autonome et complet visuellement
- **Design cohérent** — même direction artistique sur tous les états, cohérent avec l'existant

### Existing elements are REAL

- Existing layout, navigation, shared components work normally — they are NOT mocked
- Only the new page-specific content uses hardcoded data

## Step 6: Validate with user — ONE PAGE AT A TIME

After creating EACH mockup state, **stop and validate with the user before moving to the next**:

> Maquette créée : `{file_path}`
>
> Route temporaire : `/maquette/{page}--{état}`
>
> Composants existants réutilisés : {list}
>
> **Qu'est-ce que tu en penses ? On ajuste avant de passer à l'état suivant ?**

**MANDATORY: Use `frontend-design` for every iteration/adjustment too.** Do not skip it even for "small" fixes.

**Do NOT proceed to the next state until the user explicitly validates the current one.**

## Step 7: Factorize shared components

If patterns repeat across mockups, extract shared components into the project's real component directory (NOT a separate maquettes/components folder).

**Only factorize when asked or when the duplication is obvious.**

## Step 8: Next step

> Maquettes terminées pour {page} :
> - `{état1}` — ✅ validé
> - `{état2}` — ✅ validé
> ...
>
> Routes temporaires ajoutées : `/maquette/{page}--*`
> Composants existants réutilisés : {list}
> Nouveaux composants créés : {list or "aucun"}
>
> Prochaine étape : `/clear` puis `/front-contract {page}`
