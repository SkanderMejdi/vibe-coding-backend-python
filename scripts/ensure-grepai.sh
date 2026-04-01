#!/bin/bash
# Ensure grepai is ready with mcp-node-1 backend.
# Called by Claude Code SessionStart hook.

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_NAME="$(basename "$PROJECT_DIR")"
MCP_NODE="192.168.1.172"

# Defaults (override via env)
GREPAI_DSN="${GREPAI_DSN:-postgres://mcp:${GREPAI_POSTGRES_PASSWORD}@${MCP_NODE}:5432/grepai}"
GREPAI_OLLAMA_URL="${GREPAI_OLLAMA_URL:-http://${MCP_NODE}:11434}"

# 1. Check installation
if ! command -v grepai &> /dev/null; then
    echo "⚠️  grepai not installed. Run: curl -sSL https://raw.githubusercontent.com/yoanbernabeu/grepai/main/install.sh | sh"
    exit 0
fi

# 2. Check mcp-node-1 connectivity
if ! curl -sf --max-time 5 "$GREPAI_OLLAMA_URL" > /dev/null 2>&1; then
    echo "⚠️  mcp-node-1 ($MCP_NODE) unreachable. Is it powered on?"
    exit 0
fi

# 3. Create workspace if needed
if ! grepai workspace show "$PROJECT_NAME" > /dev/null 2>&1; then
    if [ -z "$GREPAI_POSTGRES_PASSWORD" ]; then
        echo "⚠️  Workspace '$PROJECT_NAME' not found. Set GREPAI_POSTGRES_PASSWORD to create it."
        echo "   export GREPAI_POSTGRES_PASSWORD=<password>"
        exit 0
    fi
    echo "🔧 Creating workspace '$PROJECT_NAME' on mcp-node-1..."
    grepai workspace create "$PROJECT_NAME" \
        --backend postgres \
        --dsn "$GREPAI_DSN" \
        --provider ollama \
        --endpoint "$GREPAI_OLLAMA_URL" \
        --model nomic-embed-text \
        --yes > /dev/null 2>&1
    grepai workspace add "$PROJECT_NAME" "$PROJECT_DIR" > /dev/null 2>&1
    echo "✅ Workspace '$PROJECT_NAME' created"
fi

# 4. Start watcher if not already running
if grepai watch --workspace "$PROJECT_NAME" --status 2>&1 | grep -q "not running"; then
    grepai watch --workspace "$PROJECT_NAME" --background > /dev/null 2>&1
    echo "✅ grepai watch started for workspace '$PROJECT_NAME'"
else
    echo "✅ grepai watch already running for '$PROJECT_NAME'"
fi
