# MLX-CODE — Complete Installation & User Guide

**🚀 Local AI Coding Assistant with Intelligent File Context**  
*macOS • Apple Silicon (M1/M2/M3/M4) • Python 3.12 • Qwen2.5 Coder Models*

---

## 📋 Table of Contents

1. [Overview & Version Info](#-1-overview--version-info)
2. [System Requirements](#-2-system-requirements)
3. [Installation](#-3-installation)
4. [First Launch](#-4-first-launch)
5. [Core Features](#-5-core-features)
6. [Command Reference](#-6-command-reference)
7. [Advanced Usage](#-7-advanced-usage)
8. [Troubleshooting](#-8-troubleshooting)
9. [Tips & Best Practices](#-9-tips--best-practices)
10. [Update Instructions](#-10-update-instructions)

---

## 🚀 1. Overview & Version Info

**MLX-CODE** is a powerful, privacy-focused local AI coding assistant that runs entirely on your Mac using Apple's MLX framework. Think of it as a self-hosted alternative to Claude Code or GitHub Copilot, but with full project context awareness and intelligent file handling.

### 📦 Current Versions

The project has two versions with different capabilities:

#### **Version 1 (mlx-code-v1.py)** - Basic File Writing
- ✅ Can **write and create** files
- ❌ Cannot **read** files automatically
- ✅ Basic conversation and code generation
- ✅ File editing with diff preview
- ⚠️ Limited context awareness

#### **Version 2 (mlx-code-v2.py)** - 🚧 Work in Progress
- ✅ Can **write and create** files
- ✅ Can **read README.md** automatically
- 🚧 **Working on**: Auto-reading ALL project files
- 🚧 **In development**: Full intelligent context loading
- 🎯 **Goal**: Automatically read and understand entire project structure

**Current Status:** Version 2 is actively being developed to support complete project-wide file reading and context awareness.

### 🎯 How to Run

Based on your current setup, use this command:

```bash
~/mlx-code
```

Or if you're in your project directory:

```bash
cd ~/Projects/MLX-Terminal-Code
~/mlx-code
```

### ✨ What Makes It Special

- **🔒 100% Local & Private** — No data sent to external servers
- **🧠 Intelligent Context** — (V2 in development) Automatically loads files
- **📁 Project Awareness** — Understands your codebase structure
- **🖼️ Image Support** — (V2 feature) Can view and describe images
- **💾 Auto-Backup** — Every file modification is backed up automatically
- **⚡ GPU Accelerated** — Uses Apple Silicon GPU for fast inference
- **🎯 Smart Templates** — Quick workflows for testing, documentation, refactoring, etc.

### 📂 Your Current File Structure

```
~/Projects/MLX-Terminal-Code/
├── mlx-code-v1.py          # Version 1: Basic (writes files, no reading)
├── mlx-code-v2.py          # Version 2: Advanced (WIP - auto file reading)
└── README.md               # This guide
```

Your main executable:
```
~/mlx-code                   # Symlink or main script
```

**Note:** Since you run `~/mlx-code`, make sure this file contains either v1 or v2 code depending on which version you want to use.

### 🔧 Technology Stack

- **MLX** (Apple) → Metal GPU acceleration for M-series chips
- **MLX-LM** → High-performance LLM inference library
- **Qwen2.5 Coder** → State-of-the-art coding models (7B/3B/1.5B variants)
- **Python 3.12** → Latest stable Python with performance improvements

### 🚧 Development Roadmap

#### ✅ Version 1 - Completed Features
- File creation and editing with ````file:path` syntax
- Colored diff preview
- Backup system
- Basic conversation flow
- Template system
- Navigation commands (`/ls`, `/cd`, `/tree`)

#### 🔨 Version 2 - Current Work (Active Development)
- ✅ **Completed:** README.md auto-loading
- 🚧 **In Progress:** Complete project file auto-reading
- 🚧 **In Progress:** Intelligent file reference detection
- 🚧 **Planned:** Multi-file context awareness
- 🚧 **Planned:** Image support with PIL
- 🚧 **Planned:** Smart context prioritization

#### 🎯 Future Goals (Version 3+)
- Real-time file watching
- Git integration
- Multi-project context switching
- Plugin system
- Web UI interface

---

## 💻 2. System Requirements

### Required

- **macOS** 13.0 (Ventura) or later
- **Apple Silicon** (M1, M2, M3, or M4 chip)
- **Python 3.12** or later
- **8GB RAM minimum** (16GB+ recommended for 7B model)
- **10GB free disk space** (for models and cache)

### Recommended

- **16GB+ RAM** for smooth operation with larger models
- **Terminal app** with Unicode support (default Terminal.app works fine)
- **$EDITOR environment variable** set (nano, vim, VSCode, etc.)

---

## 🛠️ 3. Installation

### Step 1: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Python 3.12

```bash
brew install python@3.12
```

Verify installation:

```bash
python3.12 --version
# Should output: Python 3.12.x
```

### Step 3: Create Virtual Environment

Create a dedicated environment for MLX-CODE-PRO:

```bash
python3.12 -m venv ~/.mlx-env
```

Activate it:

```bash
source ~/.mlx-env/bin/activate
```

You should see `(mlx-env)` in your terminal prompt.

**💡 Tip:** Add this to your `~/.zshrc` for easy activation:

```bash
echo 'alias mlxenv="source ~/.mlx-env/bin/activate"' >> ~/.zshrc
source ~/.zshrc
```

Now you can type `mlxenv` to activate the environment.

### Step 4: Install Required Packages

```bash
# Core requirement
pip install --upgrade pip
pip install mlx-lm

# Optional: Image support
pip install pillow
```

Verify installation:

```bash
python -c "import mlx_lm; print('✓ MLX-LM installed successfully')"
```

### Step 5: Pre-download Models (Optional but Recommended)

While MLX-CODE-PRO will download models automatically on first use, you can pre-download them:

```bash
# Recommended: 7B model (best quality, ~4.3GB)
mlx_lm.convert --hf-path Qwen/Qwen2.5-Coder-7B-Instruct -q

# Alternative: 3B model (faster, ~1.9GB)
mlx_lm.convert --hf-path Qwen/Qwen2.5-Coder-3B-Instruct -q

# Lightweight: 1.5B model (quickest, ~1GB)
mlx_lm.convert --hf-path Qwen/Qwen2.5-Coder-1.5B-Instruct -q
```

Models are cached in:
```
~/.cache/huggingface/hub/
```

### Step 6: Create Projects Directory

MLX-CODE-PRO operates in a sandboxed directory for security:

```bash
mkdir -p ~/Projects
```

All your work must be inside `~/Projects`. This prevents accidental system file modifications.

### Step 7: Install MLX-CODE Script

**Option A: If you already have the files (your current setup)**

You already have the scripts in your project:
```bash
cd ~/Projects/MLX-Terminal-Code
ls -la
# You should see: mlx-code-v1.py, mlx-code-v2.py, README.md
```

Update your main executable:
```bash
# If ~/mlx-code doesn't exist yet, create it
cp ~/Projects/MLX-Terminal-Code/mlx-code-v2.py ~/mlx-code

# Or edit the existing one
nano ~/mlx-code
```

**Option B: Creating from scratch**

```bash
# Create the file
nano ~/mlx-code
# (paste the script content)
```

Make it executable:

```bash
chmod +x ~/mlx-code
```

**Important:** Since you're working on Version 2, make sure `~/mlx-code` contains the v2 code with the improvements you're developing.

### Step 8: Add to PATH

Edit your shell configuration:

```bash
nano ~/.zshrc
```

Add this line:

```bash
export PATH="$HOME:$PATH"
```

Reload configuration:

```bash
source ~/.zshrc
```

### Step 9: Verify Installation

```bash
~/mlx-code
```

You should see the MLX-CODE banner and interface!

**Note:** If you get "command not found", the file might not be in the right place or not executable. Check:
```bash
ls -la ~/mlx-code
# Should show: -rwxr-xr-x ... /Users/yourusername/mlx-code
```

---

## 🎬 4. First Launch

### Basic Usage

1. Navigate to your project:
```bash
cd ~/Projects/MLX-Terminal-Code
# or any other project in ~/Projects
```

2. Launch MLX-CODE:
```bash
~/mlx-code
```

3. Wait for model loading (first time takes 30-60 seconds)

4. Start chatting! Type your message and press **Enter twice** to send.

### Example First Conversation (Version 1)

```
> create a simple python script that prints hello world
[Press Enter twice]

🤖 Assistant:
I'll create a simple Python script for you.

```file:hello.py
#!/usr/bin/env python3

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
` ``

Apply changes to hello.py? [y/N] y
✅ Wrote hello.py
```

### Example with Version 2 (when file reading is fully implemented)

```
> check my hello.py file for improvements
📖 Auto-loaded: hello.py

🤖 Assistant:
I've analyzed hello.py. Here are some suggestions...
```

**Current V2 Status:** Only README.md is auto-loaded. Other file reading is being developed.

---

## 🎯 5. Core Features

### 📊 Version Comparison: What Works Now vs What's Coming

| Feature | Version 1 | Version 2 (Current) | Version 2 (Goal) |
|---------|-----------|---------------------|------------------|
| Write/Create Files | ✅ Yes | ✅ Yes | ✅ Yes |
| Edit Existing Files | ✅ Yes | ✅ Yes | ✅ Yes |
| Read README.md | ❌ No | ✅ Yes | ✅ Yes |
| Read Other Files | ❌ No | 🚧 Manual only | 🎯 Automatic |
| Auto-detect File References | ❌ No | 🚧 Partial | 🎯 Full |
| Multi-file Context | ❌ No | 🚧 Limited | 🎯 Complete |
| Image Support | ❌ No | 🚧 Planned | 🎯 Full |
| Project Structure Analysis | ⚠️ Basic | ⚠️ Basic | 🎯 Advanced |
| Smart Context Priority | ❌ No | 🚧 Working on | 🎯 Intelligent |

### 🔥 Features Available Now (Both Versions)

#### 💾 File Writing & Editing
Both versions can create and modify files using the ````file:path` syntax:

```
🤖 Assistant:
```file:src/main.py
# Your code here
` ``

Apply changes? [y/N]
```

#### 🎨 Beautiful Diff Previews
See exactly what will change before applying:
- 🟢 Green for additions
- 🔴 Red for deletions  
- 🟡 Yellow for context
- Automatic backups before any change

#### 💾 Automatic Backups

Every file modification creates a timestamped backup:

```
~/Projects/myproject/main.py  →  modified
~/.mlx-code/backups/myproject_main.py_20241121_143022  →  backup created
```

Restore anytime with `/backups` and `/restore` commands.

#### 📋 Template System

Quick workflows available in both versions:

| Template | Description | Usage |
|----------|-------------|-------|
| `test` | Generate unit tests | `/template test myfile.py` |
| `doc` | Add documentation | `/template doc myfile.py` |
| `refactor` | Improve code quality | `/template refactor myfile.py` |
| `review` | Code review | `/template review myfile.py` |
| `optimize` | Performance tips | `/template optimize myfile.py` |
| `explain` | Explain code | `/template explain myfile.py` |

### 🚧 Features in Development (Version 2)

#### 🧠 Intelligent File Reading (Work in Progress)

**Current Status:**
- ✅ README.md is automatically loaded when you start
- ⚠️ Other files require manual `/open filename` command
- 🚧 Working on: Detecting file mentions in conversation
- 🚧 Working on: Auto-loading referenced files

**Goal:** When you say *"check main.py for bugs"*, the assistant will automatically:
1. Detect you mentioned `main.py`
2. Find it in the project
3. Load it into context
4. Analyze it

**Current Workaround:**
```
> /open main.py
> now check it for bugs
```

#### 📁 Project Context Awareness (Planned)

The assistant will automatically understand:
- Project type (Python, Node.js, Rust, etc.)
- Dependencies (requirements.txt, package.json)
- Project structure
- Related files

### 🎨 Smart Code Generation (Available Now)

The assistant generates production-ready code with:
- ✅ Proper error handling
- ✅ Type hints (Python)
- ✅ Meaningful comments
- ✅ Language-specific best practices
- ✅ Security considerations

---

## 📖 6. Command Reference

### 🎯 Core Commands (Available in All Versions)

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show complete help | `/help` |
| `/exit` | Quit MLX-CODE | `/exit` |
| `/clear` | Clear chat history | `/clear` |

### 🧠 Context Management

| Command | V1 | V2 Current | Description | Example |
|---------|-----|------------|-------------|---------|
| `/open <file>` | ✅ | ✅ | Manually load file into context | `/open src/main.py` |
| `/context` | ❌ | 🚧 | Show current context (V2 only) | `/context` |
| `/context on/off` | ❌ | 🚧 | Toggle auto-context (V2 WIP) | `/context on` |
| `/context clear` | ❌ | 🚧 | Clear loaded files (V2 only) | `/context clear` |
| `/context reload` | ❌ | 🚧 | Reload project (V2 WIP) | `/context reload` |

**Note:** V2 context commands are partially implemented. Full auto-loading is still in development.

### 🤖 Model Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `/model <id>` | Switch to different model | `/model mlx-community/...` |
| `/q7b` | Quick switch to Qwen 7B | `/q7b` |
| `/q3b` | Quick switch to Qwen 3B | `/q3b` |
| `/q1.5b` | Quick switch to Qwen 1.5B | `/q1.5b` |
| `/tokens <n>` | Set max tokens per response | `/tokens 2048` |
| `/ctx <n>` | Set context window size | `/ctx 30000` |

### 📁 File Navigation

| Command | Description | Example |
|---------|-------------|---------|
| `/pwd` | Show current directory | `/pwd` |
| `/cd <path>` | Change directory | `/cd src` |
| `/ls [path]` | List directory contents | `/ls utils` |
| `/tree [path]` | Show directory tree | `/tree src` |

### 🔍 Search & Compare

| Command | Description | Example |
|---------|-------------|---------|
| `/grep <pattern>` | Search in files | `/grep "TODO"` |
| `/diff <f1> <f2>` | Compare two files | `/diff old.py new.py` |

### 📋 Templates

| Command | Description | Example |
|---------|-------------|---------|
| `/template` | List all templates | `/template` |
| `/template <name> <file>` | Apply template | `/template test utils.py` |

### 💾 Backup & Restore

| Command | Description | Example |
|---------|-------------|---------|
| `/backups [file]` | List backups | `/backups main.py` |
| `/restore <backup> <file>` | Restore from backup | `/restore backup_123 main.py` |

### 🛠️ Utilities

| Command | Description | Example |
|---------|-------------|---------|
| `/save [file]` | Export chat to markdown | `/save session.md` |
| `/last` | Repeat last query | `/last` |
| `/edit` | Open last modified file in $EDITOR | `/edit` |
| `/stats` | Show session statistics | `/stats` |
| `/project` | Detect and show project info | `/project` |

---

## 🚀 7. Advanced Usage

### Multi-line Input

To send multi-line prompts:

```
> create a flask api with three endpoints:
> - GET /users
> - POST /users
> - DELETE /users/:id
[Press Enter on empty line to send]
```

### Working with Multiple Files

```
> refactor both main.py and utils.py to use async/await
📖 Auto-loaded: main.py, utils.py
🤖 Assistant: [Analyzes both files and suggests improvements]
```

### Project-wide Analysis

```
> /project
🔧 Detected: python
📁 Project structure:
myproject/
  src/
    main.py
    utils.py
  tests/
    test_main.py
  requirements.txt
  README.md
```

### Custom Model Configuration

```
> /model mlx-community/custom-model-4bit
⠋ Loading model...
✓ Model loaded successfully
```

### Batch File Operations

When multiple files are suggested:

```
📝 Found 3 file(s) to modify
  • src/main.py
  • src/utils.py
  • tests/test_main.py

Options:
  [a] Apply all changes
  [i] Apply individually
  [n] Cancel all

Your choice: a
```

### Session Export

```
> /save my-refactoring-session.md
✓ Saved to my-refactoring-session.md
```

The exported markdown includes:
- Full conversation history
- Model information
- Timestamp
- Project type

---

## 🔧 8. Troubleshooting

### ❌ "mlx_lm not found"

**Problem:** MLX-LM library not installed

**Solution:**
```bash
source ~/.mlx-env/bin/activate
pip install mlx-lm
```

### ❌ "permission denied: ~/mlx-code"

**Problem:** Script not executable

**Solution:**
```bash
chmod +x ~/mlx-code
```

### ❌ "command not found: ~/mlx-code"

**Problem:** Script doesn't exist or wrong path

**Solution:**
```bash
# Check if file exists
ls -la ~/mlx-code

# If it doesn't exist, copy from your project
cp ~/Projects/MLX-Terminal-Code/mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code
```

### ❌ "cannot cd outside sandbox"

**Problem:** Trying to access files outside `~/Projects`

**Solution:** Only work within `~/Projects` directory:
```bash
cd ~/Projects/yourproject
~/mlx-code
```

### ❌ Files not being auto-loaded (Version 2)

**Problem:** Expected auto-loading not working yet

**Current Status:** 
- ✅ README.md auto-loads
- 🚧 Other files need manual `/open` command
- 🚧 Full auto-loading is in development

**Workaround:**
```bash
> /open filename.py
> now analyze this file
```

### ❌ Model loading takes forever

**Problem:** First-time download of large model

**Solution:** 
- Be patient (7B model is ~4.3GB)
- Or pre-download with `mlx_lm.convert`
- Or switch to smaller model with `/q3b` (if implemented)

### ❌ "Out of memory" error

**Problem:** Insufficient RAM for model

**Solutions:**
1. Switch to smaller model in code
2. Reduce context size: `/ctx 16000`
3. Reduce max tokens: `/tokens 512`
4. Close other applications

### ❌ Context commands not working (Version 1)

**Problem:** Using V2 commands in V1

**Solution:** Check which version you're running:
```bash
head -n 5 ~/mlx-code
# Look for version indicator in comments
```

If you want V2 features, copy the v2 script:
```bash
cp ~/Projects/MLX-Terminal-Code/mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code
```

---

## 💡 9. Tips & Best Practices

### 🎯 For Best Results

1. **Be Specific**
   - ❌ "fix the bug"
   - ✅ "fix the IndexError in line 42 of main.py"

2. **Use Context Wisely**
   - Mention files by name for auto-loading
   - Use `/open` for large files
   - Clear context with `/context clear` when switching tasks

3. **Leverage Templates**
   - Use `/template test` before writing tests manually
   - Use `/template review` for code reviews
   - Use `/template doc` for documentation

4. **Backup Management**
   - Check backups regularly: `/backups`
   - Old backups can be manually deleted from `~/.mlx-code/backups/`

5. **Model Selection**
   - **7B model**: Best quality, slower, more RAM
   - **3B model**: Good balance
   - **1.5B model**: Fastest, less accurate

### 🔒 Security Best Practices

- Never run MLX-CODE-PRO with `sudo`
- Keep work inside `~/Projects` sandbox
- Review all code changes before applying
- Use `/backups` to check before large refactoring
- Don't include API keys or passwords in prompts

### ⚡ Performance Optimization

```bash
# For faster responses
/tokens 512
/ctx 16000

# For better quality
/tokens 2048
/ctx 24000

# Find your balance
/stats  # Check token usage
```

### 📁 Project Organization

Recommended structure:
```
~/Projects/
├── personal/
│   ├── project1/
│   └── project2/
├── work/
│   ├── client1/
│   └── client2/
└── experiments/
    └── testing/
```

### 🎨 Workflow Examples

**Adding Tests to Existing Code:**
```
> /template test src/utils.py
[Reviews generated tests]
> a  # Apply all
```

**Refactoring with Review:**
```
> /open old_code.py
> refactor this to use modern Python 3.12 features
> /template review old_code.py
> compare the differences
```

**Debugging Session:**
```
> /open buggy_script.py
> /template debug buggy_script.py
> the error happens when input is empty
> show me the fixed version
```

---

## 🔄 10. Update Instructions

### Updating Your MLX-CODE Script

#### Option 1: Update from Project Directory

If you're working on the code in your project:

```bash
# Edit in your project
cd ~/Projects/MLX-Terminal-Code
nano mlx-code-v2.py
# Make your changes...

# Copy to main executable
cp mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code

# Test
~/mlx-code
```

#### Option 2: Direct Edit

```bash
# Backup current version first
cp ~/mlx-code ~/mlx-code.backup.$(date +%Y%m%d)

# Edit directly
nano ~/mlx-code
# Make your changes...

# Test
~/mlx-code

# If something breaks, restore backup
# cp ~/mlx-code.backup.YYYYMMDD ~/mlx-code
```

### Switching Between V1 and V2

```bash
# Use Version 1 (stable, writes only)
cp ~/Projects/MLX-Terminal-Code/mlx-code-v1.py ~/mlx-code
chmod +x ~/mlx-code

# Use Version 2 (development, with file reading)
cp ~/Projects/MLX-Terminal-Code/mlx-code-v2.py ~/mlx-code
chmod +x ~/mlx-code
```

### Updating Models

```bash
# Models auto-update, but you can force re-download:
rm -rf ~/.cache/huggingface/hub/models--*qwen*

# Then relaunch (will download fresh)
~/mlx-code
```

### Updating Python Dependencies

```bash
source ~/.mlx-env/bin/activate
pip install --upgrade mlx-lm pillow
```

### View Your Current Version

```bash
# Check which version you're running
head -n 20 ~/mlx-code | grep -E "version|VERSION|v1|v2"

# Or check in the script directly
nano ~/mlx-code
# Look at the top comments or filename references
```

---

## 📊 Feature Comparison

### MLX-CODE vs Other Tools

| Feature | MLX-CODE V1 | MLX-CODE V2 | GitHub Copilot | Claude Code |
|---------|-------------|-------------|----------------|-------------|
| 100% Local/Private | ✅ | ✅ | ❌ | ❌ |
| Write/Edit Files | ✅ | ✅ | ✅ | ✅ |
| Read Files Auto | ❌ | 🚧 Partial | ⚠️ Limited | ✅ |
| Full Project Context | ❌ | 🚧 WIP | ⚠️ Limited | ✅ |
| Image Support | ❌ | 🚧 Planned | ❌ | ✅ |
| Automatic Backups | ✅ | ✅ | ❌ | ❌ |
| Template System | ✅ | ✅ | ❌ | ⚠️ |
| Free & Open Source | ✅ | ✅ | ❌ | ❌ |
| Requires Internet | ❌ | ❌ | ✅ | ✅ |
| Multi-file Editing | ✅ | ✅ | ⚠️ | ✅ |
| Diff Preview | ✅ | ✅ | ⚠️ | ⚠️ |

**Legend:**
- ✅ = Fully working
- 🚧 = In development
- ⚠️ = Partial/Limited
- ❌ = Not available

### Version Roadmap

**V1 (Stable)**
- ✅ Complete: All basic features working
- ✅ Production ready for file editing
- ❌ No file reading capabilities

**V2 (Current - Active Development)**
- ✅ Complete: README.md auto-loading
- 🚧 In Progress: Full file reading system
- 🚧 In Progress: Intelligent context management
- 🎯 Goal: Match Claude Code functionality locally

**V3 (Future)**
- Git integration
- Real-time file watching
- Multi-project support
- Web UI

---

## 🗂️ File Structure Overview

```
~/
├── mlx-code                                # Main executable (your current setup)
│                                          # Contains either V1 or V2 code
│
├── Projects/                              # Your workspace (SANDBOX)
│   ├── MLX-Terminal-Code/                # This project
│   │   ├── mlx-code-v1.py               # Version 1: Basic (writes only)
│   │   ├── mlx-code-v2.py               # Version 2: Advanced (WIP)
│   │   └── README.md                     # This guide
│   │
│   ├── your-other-project/               # Your projects
│   └── ...
│
├── .mlx-env/                             # Python virtual environment
│   ├── bin/
│   │   └── python3.12
│   ├── lib/
│   └── ...
│
└── .mlx-code/                            # MLX-CODE data directory
    ├── config.json                       # User configuration (auto-saved)
    ├── history.log                       # Operation logs
    └── backups/                          # File backups
        ├── MLX-Terminal-Code_mlx-code-v2.py_20241121_140530
        └── ...

~/.cache/huggingface/hub/                 # Model cache
    └── models--mlx-community--qwen2.5-coder-7b-instruct-4bit/


---

## 🆘 Getting Help

### In-App Help
```bash
/help           # Show all commands
/stats          # Show session info
/context        # Show current context
```

### Log Files
Check operation logs:
```bash
cat ~/.mlx-code/history.log
```

### Reset Everything
```bash
# Clear all context and history
/clear
/context clear

# Or restart
/exit
mlx-code-pro
```

---

## 📝 Configuration File

Location: `~/.mlx-code/config.json`

Example configuration:
```json
{
  "model": "mlx-community/qwen2.5-coder-7b-instruct-4bit",
  "max_tokens": 1024,
  "ctx_chars": 24000
}
```

Settings are automatically saved when you `/exit`.

---

## 🎓 Learning Resources

### Understanding MLX
- [Apple MLX Documentation](https://ml-explore.github.io/mlx/)
- [MLX-LM GitHub](https://github.com/ml-explore/mlx-lm)

### Qwen2.5 Coder Models
- [Model Card](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct)
- [Technical Report](https://qwenlm.github.io/blog/qwen2.5-coder/)

### Python 3.12 Features
- [What's New in Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html)

---

## 📜 License & Attribution

**MLX-CODE-PRO** uses:
- **MLX & MLX-LM** by Apple (MIT License)
- **Qwen2.5 Coder** by Alibaba Cloud (Apache 2.0)
- **Python 3.12** (PSF License)

This project is open-source and free to use.

---

## 🎉 Quick Start Checklist

- [ ] Install Python 3.12
- [ ] Create virtual environment (`~/.mlx-env`)
- [ ] Install `mlx-lm` (and optionally `pillow`)
- [ ] Create `~/Projects` directory
- [ ] Choose your version: V1 (stable) or V2 (development)
- [ ] Copy chosen version to `~/mlx-code`
- [ ] Make executable: `chmod +x ~/mlx-code`
- [ ] Test with `~/mlx-code`
- [ ] Navigate to project: `cd ~/Projects/yourproject`
- [ ] Start coding with AI! 🚀

---

## 🚧 Development Status

### Current Focus (Version 2)

We're actively working on making MLX-CODE truly intelligent:

**✅ Completed:**
- Basic file writing and editing
- Beautiful diff previews
- Automatic backups
- Template system
- README.md auto-loading

**🔨 In Progress:**
- Intelligent file reference detection
- Auto-loading all mentioned files
- Smart context management
- Project-wide file reading

**🎯 Upcoming:**
- Image support (Pillow integration)
- Multi-file context priority
- Cross-file reference understanding
- Advanced project structure analysis

### How to Contribute / Test

If you want to help test and improve V2:

1. **Try different file mentions:**
   ```
   > check main.py
   > look at utils.py and helpers.py
   > analyze the bug in src/parser.js
   ```

2. **Report what works:**
   - Which files get auto-loaded?
   - Which ones don't?
   - Any patterns you notice?

3. **Test edge cases:**
   - Files in subdirectories
   - Files with spaces in names
   - Multiple files in one message

4. **Share feedback:**
   - What features would you like?
   - What's confusing?
   - What works well?

---

## 📞 Support

For issues, questions, or contributions:
- Check `/help` within the app
- Review this README thoroughly
- Check logs in `~/.mlx-code/history.log`
- Verify Python 3.12 compatibility
- Compare V1 vs V2 features to understand what's implemented

### Common Questions

**Q: Which version should I use?**
A: Use V1 for stable file editing, V2 for testing new features (but be aware some features are still WIP).

**Q: Why isn't my file being auto-loaded?**
A: V2's auto-loading is still in development. Currently only README.md works automatically. Use `/open filename` as workaround.

**Q: How do I know which version I'm running?**
A: Check the top of your `~/mlx-code` file or see which features work (e.g., `/context` commands only in V2).

**Q: Can I use both versions?**
A: Yes! Keep both in your project folder and copy whichever you need to `~/mlx-code`.

---

**Made with ❤️ by developers, for developers who value privacy and local control**

*Last updated: November 21, 2024*  
*Version: 2.0 (Development)*  
*Python: 3.12+*  
*Platform: macOS Apple Silicon*

---

## 🔖 Quick Reference Card

```bash
# Start MLX-CODE
~/mlx-code

# Essential Commands
/help          # Show all commands
/open file     # Load file into context (V2 workaround)
/ls            # List files
/cd path       # Change directory
/template      # List code templates
/backups       # Show file backups
/stats         # Session statistics
/exit          # Quit

# File Editing Workflow
1. Ask assistant to create/modify code
2. Review the ```file:path``` blocks
3. Choose: [a]pply all, [i]ndividual, or [n]o
4. Files are backed up automatically

# Context Management (V2)
/context       # Show what's loaded
/open file     # Manually load a file
/context clear # Clear all loaded files
```

**Remember:** End your message with an empty line (press Enter twice) to send! 🚀
