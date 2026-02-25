# MLX-CODE Quick Start Guide

Get up and running with MLX-CODE in 10 minutes! 🚀

---

## What is MLX-CODE?

MLX-CODE is a **100% local AI coding assistant** that runs entirely on your Mac (Apple Silicon). Think of it as having ChatGPT or Claude, but for coding, completely private, and running on your own computer.

**Key Benefits:**
- 🔒 **Completely Private** - No data leaves your machine
- ⚡ **Fast** - Uses your Mac's GPU acceleration
- 🆓 **Free** - No subscriptions or API costs
- 🧠 **Context-Aware** - Understands your entire project

### 🤖 AI Models

**⚠️ Default Model: 1.5B (Demo Only) — Upgrade for Real Coding!**

MLX-CODE starts with **Qwen2.5-Coder-1.5B** by default:
- ✅ Fast setup (only 1GB download)
- ✅ Works on all Macs
- ⚠️ **Limited quality** - only for testing/demo

**🎯 Recommended Models for Real Work:**

| Model | Size | Quality | RAM | Command | Use For |
|-------|------|---------|-----|---------|---------|
| 1.5B (Default) | 1GB | ⭐⭐ | 4GB | `/q1.5b` | **Demo only** |
| 3B | 1.9GB | ⭐⭐⭐ | 6GB | `/q3b` | Light coding |
| **7B** ⭐ | 4.3GB | ⭐⭐⭐⭐ | 8GB | `/q7b` | **Recommended** |
| 14B | 8.5GB | ⭐⭐⭐⭐ | 16GB | `/q14b` | Advanced |
| **DeepSeek** ⭐⭐⭐ | 9GB | ⭐⭐⭐⭐⭐ | 16GB | `/deepseek` | **Best for code** |

**Quick Upgrade (inside MLX-CODE):**
```bash
# Best for M1/M2 16GB:
> /deepseek

# Safe choice:
> /q7b

# Multitasking:
> /q3b
```

First download takes 5-30 min, then loads instantly from cache.

**💡 Faster Downloads:** See **[DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md)** for git-lfs method (3-5x faster!).

---

## Understanding the ~/Projects Folder

### What is it?

The `~/Projects` folder is your **workspace sandbox** where MLX-CODE operates. This is a safety feature.

### Why does it exist?

**Security & Safety:**
- Prevents the AI from accidentally modifying system files
- Protects your personal documents, photos, etc.
- Keeps all your coding work organized in one place
- You control exactly what the AI can access

### How it works:

```
Your Mac
├── Documents/          ❌ MLX-CODE cannot access
├── Desktop/            ❌ MLX-CODE cannot access
├── Downloads/          ❌ MLX-CODE cannot access
├── Pictures/           ❌ MLX-CODE cannot access
└── Projects/           ✅ MLX-CODE works here!
    ├── my-website/     ✅ Accessible
    ├── python-app/     ✅ Accessible
    └── learning/       ✅ Accessible
```

### What if I already have projects elsewhere?

**Option 1: Move them** (recommended)
```bash
# Example: Move existing project
mv ~/Documents/my-app ~/Projects/my-app
```

**Option 2: Create symbolic links**
```bash
# Keep files in original location, create link in Projects
ln -s ~/Documents/my-app ~/Projects/my-app
```

**Option 3: Work with copies**
```bash
# Copy to Projects folder
cp -r ~/Documents/my-app ~/Projects/my-app
```

### Example Project Organization

Here's how you might organize your Projects folder:

```
~/Projects/
├── personal/
│   ├── my-website/
│   ├── blog/
│   └── hobby-projects/
├── work/
│   ├── client-project-1/
│   └── client-project-2/
├── learning/
│   ├── python-tutorials/
│   ├── react-practice/
│   └── rust-experiments/
└── MLX-Terminal-Code/     # This project!
    ├── mlx-code-v1.py
    ├── mlx-code-v2.py
    └── README.md
```

---

## Installation Steps

### Step 1: Check System Requirements

```bash
# Verify Apple Silicon (should show "arm64")
uname -m

# Check macOS version (need 13.0+)
sw_vers
```

**Requirements:**
- macOS 13.0 (Ventura) or later
- Apple Silicon (M1, M2, M3, or M4 chip)
- At least 8GB RAM (16GB recommended)
- 10GB free disk space (for models)

---

### Step 2: Install Python 3.12

```bash
# Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Verify installation
python3.12 --version
# Should show: Python 3.12.x
```

---

### Step 3: Create Virtual Environment

A virtual environment keeps MLX-CODE's dependencies separate from your system Python.

```bash
# Create the environment
python3.12 -m venv ~/.mlx-env
```

**Note:** As of v3.0, you do NOT need to activate the environment to run MLX-CODE. The script uses the venv Python directly. Only activate for installing packages:

```bash
source ~/.mlx-env/bin/activate  # Only needed for pip install
```

---

### Step 4: Install Required Packages

```bash
# Make sure virtual environment is active!
# You should see (mlx-env) in your prompt

# Upgrade pip
pip install --upgrade pip

# Install MLX-LM (REQUIRED - this is the AI engine)
pip install mlx-lm

# Install prompt-toolkit (RECOMMENDED - for better terminal experience)
pip install prompt-toolkit

# Install Pillow (OPTIONAL - for image support in V2)
pip install pillow

# Or install all at once:
cd ~/Projects/MLX-Terminal-Code
pip install -r requirements.txt

# Verify installation
python -c "import mlx_lm; print('✓ MLX-LM installed successfully')"
python -c "import prompt_toolkit; print('✓ prompt-toolkit installed successfully')"
```

**What is prompt-toolkit?**
- Enables command history with ↑/↓ arrows
- Allows cursor movement with ←/→ arrows
- Adds Tab completion for commands
- Fixes paste issues when pasting multi-line code
- Makes Ctrl+C work properly (no more ^C symbols!)

---

### Step 5: Create Projects Folder

```bash
# Create the main workspace
mkdir -p ~/Projects

# Verify it exists
ls -la ~ | grep Projects
```

---

### Step 6: Set Up MLX-CODE Script

You have two versions to choose from:

**Version 2 (Recommended)** - Intelligent with auto-file reading:
```bash
# Copy V2 to your home directory
cp mlx-code-v2.py ~/mlx-code

# Make it executable
chmod +x ~/mlx-code

# Verify
ls -la ~/mlx-code
```

**Version 1 (Basic)** - Stable but no auto-reading:
```bash
# If you prefer the simpler version
cp mlx-code-v1.py ~/mlx-code
chmod +x ~/mlx-code
```

---

### Step 7: Make It Accessible Globally (Optional)

```bash
# Add ~/mlx-code to your PATH
echo 'export PATH="$HOME:$PATH"' >> ~/.zshrc

# Reload your shell configuration
source ~/.zshrc

# Now you can run 'mlx-code' from anywhere!
```

---

## First Run

### 1. Navigate to Your Project

```bash
# Go to your project directory
cd ~/Documents/Progetti/your-project
# Or any directory you want to work in
```

### 2. Launch MLX-CODE

```bash
~/mlx-code
```

**No env activation needed!** (v3.0+ uses the venv Python directly via shebang)

**⏳ First Launch:**
- The AI model will download (~1GB for default 1.5B)
- This takes 1-5 minutes depending on your internet
- Only happens once - models are cached locally
- Real-time progress is shown

**✅ Success:**
You'll see the MLX-CODE banner and help text!

---

## Your First Conversation

### Example 1: Create a Simple Script

```
> create a python script that prints hello world

[Press Enter twice to send]
```

The AI will:
1. Generate the code
2. Show you a preview with syntax highlighting
3. Ask if you want to apply changes
4. Create the file with automatic backup

### Example 2: Using Templates (V2)

```
> /template test myfile.py

[Press Enter]
```

This generates comprehensive unit tests for your file!

### Example 3: Auto-File Loading (V2 Only)

```
> check main.py for bugs

[Press Enter twice]
```

**V2 automatically:**
1. Detects you mentioned "main.py"
2. Finds it in your project
3. Loads it into context
4. Analyzes it for bugs
5. Suggests fixes

---

## Working with Projects

### Starting a New Project

```bash
# Create project folder
mkdir -p ~/Projects/my-new-app
cd ~/Projects/my-new-app

# Activate environment
source ~/.mlx-env/bin/activate

# Launch MLX-CODE
~/mlx-code

# Now chat with the AI!
> create a basic flask web app with a home page

[Press Enter twice]
```

### Working on Existing Projects

```bash
# Navigate to your project
cd ~/Projects/existing-project

# Activate environment
source ~/.mlx-env/bin/activate

# Launch
~/mlx-code

# Ask about your code
> explain what main.py does

[Press Enter twice]
```

### Project Context (V2 Feature)

When you launch MLX-CODE V2 in a project folder, it automatically:
- Reads README.md
- Detects project type (Python, Node.js, Rust, etc.)
- Loads package.json, requirements.txt, Cargo.toml, etc.
- Understands your project structure

```bash
cd ~/Projects/my-python-app
~/mlx-code

# V2 will show:
# 📁 Loaded project context: README.md, requirements.txt
# 🔧 Detected: python
```

---

## Essential Commands

Once MLX-CODE is running:

### Getting Help
```
/help              # Show all available commands
/stats             # Show session statistics
```

### Navigation
```
/pwd               # Show current directory
/cd src            # Change to src folder
/ls                # List files
/tree              # Show directory tree
```

### Context Management (V2)
```
/context           # Show what files are loaded
/open myfile.py    # Manually load a file
/context clear     # Clear loaded files
```

### Working with Code
```
/template          # List available templates
/template test myfile.py    # Generate tests
/backups           # Show file backups
/save              # Export chat to markdown
```

### Model Settings
```
/q7b               # Switch to 7B model (best quality)
/q3b               # Switch to 3B model (faster)
/tokens 2048       # Increase response length
```

### Exit
```
/exit              # Quit and save settings
```

---

## Keyboard Shortcuts (v2.1+)

**NEW!** With `prompt-toolkit` installed, you get a professional terminal experience:

### Navigation
```
↑ / ↓              # Navigate command history (previous/next)
← / →              # Move cursor to edit text
Home / End         # Jump to start/end of line
```

### Editing
```
Tab                # Auto-complete commands
Ctrl+C             # Clear current input (doesn't quit!)
Ctrl+D             # Exit MLX-CODE
Backspace / Delete # Edit text normally
```

### Features
- ✅ **Command History:** All commands saved, navigate with arrows
- ✅ **Multi-line Paste:** Paste code without breaking
- ✅ **Tab Completion:** Type `/mod` then Tab → `/models`
- ✅ **Smart Ctrl+C:** Clears buffer instead of showing ^C

**Example:**
```bash
# Type a command
> /download ds

# Press ↑ to recall it
> /download ds

# Press ← to move cursor and edit
> /download q7b  # Changed ds → q7b

# Press Tab for completion
> /mod [Tab]
> /models  # Auto-completed!
```

**Without prompt-toolkit:**
- ⚠️ Arrow keys show strange symbols
- ⚠️ No command history
- ⚠️ Pasting code may break
- ⚠️ Ctrl+C shows ^C symbols

**Solution:** Install prompt-toolkit (see Step 4 in Installation)

---

## Tips for Multi-Line Input

MLX-CODE uses **double-Enter** to send messages:

```
> create a flask API with these endpoints:
> - GET /users (list all users)
> - POST /users (create new user)
> - DELETE /users/:id (delete user)
>
> Use SQLAlchemy for the database

[Press Enter on empty line to send]
```

This lets you write detailed, multi-line prompts!

---

## Troubleshooting

### "Command not found: mlx-code"

```bash
# Check if file exists
ls -la ~/mlx-code

# If missing, copy again
cp mlx-code-v2.py ~/mlx-code

# Make executable
chmod +x ~/mlx-code
```

### "mlx_lm not found"

```bash
# Activate virtual environment first!
source ~/.mlx-env/bin/activate

# Then install
pip install mlx-lm
```

### "Cannot cd outside sandbox"

This means you're trying to work outside `~/Projects`:

```bash
# Make sure you're in Projects folder
cd ~/Projects/your-project

# Then launch
~/mlx-code
```

### "Permission denied"

```bash
# Make script executable
chmod +x ~/mlx-code
```

### Model Download is Slow

**⚡ BETTER METHOD AVAILABLE!** Use **git-lfs** for 3-5x faster downloads!

See **[DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md)** for the recommended git-lfs method which is:
- ✅ 3-5x faster (3-5 MB/s vs 150-500 KB/s)
- ✅ More reliable with slow connections
- ✅ Auto-resumes if interrupted

**If using the default method:**
First download takes time (4-5GB). Grab a coffee! ☕
- Models are cached in `~/.cache/huggingface/`
- Only downloads once
- Switch to smaller model if needed: `/q3b` (1.9GB)

### Out of Memory Errors

```bash
# Use smaller model
/q3b

# Or reduce context size
/ctx 16000
/tokens 512
```

---

## Understanding File Operations

### How File Changes Work

1. **You ask:** "create a config.json file"
2. **AI generates** the complete file content
3. **Preview shown** with syntax highlighting
4. **Diff displayed** if file already exists
5. **You choose:**
   - `[a]` Apply all changes
   - `[i]` Review individually
   - `[n]` Cancel
6. **Automatic backup** created before writing
7. **File updated** and confirmed

### Safety Features

**Every file modification:**
- ✅ Creates timestamped backup in `~/.mlx-code/backups/`
- ✅ Shows colored diff preview
- ✅ Requires your confirmation
- ✅ Logged to `~/.mlx-code/history.log`

**Restore from backup:**
```
/backups myfile.py          # List backups for file
/restore backup_name myfile.py   # Restore specific backup
```

---

## Version Differences Quick Reference

| Feature | Version 1 | Version 3 |
|---------|-----------|-----------|
| Write/Edit Files | ✅ | ✅ |
| File Backups | ✅ | ✅ |
| Templates | 6 templates | 8 templates |
| Auto-load files when mentioned | ❌ | ✅ |
| Streaming output | ❌ | ✅ |
| Git integration | ❌ | ✅ |
| Shell execution (`/run`) | ❌ | ✅ |
| Auto-save conversations | ❌ | ✅ |
| Per-project config | ❌ | ✅ |
| Find & replace (`/replace`) | ❌ | ✅ |
| Clipboard (`/copy`) | ❌ | ✅ |
| File search (`/find`) | ❌ | ✅ |

**Recommendation:** Use Version 3 (mlx-code-v2.py) for the best experience!

---

## Next Steps

### Learn More
- Read the full [README.md](README.md) for detailed documentation
- Check [ROADMAP.md](ROADMAP.md) for upcoming features
- Explore templates: `/template` in MLX-CODE

### Customize
- Adjust model size for your RAM (`/q7b`, `/q3b`, `/q1.5b`)
- Set preferred token limits (`/tokens 2048`)
- Create your own templates (edit the script)

### Get Productive
- Use `/template test` before writing tests
- Use `/template review` for code reviews
- Use `/template doc` to add documentation
- Use `/save` to export useful conversations

---

## Example Workflow

Here's a complete workflow from start to finish:

```bash
# 1. Create new project
mkdir -p ~/Projects/todo-app
cd ~/Projects/todo-app

# 2. Activate environment
source ~/.mlx-env/bin/activate

# 3. Start MLX-CODE
~/mlx-code

# 4. Create initial structure
> create a python todo app with these files:
> - main.py (CLI interface)
> - todo.py (Todo class)
> - storage.py (JSON file storage)
>
> Use click library for the CLI

[Press Enter twice]

# 5. Review and apply changes
[a]  # Apply all

# 6. Generate tests
> /template test todo.py

[Press Enter]

# 7. Add documentation
> /template doc main.py

[Press Enter]

# 8. Check for improvements
> review all the code and suggest improvements

[Press Enter twice]

# 9. Save session
> /save todo-app-development.md

# 10. Exit
> /exit
```

---

## Quick Reference Card

```bash
# Setup (one-time)
python3.12 -m venv ~/.mlx-env
source ~/.mlx-env/bin/activate
pip install mlx-lm prompt-toolkit pillow
cp mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code

# Daily usage (no env activation needed!)
cd ~/your-project
~/mlx-code

# Inside MLX-CODE
[Type your message]
[Press Enter twice to send]
/help                    # Show commands
/exit                    # Quit
```

---

## Support & Resources

### Log Files
Check what happened:
```bash
cat ~/.mlx-code/history.log
```

### Backups Location
```bash
ls -la ~/.mlx-code/backups/
```

### Model Cache
```bash
ls -la ~/.cache/huggingface/hub/
```

### Reset Everything
```bash
# Clear chat history
/clear

# Clear context
/context clear

# Or delete all data
rm -rf ~/.mlx-code/
```

---

## Summary

✅ **You now know:**
- What the ~/Projects folder is and why it exists
- How to install and run MLX-CODE
- How to work with different projects
- Essential commands and workflows
- How to troubleshoot common issues

🚀 **Start coding with AI assistance - completely private and free!**

---

*Last updated: February 25, 2026*
*MLX-CODE Version 3.0*
*For Apple Silicon Macs (M1/M2/M3/M4)*
