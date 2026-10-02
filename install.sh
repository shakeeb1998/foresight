#!/usr/bin/env bash
# Install the foresight skill for Claude Code, Cursor and any Agent Skills compatible agent.
#
#   ./install.sh                     # auto-detect: links into every tool found (~/.claude, ~/.cursor)
#   ./install.sh --cursor            # Cursor only        -> ~/.cursor/skills/foresight (+ foresight-relearn)
#   ./install.sh --claude            # Claude Code only   -> ~/.claude/skills/foresight (+ foresight-relearn)
#   ./install.sh --agents            # generic standard   -> ~/.agents/skills/foresight
#   ./install.sh --project <dir>     # also add the Cursor rule to <dir>/.cursor/rules/foresight.mdc
#   ./install.sh --copy              # copy instead of symlink (e.g. synced or read-only homes)
#   ./install.sh --force             # replace an existing non-symlink install (it is backed up first)
#   ./install.sh --hooks             # also install the binding-guard gates into ~/.claude/settings.json
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$REPO/plugins/foresight/skills"
targets=() project="" mode="link" force=0 hooks=0

while [ $# -gt 0 ]; do
  case "$1" in
    --claude) targets+=(claude) ;;
    --cursor) targets+=(cursor) ;;
    --agents) targets+=(agents) ;;
    --project) project="${2:?--project needs a directory}"; shift ;;
    --copy) mode="copy" ;;
    --force) force=1 ;;
    --hooks) hooks=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ ${#targets[@]} -eq 0 ]; then
  [ -d "$HOME/.claude" ] && targets+=(claude)
  [ -d "$HOME/.cursor" ] && targets+=(cursor)
  [ ${#targets[@]} -eq 0 ] && targets+=(agents)
fi

place() {  # place <skill-name> <dest-dir>
  local src="$SKILLS/$1" dest="$2/$1"
  mkdir -p "$2"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    if [ $force -eq 0 ]; then
      echo "  skip  $dest exists and is not a symlink (use --force to replace; it is backed up)"; return
    fi
    mv "$dest" "$dest.bak.$(date +%Y%m%d%H%M%S)"
  fi
  if [ "$mode" = "copy" ]; then rm -rf "$dest"; cp -R "$src" "$dest"; else ln -sfn "$src" "$dest"; fi
  echo "  ok    $dest"
}

for t in "${targets[@]}"; do
  case "$t" in
    claude)
      echo "Claude Code:"
      place foresight "$HOME/.claude/skills"
      place foresight-relearn "$HOME/.claude/skills"   # relearn mines Claude Code transcripts
      ;;
    cursor)
      echo "Cursor:"
      place foresight "$HOME/.cursor/skills"
      place foresight-relearn "$HOME/.cursor/skills"   # relearn mines Cursor agent transcripts
      ;;
    agents)
      echo "Agent Skills (~/.agents):"
      place foresight "$HOME/.agents/skills"
      ;;
  esac
done

if [ -n "$project" ]; then
  mkdir -p "$project/.cursor/rules"
  cp "$REPO/plugins/foresight/rules/foresight.mdc" "$project/.cursor/rules/foresight.mdc"
  echo "Cursor rule: $project/.cursor/rules/foresight.mdc"
fi

if [ $hooks -eq 1 ]; then
  echo "Claude Code gates:"
  python3 "$REPO/plugins/foresight/hooks/install_hooks.py" --fs "$HOME/.claude/skills/foresight/fs.py"
fi

echo
echo "Check:"
python3 "$SKILLS/foresight/fs.py" match "add a paginated list endpoint with per-row counts" | head -4
