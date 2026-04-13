#!/usr/bin/env bash
# =============================================================================
# OpenClaw Universal Install Script
# Supports: macOS, Linux (apt/dnf/yum), WSL2, Windows (PowerShell)
#
# Usage (one-liner):
#   curl -fsSL https://openclaw.ai/install.sh | bash
#
# Or download and run locally:
#   bash install-openclaw.sh [options]
#
# Options:
#   --with-workspace   Clone/sync your workspace from GitHub after install
#   --workspace-url    GitHub repo URL (e.g. AndrewXuTurtle/Presentasi-Andrew)
#   --skills-only      Only update skills (skip OpenClaw install)
#   --update           Update OpenClaw + workspace
#   --verify           Verify installation only
#   --help, -h         Show this help
# =============================================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERR]${NC}  $1" >&2; }

WITH_WORKSPACE=false
WORKSPACE_URL=""
SKILLS_ONLY=false
IS_UPDATE=false
VERIFY_ONLY=false

# Parse flags
while [[ $# -gt 0 ]]; do
  case $1 in
    --with-workspace) WITH_WORKSPACE=true; shift ;;
    --workspace-url)  WORKSPACE_URL="$2"; shift 2 ;;
    --skills-only)    SKILLS_ONLY=true; shift ;;
    --update)         IS_UPDATE=true; shift ;;
    --verify)         VERIFY_ONLY=true; shift ;;
    --help|-h)        grep "^#" "$0" | grep -v "^#!/\|# =================================================================\|# Options\|# Usage\|# Or downl\|# Next\|#   \|#    " | sed 's/^# //'; exit 0 ;;
    *)                shift ;;
  esac
done

# ---- Detect OS ----
detect_os() {
  case "$(uname -s)" in
    Darwin)          echo "macos" ;;
    Linux)
      if grep -qEi "(Microsoft|WSL)" /proc/version 2>/dev/null; then
        echo "wsl"; else echo "linux"; fi ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)                     echo "unknown" ;;
  esac
}

OS_TYPE=$(detect_os)
info "Detected OS: $OS_TYPE"

# =============================================================================
# VERIFY MODE
# =============================================================================
if $VERIFY_ONLY; then
  echo ""
  info "=== Verifying OpenClaw Installation ==="
  if command -v openclaw &>/dev/null; then
    VER=$(openclaw --version 2>/dev/null || echo "unknown")
    success "OpenClaw CLI: $VER"
  else
    error "OpenClaw CLI: not found in PATH"
  fi
  if command -v node &>/dev/null; then
    success "Node.js: $(node --version)"
  else
    warn "Node.js: not found"
  fi
  if command -v openclaw &>/dev/null && openclaw gateway status &>/dev/null; then
    success "Gateway: running ✅"
  else
    warn "Gateway: not running (run: openclaw gateway start)"
  fi
  if [[ -d "$HOME/.openclaw/workspace" ]]; then
    WS_SIZE=$(du -sh "$HOME/.openclaw/workspace" 2>/dev/null | cut -f1)
    success "Workspace: exists ($WS_SIZE)"
  else
    warn "Workspace: not found"
  fi
  echo ""
  exit 0
fi

# =============================================================================
# SKILLS ONLY MODE
# =============================================================================
if $SKILLS_ONLY; then
  info "Updating OpenClaw skills..."
  if command -v openclaw &>/dev/null; then
    openclaw skills update 2>/dev/null || warn "openclaw skills update failed"
  fi
  if command -v npx &>/dev/null; then
    npx clawhub sync 2>/dev/null || true
  fi
  success "Skills update complete."
  exit 0
fi

# =============================================================================
# ENSURE OPENCLAW IS INSTALLED
# =============================================================================
install_openclaw() {
  info "Installing OpenClaw..."

  case $OS_TYPE in
    macos|linux|wsl)
      info "Running official install.sh (macOS/Linux/WSL)..."
      curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --no-onboard
      ;;
    windows)
      info "Running official install.ps1 (Windows PowerShell)..."
      powershell -ExecutionPolicy Bypass -Command "& ([scriptblock]::Create((Invoke-WebRequest -useb https://openclaw.ai/install.ps1).Content))) -NoOnboard"
      ;;
    *)
      error "Unsupported OS: $OS_TYPE"
      exit 1
      ;;
  esac
}

if ! command -v openclaw &>/dev/null; then
  install_openclaw
else
  if $IS_UPDATE; then
    info "OpenClaw found — updating..."
    openclaw update 2>/dev/null || install_openclaw
  else
    success "OpenClaw already installed ($(openclaw --version 2>/dev/null || echo '?'))"
  fi
fi

# Ensure openclaw is in PATH for this session
export PATH="$(npm prefix -g 2>/dev/null)/bin:$PATH"
if ! command -v openclaw &>/dev/null && [[ -f "$HOME/.openclaw/bin/openclaw" ]]; then
  export PATH="$HOME/.openclaw/bin:$PATH"
fi

# =============================================================================
# START GATEWAY
# =============================================================================
if command -v openclaw &>/dev/null; then
  if ! openclaw gateway status &>/dev/null; then
    info "Starting OpenClaw gateway..."
    openclaw gateway start 2>/dev/null || warn "Could not auto-start gateway — run 'openclaw gateway start' manually"
  else
    success "Gateway already running"
  fi
fi

# =============================================================================
# SYNC WORKSPACE FROM GITHUB
# =============================================================================
if $WITH_WORKSPACE || [[ -n "$WORKSPACE_URL" ]]; then
  info "Syncing workspace from GitHub..."
  ws_dir="$HOME/.openclaw/workspace"

  # Try to get URL from existing workspace git remote
  if [[ -z "$WORKSPACE_URL" ]] && [[ -d "$ws_dir/.git" ]]; then
    remote_url=$(git -C "$ws_dir" remote get-url origin 2>/dev/null || true)
    if [[ -n "$remote_url" ]]; then
      # Convert git@github.com:user/repo to https://github.com/user/repo
      WORKSPACE_URL=$(echo "$remote_url" | sed 's/git@github\.com:/https:\/\/github.com\//' | sed 's/\.git$//')
    fi
  fi

  if [[ -d "$ws_dir/.git" ]]; then
    info "Workspace exists — pulling latest..."
    git -C "$ws_dir" pull origin main 2>/dev/null || git -C "$ws_dir" pull 2>/dev/null || \
      warn "Pull failed (auth issue or no remote)"
  elif [[ -n "$WORKSPACE_URL" ]]; then
    info "Cloning workspace to $ws_dir..."
    git clone "$WORKSPACE_URL" "$ws_dir" 2>/dev/null || \
      warn "Clone failed (repo may be private or unreachable)"
  fi
  success "Workspace sync done."
fi

# =============================================================================
# FINAL VERIFICATION
# =============================================================================
echo ""
info "=== Final Check ==="
if command -v openclaw &>/dev/null; then
  success "OpenClaw CLI: $(openclaw --version 2>/dev/null || echo '?')"
else
  error "OpenClaw CLI: NOT in PATH — restart terminal and run 'openclaw gateway status'"
fi
if command -v node &>/dev/null; then
  success "Node.js: $(node --version)"
fi
if command -v openclaw &>/dev/null && openclaw gateway status &>/dev/null; then
  success "Gateway: running ✅"
else
  warn "Gateway: not running — run 'openclaw gateway start'"
fi
echo ""
success "All done! 🚀"
echo ""
echo "  openclaw gateway status   # check status"
echo "  openclaw onboard          # configure Telegram/WhatsApp/etc."
echo "  openclaw skills list      # list available skills"
echo "  openclaw doctor            # diagnose issues"
echo "  openclaw update            # update to latest version"
