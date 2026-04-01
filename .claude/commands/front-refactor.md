---
description: "Frontend: refactor components, extract shared UI, verify design system coherence. Optional."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, grepai
---

# Front Refactor: $ARGUMENTS

**IMPORTANT: Always use the `frontend-design` skill when touching visual code. Design quality must not regress.**

## Step 1: Inventory current state

```bash
ls frontend/src/components/ frontend/src/features/*/components/ 2>/dev/null
```

```bash
ls frontend/src/pages/*.vue 2>/dev/null
```

```bash
grepai search "shared styles or design tokens" --json --compact 2>/dev/null || grep -rn "color:\|font-size:\|border-radius:\|--" frontend/src/ --include="*.vue" | head -20
```

## Step 2: Analyze and identify opportunities

Look for issues in **two categories**: visual coherence AND code quality.

### A. Visual / Design system

#### Component extraction
- **Repeated HTML patterns** across pages → extract to shared components
- **Same visual block** in multiple states → shared component
- **Variation of the same concept** (card with different content) → component with slots

#### Design system coherence
- **Inconsistent colors** — same concept with different colors across pages
- **Inconsistent spacing** — margins/paddings that drift between components
- **Inconsistent typography** — font sizes, weights that vary for similar elements
- **Inconsistent interactions** — buttons that look different for the same action type

#### CSS organization
- **Duplicated CSS** across `.vue` files → extract to shared styles or components
- **Magic values** (raw hex colors, pixel values) → design tokens / CSS variables
- **Overly specific selectors** → simplify

#### UX coherence
- **Same action, different pattern** — delete confirmation in one place, instant delete in another
- **Inconsistent feedback** — loading spinner here, skeleton there, nothing elsewhere
- **Navigation patterns** — back button logic varies between pages

### B. Vue.js code quality

#### TypeScript / Type safety
- **Comment-based types** (`// 'loading' | 'ready' | ...`) → should use TypeScript or JSDoc `@type` annotations
- **Untyped props / emits** → should use `defineProps<{}>()` and `defineEmits<{}>()`
- **Untyped API responses** → should define interfaces or use Zod/Valibot for runtime validation

#### State management
- **Hand-rolled reactive stores** (`reactive()` + exported functions) → should use Pinia
- **State scattered across components** → should centralize in stores where appropriate
- **State machines via string refs** (`ref('loading')`) → evaluate if a proper state machine pattern is needed

#### Composables & API patterns
- **API calls directly in component handlers** → extract to composables (`useXxx`)
- **No loading/error pattern** → use a standard composable pattern (`useAsyncData` or similar)
- **Duplicated fetch logic** → extract shared API composable

#### Component architecture
- **Giant single-file components** (>200 lines of template) → decompose into smaller components
- **Business logic in templates** (complex `v-if` chains, inline calculations) → move to computed or composables
- **Props drilling** → consider provide/inject or stores

## Step 3: Present observations to user

**Do NOT start coding. Present your observations first.**

> Voici ce que j'ai identifié :
>
> **Composants à extraire :**
> 1. {pattern} (used in {pages}) → `components/{Name}.vue`
>
> **Incohérences design system :**
> 1. {observation} → {proposed fix}
>
> **CSS à factoriser :**
> 1. {observation} → {proposed change}
>
> **Code Vue à améliorer :**
> 1. {observation} → {proposed fix}
>
> **Architecture à revoir :**
> 1. {observation} → {proposed fix}
>
> Tu valides ? Tu veux prioriser ou retirer quelque chose ?

**Wait for explicit validation before touching any code.**

## Step 4: Refactor incrementally

**One change at a time.** Use `frontend-design` for each visual change.

After each change:
- Visually verify the result (screenshot if possible)
- Check that other components are not broken
- Confirm design coherence is maintained or improved

## Step 5: Final coherence check

Review all pages together:

```bash
find frontend/src -name "*.vue" -path "*/pages/*" -o -name "*.vue" -path "*/components/*" | head -30
```

Verify:
- [ ] Shared components are used consistently
- [ ] Colors, spacing, typography follow the same tokens
- [ ] Same actions have the same visual pattern everywhere
- [ ] No orphaned CSS (styles defined but not used)
- [ ] No duplicated CSS blocks across files
- [ ] No hand-rolled patterns where Vue conventions exist (Pinia, composables, TypeScript)
- [ ] No comment-based types where real types should be used
- [ ] API calls use a consistent pattern (composables, not inline)

## Step 6: Done

> Refactoring front terminé.
>
> Changements :
> - {list}
>
> Composants partagés :
> - {list}
>
> Améliorations code :
> - {list}
>
> Tu peux `git commit`.
