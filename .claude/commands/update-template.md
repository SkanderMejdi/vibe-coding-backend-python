---
description: "Update this project's workflow files from the vibe-coding template. Merges changes intelligently, preserving project-specific customizations."
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Update Template

**Goal: Sync workflow files from the vibe-coding-backend-python template into this project, without overwriting project-specific customizations.**

## Step 1: Locate template source

```bash
TEMPLATE_DIR="${VIBE_TEMPLATE_DIR:-$HOME/Code/vibe-coding-backend-python}"
echo "Template source: $TEMPLATE_DIR"
ls "$TEMPLATE_DIR/.claude/commands/" "$TEMPLATE_DIR/scripts/" "$TEMPLATE_DIR/.mcp.json" "$TEMPLATE_DIR/CLAUDE.md" 2>/dev/null | head -30
```

If template not found, ask the user:
> Template introuvable dans `~/Code/vibe-coding-backend-python`. Quel est le chemin ?

## Step 2: Diff all workflow files

Compare template files with current project files. For each file, classify as:
- **Identical** — no update needed
- **Template updated** — template has changes the project doesn't have
- **Project customized** — project has diverged (custom settings, paths, etc.)
- **Both changed** — needs manual merge
- **Missing** — exists in template but not in project

### Files to sync

**Always sync (overwrite OK):**
- `.claude/commands/back-clarify.md`
- `.claude/commands/back-specify.md`
- `.claude/commands/back-implement.md`
- `.claude/commands/back-refactor.md`
- `.claude/commands/front-clarify.md`
- `.claude/commands/front-maquette.md`
- `.claude/commands/front-contract.md`
- `.claude/commands/front-dynamize.md`
- `.claude/commands/front-refactor.md`
- `.claude/commands/audit-project.md`
- `.claude/commands/update-template.md` (this file)
- `.claude/skills/hexagonal-arch/SKILL.md`
- `.claude/hooks/check_architecture.py`
- `scripts/ensure-grepai.sh`
- `scripts/check_contract.py`
- `scripts/pre-commit`
- `scripts/install-hooks.sh`

**Merge (preserve project customizations):**
- `.mcp.json` — merge mcpServers (keep project-specific servers like playwright with custom args)
- `.claude/settings.json` — merge permissions, hooks, mcpServers (keep project-specific entries)
- `CLAUDE.md` — merge workflow sections (keep project-specific sections)
- `Makefile` — add missing targets (keep project-specific targets)

**Never overwrite:**
- `pyproject.toml`
- `docker-compose.*.yml`
- `.claude/settings.local.json`

```bash
# For each sync file, show diff
for f in .claude/commands/back-clarify.md .claude/commands/back-specify.md .claude/commands/back-implement.md .claude/commands/back-refactor.md .claude/commands/front-clarify.md .claude/commands/front-maquette.md .claude/commands/front-contract.md .claude/commands/front-dynamize.md .claude/commands/front-refactor.md .claude/commands/audit-project.md .claude/skills/hexagonal-arch/SKILL.md .claude/hooks/check_architecture.py scripts/ensure-grepai.sh scripts/check_contract.py scripts/pre-commit scripts/install-hooks.sh; do
    if [ -f "$TEMPLATE_DIR/$f" ] && [ -f "$f" ]; then
        if ! diff -q "$TEMPLATE_DIR/$f" "$f" > /dev/null 2>&1; then
            echo "CHANGED: $f"
        fi
    elif [ -f "$TEMPLATE_DIR/$f" ]; then
        echo "NEW: $f"
    fi
done
```

## Step 3: Present changes to user

> **Fichiers à mettre à jour :**
>
> Copie directe :
> - {list of CHANGED and NEW files from "always sync"}
>
> Merge nécessaire :
> - `.mcp.json` — {describe what changed in template}
> - `.claude/settings.json` — {describe what changed}
> - `CLAUDE.md` — {describe what changed}
>
> Rien à faire :
> - {list of identical files}
>
> On y va ?

**Wait for user confirmation.**

## Step 4: Apply updates

### Direct copies

For each "always sync" file that needs updating:

```bash
cp "$TEMPLATE_DIR/{file}" "{file}"
```

### Merges

For each "merge" file, read BOTH versions and apply template changes while preserving project customizations:

**`.mcp.json`:**
- Keep all project-specific mcpServers (e.g. playwright with custom args)
- Update grepai config from template
- Add new servers from template (e.g. memory) if missing

**`.claude/settings.json`:**
- Keep project-specific permissions
- Update hooks from template
- Update mcpServers (same logic as .mcp.json)
- Keep project-specific hooks

**`CLAUDE.md`:**
- Keep project-specific sections (anything not from template)
- Update template sections (Philosophy, Commands, Architecture, Conventions, Flow, Git Workflow, grepai, Memory)
- Preserve project-specific additions

**`Makefile`:**
- Keep all existing targets
- Add new targets from template that don't exist

## Step 5: Verify

```bash
# Check JSON files are valid
python3 -c "import json; json.load(open('.mcp.json'))" && echo ".mcp.json OK" || echo ".mcp.json INVALID"
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "settings.json OK" || echo "settings.json INVALID"

# Check scripts are executable
ls -la scripts/ensure-grepai.sh scripts/pre-commit scripts/install-hooks.sh
chmod +x scripts/ensure-grepai.sh scripts/pre-commit scripts/install-hooks.sh 2>/dev/null
```

## Step 6: Done

> Template mis à jour.
>
> Fichiers copiés :
> - {list}
>
> Fichiers mergés :
> - {list with what was preserved}
>
> Nouveaux fichiers :
> - {list}
>
> Tu peux `git diff` pour vérifier, puis `git commit -m "[infra] update vibe-coding template"`.
