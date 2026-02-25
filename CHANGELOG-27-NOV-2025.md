# Changelog — November 27, 2025

## Version 2.1 — Model Management Update

### New Features

#### Complete Model Management
- **`/models`** — List all available models with status (installed/not installed)
- **`/installed`** — Show installed models with disk usage
- **`/download <model>`** — Download models on-demand without restarting
- **`/delete <model>`** — Delete models to free disk space

#### 20+ Models Optimized for M4 Pro 24GB

**Qwen Coder (Best for Code):**
- `/q1.5b` — Qwen 1.5B (~1GB) - Quick testing
- `/q3b` — Qwen 3B (~2GB) - Fast coding
- `/q7b` — Qwen 7B (~4GB) - Recommended
- `/q14b` — Qwen 14B (~9GB) - Advanced
- **`/q32b`** — **Qwen 32B (~17GB) - Best Quality** NEW!

**DeepSeek Coder (Excellent):**
- `/ds1.3b` — DeepSeek 1.3B (~1GB)
- `/ds6.7b` — DeepSeek 6.7B (~4GB)
- `/ds` — DeepSeek V2 Lite (~9GB)

**Llama 3 (Strong Reasoning):**
- `/llama3-8b` — Llama 3 8B (~5GB) NEW!
- `/l3-8b` — Alias for Llama 3 8B

**Phi (Efficient):**
- `/phi3` — Phi-3 Mini (~2GB) NEW!
- `/phi` — Alias for Phi-3

**CodeLlama (Code Specialist):**
- `/codellama` — CodeLlama 13B (~7GB) NEW!
- `/cl13b` — Alias for CodeLlama 13B

**Mistral (Versatile):**
- `/mistral` — Mistral 7B (~4GB)
- `/m7b` — Alias for Mistral 7B

#### Advanced Terminal Input (prompt-toolkit)
- **Command History** — Navigate with ↑/↓ through previous commands
- **Cursor Navigation** — Move cursor with ←/→ to edit text
- **Tab Completion** — Auto-complete commands (e.g., `/mod` + Tab → `/models`)
- **Multi-line Paste** — Paste multi-line code without issues
- **Smart Ctrl+C** — Clears buffer without showing ^C
- **Persistent History** — Saves all commands to `~/.mlx-code/command_history.txt`

**Installation:**
```bash
pip install prompt-toolkit
# or
pip install -r requirements.txt
```

**Benefits:**
- No more strange symbols when using arrow keys
- No more issues when pasting code
- Ctrl+C works correctly (doesn't show ^C)
- Professional experience like modern zsh/bash

### Technical Improvements

#### Model Helpers
```python
# New functions added:
- list_installed_models() → List installed models
- delete_model(name) → Delete model from cache
- get_model_ram_requirement(name) → Estimate RAM needed
- list_available_models() → Complete metadata for all models
- get_model_size_estimate(name) → Improved download size estimate
```

#### Missing Import
- Added `import subprocess` required for `download_model_with_git_lfs()`

#### Dynamic Aliases
- Fully dynamic alias system: all aliases in `MODEL_ALIASES` work automatically
- No longer need to hardcode `/q7b`, `/q3b` etc. in the code

### New Documentation

#### **GUIDE-M4-PRO-24GB.md** (NEW!)
Complete guide to maximize M4 Pro with 24GB RAM:
- Complete model overview
- Commands and practical examples
- Performance comparison
- Recommended optimal setup
- Tips & tricks for M4 Pro

#### Added Sections:
- When to use which model
- Optimized workflows
- M4 Pro specific FAQ
- 3-model complementary setup

### UI Improvements

#### Updated Help
```
MODEL & SETTINGS:
  /model <id>            Switch model
  /models                List available models      NEW
  /installed             Show installed models      NEW
  /download <model>      Download a model          NEW
  /delete <model>        Delete a model from cache NEW

  Quick model switches (M4 Pro 24GB optimized):
    /q1.5b (1GB)   /q3b (2GB)    /q7b (4GB)    /q14b (9GB)   /q32b (17GB)
    /ds1.3b (1GB)  /ds6.7b (4GB)  /ds (9GB)     /deepseek (9GB)
    /phi3 (2GB)    /llama3-8b (5GB)  /mistral (4GB)  /codellama (7GB)
```

#### `/models` Command Output
```
════════════════════════════════════════════════════════════════════════════════
Available Models (M4 Pro 24GB Optimized)
════════════════════════════════════════════════════════════════════════════════

Qwen Coder (Recommended for Code)
  /q1.5b          ~1.0GB   ~2-3GB RAM  Installed
  /q3b            ~1.9GB   ~3-4GB RAM  Not installed
  /q7b            ~4.3GB   ~5-7GB RAM  Installed
  /q14b           ~8.5GB  ~10-12GB RAM  Not installed
  /q32b          ~17.0GB  ~20-22GB RAM  Installed

[... more models ...]

Usage:
  Switch model: /<alias> (e.g., /q32b)
  Download: /download <alias> (e.g., /download q32b)
  Delete: /delete <alias>
```

#### `/installed` Command Output
```
════════════════════════════════════════════════════════════════════════════════
Installed Models
════════════════════════════════════════════════════════════════════════════════

  mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit              1.02GB  /q1.5b
  mlx-community/qwen2.5-coder-7b-instruct-4bit                4.28GB  /q7b
  mlx-community/Qwen2.5-Coder-32B-Instruct-4bit              17.34GB  /q32b

Total disk usage: 22.64GB
Cache location: ~/.cache/huggingface/hub/
════════════════════════════════════════════════════════════════════════════════
```

### Bug Fixes

- Fixed: `subprocess` not imported caused error in `download_model_with_git_lfs()`
- Fixed: Inaccurate model size estimate for models > 14B

### Breaking Changes

None! All new features are backwards-compatible.

### Statistics

- **+20 models** available (before: 9, now: 29)
- **+4 commands** for model management
- **+100 lines** of model management code
- **+500 lines** of documentation (GUIDE-M4-PRO-24GB.md + GUIDE-M1-16GB.md)
- **+1 optional dependency** (prompt-toolkit for advanced input)
- **+50 lines** for prompt-toolkit integration with graceful fallback

---

## How to Update

### If you already have mlx-code installed:

```bash
cd ~/Documents/Progetti/MLX-Terminal-Code
git pull origin main

# Install updated dependencies (recommended)
source ~/.mlx-env/bin/activate
pip install -r requirements.txt
# or just prompt-toolkit:
pip install prompt-toolkit

# Copy new version
cp mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code

# Test
~/mlx-code
> /models
```

### First Installation:

```bash
cd ~/Documents/Progetti/MLX-Terminal-Code

# Install dependencies (recommended)
source ~/.mlx-env/bin/activate
pip install -r requirements.txt

# Copy and launch mlx-code
cp mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code
~/mlx-code
```

---

## Quick Start for M4 Pro 24GB

```bash
# Launch mlx-code
~/mlx-code

# See all models
> /models

# Download the most powerful (Qwen 32B)
> /download q32b
# Wait ~15 minutes

# Switch to Qwen 32B
> /q32b

# Or download DeepSeek (faster)
> /download ds
> /ds
```

---

## Upcoming Features (Roadmap)

- [ ] Automatic model comparison (`/benchmark`)
- [ ] Auto-switch based on query complexity
- [ ] Background downloads
- [ ] Custom model support
- [ ] Web interface (optional)
- [ ] Integrated model zoo

---

## Contributors

- **Gianluca** — Model management system & M4 Pro optimization
- **Claude** — Documentation & testing

---

## Release Notes

**Date:** November 27, 2025
**Version:** 2.1.0
**Python:** 3.12+
**MLX:** 0.20.0+
**Compatible:** M1/M2/M3/M4 (8GB/16GB/24GB/48GB RAM)

---

**Happy coding with mlx-code v2.1!**
