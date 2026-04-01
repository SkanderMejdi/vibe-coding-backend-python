# Importing this workflow into a project

Instructions for a Claude Code session to import the vibe-coding workflow files into a target project.

## Source repository

Clone the template:

```bash
git clone git@github.com:SkanderMejdi/vibe-coding-backend-python.git /tmp/vibe-template
```

## Files to import

### 1. `.claude/` directory

Import the entire `.claude/` directory from the template:

```
.claude/
  commands/          # Workflow skills
  skills/            # Architecture reference
  hooks/             # Architecture validation hook
  agents/            # Deep exploration agent
  settings.json      # Permissions, MCP servers, hooks config
```

**If the target project already has a `.claude/` directory:**
- **`settings.json`** — MERGE, don't overwrite. The target may have its own permissions, hooks, or MCP servers. Merge the `permissions`, `hooks`, and `mcpServers` sections. Show the user the diff and ask which entries to keep.
- **`commands/`** — copy all `.md` files. If a command with the same name already exists, show both versions to the user and ask which to keep.
- **Everything else** — copy if it doesn't exist, ask the user if it does.

### 2. `scripts/`

Import these scripts:

```
scripts/
  pre-commit
  install-hooks.sh
  check_contract.py
  ensure-grepai.sh
```

**If `scripts/` already exists**, add the files without overwriting existing ones. If a file with the same name exists, show the user and propose a merge strategy.

### 3. `Makefile`

Import the Makefile. **If one already exists**, show the user the new targets and propose adding them to the existing Makefile rather than replacing it. The required targets are: `test`, `test-quick`, `lint`, `typecheck`, `format`, `openapi`, `check-contract`.

### 4. `CLAUDE.md`

Import `CLAUDE.md`. **If one already exists**, merge the content — the target project's existing instructions should be preserved. Add the workflow sections (Philosophy, Commands, Architecture, Conventions, Flow, Git Workflow) alongside existing content.

### 5. `pyproject.toml`

Do NOT overwrite. Check that the target project has the required dev dependencies (`pytest`, `black`, `ruff`, `mypy`) and the tool configs (`[tool.black]`, `[tool.mypy]`, `[tool.pytest]`). If missing, propose adding them.

### 6. Docker Compose

Import `docker-compose.test.yml` if the target project doesn't have one. If it does, check that it has a Postgres test service and propose adjustments if needed.

## Post-import initialization

1. Run `./scripts/install-hooks.sh` to install the git pre-commit hook
2. **mcp-node-1 backend** (grepai + memory):
   - Ensure mcp-node-1 is running (192.168.1.172)
   - Install grepai: `curl -sSL https://raw.githubusercontent.com/yoanbernabeu/grepai/main/install.sh | sh`
   - Set the PostgreSQL password: `export GREPAI_POSTGRES_PASSWORD=<password>`
   - The `SessionStart` hook auto-creates the workspace and starts the watcher
   - Memory (Ogham) is configured via `.mcp.json` (SSE, no setup needed)
3. Verify `make test` works. If not, adapt the Makefile to the target project's test runner.

## Conflict resolution principle

**Never overwrite existing files silently.** For every conflict:
1. Show the user what exists and what the template provides
2. Propose a merge strategy (add sections, rename, keep both)
3. Wait for the user's decision before proceeding
