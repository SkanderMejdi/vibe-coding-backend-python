---
description: "Frontend: refactor components, extract shared UI, verify design system coherence. Optional."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, grepai
---

# Front Refactor: $ARGUMENTS

**IMPORTANT: Always use the `frontend-design` skill when touching visual code. Design quality must not regress.**

## Step 1: Inventory current state

```bash
ls maquettes/components/ 2>/dev/null || echo "No shared components yet"
```

```bash
ls maquettes/*/*.vue 2>/dev/null
```

```bash
grepai search "shared styles or design tokens" --json --compact 2>/dev/null || grep -rn "color:\|font-size:\|border-radius:\|--" maquettes/ --include="*.vue" | head -20
```

## Step 2: Analyze and identify opportunities

Look for:

### Component extraction
- **Repeated HTML patterns** across mockups → extract to `maquettes/components/`
- **Same visual block** in multiple states → shared component
- **Variation of the same concept** (card with different content) → component with slots

### Design system coherence
- **Inconsistent colors** — same concept with different colors across pages
- **Inconsistent spacing** — margins/paddings that drift between components
- **Inconsistent typography** — font sizes, weights that vary for similar elements
- **Inconsistent interactions** — buttons that look different for the same action type

### CSS organization
- **Duplicated CSS** across `.vue` files → extract to shared styles
- **Magic values** (raw hex colors, pixel values) → design tokens / CSS variables
- **Overly specific selectors** → simplify

### UX coherence
- **Same action, different pattern** — delete confirmation in one place, instant delete in another
- **Inconsistent feedback** — loading spinner here, skeleton there, nothing elsewhere
- **Navigation patterns** — back button logic varies between pages

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
> **UX à harmoniser :**
> 1. {observation} → {proposed fix}
>
> Tu valides ? Tu veux prioriser ou retirer quelque chose ?

**Wait for explicit validation before touching any code.**

## Step 4: Refactor incrementally

**One change at a time.** Use `frontend-design` for each visual change.

After each change:
- Visually verify the result (screenshot if possible)
- Check that other mockups/components are not broken
- Confirm design coherence is maintained or improved

## Step 5: Final coherence check

Review all pages together:

```bash
cat maquettes/*/*.vue maquettes/components/*.vue 2>/dev/null
```

Verify:
- [ ] Shared components are used consistently
- [ ] Colors, spacing, typography follow the same tokens
- [ ] Same actions have the same visual pattern everywhere
- [ ] No orphaned CSS (styles defined but not used)

## Step 6: Done

> Refactoring front terminé.
>
> Changements :
> - {list}
>
> Composants partagés :
> - `maquettes/components/{list}`
>
> Tu peux `git commit`.
