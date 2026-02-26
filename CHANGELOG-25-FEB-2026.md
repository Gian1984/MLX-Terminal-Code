# Changelog — February 25, 2026

## Version 3.0 — Major Architecture & UX Overhaul

**Release Date:** February 25, 2026

This release brings 21 improvements plus critical bug fixes, transforming MLX-CODE from a basic chat interface into a professional-grade local coding assistant.

---

### Streaming Output

- **Real-time token generation** using `mlx_lm.stream_generate()`
- Tokens appear as they're generated (no more waiting for full response)
- Speed display after each response: `[142 tokens, 23.5 tok/s]`
- "Thinking..." indicator while prompt is being processed

### Universal Model Compatibility

- Replaced hardcoded Qwen template with `tokenizer.apply_chat_template()`
- Works correctly with **any model**: Qwen, Llama, Mistral, Phi, DeepSeek, CodeLlama
- Automatic fallback to Qwen-style template for older tokenizers

### Compact System Prompt

- Reduced system prompt from ~2500 to ~400 characters
- **Fixes repeated/stuck responses** on small models (1.5B, 3B)
- Current date injected into prompt (model now knows today's date)
- Context moved to system prompt — no longer duplicated in every user turn

### Command Dispatcher Architecture

- **Major refactor**: replaced ~450-line if/elif chain with clean dispatcher pattern
- New `AppState` class for shared mutable state
- 25+ `cmd_*` handler functions extracted from monolithic main loop
- `COMMAND_DISPATCH` dictionary maps commands to handlers
- Main loop reduced to ~50 lines

### New Commands

| Command | Description |
|---------|-------------|
| `/git` | Git integration (status, diff, log, branch, add, commit, stash) |
| `/run <cmd>` | Execute shell commands with output capture |
| `/run <cmd> --ai` | Execute and send output to AI for analysis |
| `/find <pattern>` | Glob-style file search across project |
| `/replace <file> "old" "new"` | Find and replace with diff preview and confirmation |
| `/copy` | Copy last code block to clipboard (via `pbcopy`) |
| `/undo` | Undo last file modification (restores from backup) |

### Context Management

- **Budget enforcement**: `MAX_FILE_CONTEXT_CHARS = 15000` prevents prompt overflow
- Reversed file iteration (most recently opened = highest priority)
- Progress bar in `/context` display
- File truncation warnings when files exceed size limits

### Enhanced `/open` Command

- Support for line ranges: `/open file.py:10-50`
- Line numbers displayed in output
- File size information shown

### Auto-save Conversations

- Conversation automatically saved to `~/.mlx-code/autosave.json` after each exchange
- Restore prompt on startup if previous session was interrupted
- Clean exit clears autosave

### Per-project Configuration

- Support for `.mlx-code.json` in project root
- Override model, max_tokens, ctx_chars, auto_context per project
- Applied automatically on startup and when changing directories

### Improved Markdown Rendering

- New `StreamRenderer` class with line-buffered output
- Colored headers, bullet lists, numbered lists, blockquotes
- Inline formatting: **bold**, *italic*, `code`
- Code blocks highlighted in distinct color
- Horizontal rules rendered

### Model Switch Fix

- `reload_session()` now preserves conversation history, opened files, and stats
- No more lost context when switching models mid-session

### Repetition Detection

- Detects stuck generation loops (repeated patterns of 30-80 chars)
- Automatically stops generation and notifies user
- Checks every 50 tokens after 150 tokens generated

### Security Fixes

- **Command injection fix**: `/edit` now uses `subprocess.run([editor, file])` instead of `os.system(f"{editor} {file}")`
- Fixed 3 bare `except:` clauses changed to `except Exception:`
- `/run` command has 60-second timeout and 5000-char output limit

### Direct Venv Execution

- Shebang changed from `#!/usr/bin/env python3` to `#!/Users/gianlucatiengo/.mlx-env/bin/python3`
- **No more `source ~/.mlx-env/bin/activate` needed** — just run `~/mlx-code` directly

### UX Improvements

- "Thinking..." indicator while model processes prompt
- Multi-line input hint: *(press Enter on empty line to send, or keep typing for multi-line)*
- `sys.stdout.flush()` calls ensure output appears immediately
- Real token counting for both prompt and generated tokens

---

## Summary of Changes

| Category | Count |
|----------|-------|
| New commands | 7 (`/git`, `/run`, `/find`, `/replace`, `/copy`, `/undo`, `/run --ai`) |
| Security fixes | 4 (command injection, bare excepts) |
| Architecture improvements | 3 (dispatcher, AppState, StreamRenderer) |
| UX improvements | 6 (streaming, thinking indicator, hints, flush, markdown, autosave) |
| Bug fixes | 3 (model switch, repetition loops, stdout buffering) |
| **Total improvements** | **21+** |

## File Changes

- `mlx-code-v2.py`: ~2275 lines -> ~3000 lines (complete rewrite of core systems)
- Dependencies: added `prompt-toolkit` (installed in `~/.mlx-env`)

## How to Update

```bash
# Backup old version
cp ~/mlx-code ~/mlx-code.backup

# Copy new version
cp ~/Documents/Progetti/MLX-Terminal-Code/mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code

# Install new dependency
~/.mlx-env/bin/pip install prompt-toolkit

# Run (no env activation needed!)
~/mlx-code
```

---

**Contributors:**
- **Gianluca** — Project owner
