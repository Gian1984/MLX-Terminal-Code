# MLX-CODE — Optimized Guide for M4 Pro 24GB

**🚀 Maximize Your M4 Pro with 24GB Unified Memory!**
*Apple M4 Pro • 24GB RAM • Python 3.12 • MLX Framework*

---

## 📋 Table of Contents

1. [Quick Start](#-1-quick-start)
2. [Model Overview](#-2-model-overview)
3. [Model Management Commands](#-3-model-management-commands)
4. [Recommended Setup](#-4-recommended-setup)
5. [Performance Comparison](#-5-performance-comparison)
6. [When to Use Which Model](#-6-when-to-use-which-model)
7. [Tips & Tricks](#-7-tips--tricks)
8. [Troubleshooting](#-8-troubleshooting)
9. [FAQ](#-9-faq)

---

## 🚀 1. Quick Start

### First Time Setup

```bash
# 1. Launch MLX-CODE
~/mlx-code

# 2. List all available models
> /models

# 3. Download DeepSeek V2 Lite (RECOMMENDED for 24GB!)
> /download ds
# Wait 10-20 minutes (~9GB download)

# 4. Switch to DeepSeek V2
> /ds

# 5. Test it!
> write a Python function to parse JSON with error handling
```

### Already Have Models?

```bash
# Check what's installed
> /installed

# Switch to best model
> /ds          # DeepSeek V2 - Best choice!
> /q14b        # Qwen 14B - Alternative
> /q7b         # Qwen 7B - Fast & safe
```

---

## 📊 2. Model Overview

### ⚠️ IMPORTANT: Qwen 32B Warning

**Qwen 32B is NOT recommended for M4 Pro 24GB** because:
- ❌ Requires ~17.6GB just to load
- ❌ Needs 3-4GB extra for generation
- ❌ Total: ~20-21GB (too close to limit!)
- ❌ Crashes with "Insufficient Memory" error
- ❌ Unstable even with all apps closed

**Use these instead:**
- ✅ **DeepSeek V2 Lite** (~9-12GB) - **Equal or better quality!**
- ✅ **Qwen 14B** (~10-12GB) - Great alternative
- ✅ **Qwen 7B** (~5-7GB) - Safe and fast

### 🏆 Available Models by Category

#### **Qwen Coder** (Best for Coding)
| Alias | Download | RAM Usage | Quality | Speed | Command |
|-------|----------|-----------|---------|-------|---------|
| `/q1.5b` | ~1.0GB | ~2-3GB | ⭐⭐ | ⚡⚡⚡ | `/q1.5b` |
| `/q3b` | ~1.9GB | ~3-4GB | ⭐⭐⭐ | ⚡⚡⚡ | `/q3b` |
| `/q7b` | ~4.3GB | ~5-7GB | ⭐⭐⭐⭐ | ⚡⚡ | `/q7b` |
| `/q14b` | ~8.5GB | ~10-12GB | ⭐⭐⭐⭐⭐ | ⚡⚡ | `/q14b` |
| ~~`/q32b`~~ | ~~17GB~~ | ~~20GB~~ | ⭐⭐⭐⭐⭐ | ⚡ | ❌ **Too large** |

**✅ Recommended:** `/q14b` — Best Qwen model that fits 24GB safely

#### **DeepSeek Coder** (Excellent for Code)
| Alias | Download | RAM Usage | Quality | Speed | Command |
|-------|----------|-----------|---------|-------|---------|
| `/ds1.3b` | ~1.0GB | ~2-3GB | ⭐⭐ | ⚡⚡⚡ | `/ds1.3b` |
| `/ds6.7b` | ~4.0GB | ~5-7GB | ⭐⭐⭐⭐ | ⚡⚡ | `/ds6.7b` |
| **`/ds`** | **~9.0GB** | **~9-12GB** | **⭐⭐⭐⭐⭐** | **⚡⚡** | **`/ds`** |

**🏆 BEST CHOICE:** `/ds` (DeepSeek V2 Lite) — Optimized for M4 Pro 24GB!

#### **Other Powerful Models**
| Alias | Model | RAM | Specialization | Command |
|-------|-------|-----|----------------|---------|
| `/llama3-8b` | Llama 3 8B | ~6-8GB | Advanced reasoning | `/llama3-8b` |
| `/codellama` | CodeLlama 13B | ~10-12GB | Code specialist | `/codellama` |
| `/mistral` | Mistral 7B | ~5-7GB | Versatile | `/mistral` |
| `/phi3` | Phi-3 Mini | ~3-4GB | Efficient & fast | `/phi3` |

---

## 🛠️ 3. Model Management Commands

### New Commands in v2.1

```bash
# List all available models with installation status
> /models

# Show only installed models with disk usage
> /installed

# Download a model (example: DeepSeek V2)
> /download ds

# Delete a model to free disk space
> /delete q3b

# Quick switch to any model (if already downloaded)
> /ds          # DeepSeek V2
> /q14b        # Qwen 14B
> /llama3-8b   # Llama 3 8B
```

### Download Example: DeepSeek V2

```bash
~/mlx-code

# Inside mlx-code:
> /download ds
```

**Output:**
```
═══════════════════════════════════════════════════════════════════
📥 Download Model: /ds
═══════════════════════════════════════════════════════════════════
  Model: mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit
  Size: ~9.0GB
  RAM needed: ~9-12GB
═══════════════════════════════════════════════════════════════════

Download this model? [y/N] y

🚀 Using git-lfs for faster download (3-5x faster!)
──────────────────────────────────────────────────────────────────
📥 Cloning from HuggingFace...
[progress bar]
✅ Model downloaded successfully!
──────────────────────────────────────────────────────────────────
```

### Delete Example

```bash
> /installed
# See list of installed models

> /delete q3b
⚠️  WARNING: This will delete the model from disk!
  Model: mlx-community/qwen2.5-coder-3b-instruct-4bit
  Alias: /q3b

Are you sure? [y/N] y
✅ Model deleted successfully!
```

---

## 🎯 4. Recommended Setup

### 🥇 Optimal 3-Model Setup

With 24GB RAM, you can keep multiple models installed for different purposes:

#### **1. DeepSeek V2 Lite** → Main Workhorse (RECOMMENDED!)
```bash
> /download ds
> /ds  # Use this for serious coding
```
- ✅ **Excellent quality** for complex code (⭐⭐⭐⭐⭐)
- ✅ **Stable with 24GB** (~9-12GB RAM usage)
- ✅ Fast (~1-2 seconds per response)
- ✅ Great for refactoring and architecture

**Why DeepSeek V2 over Qwen 32B?**
- Same or better code quality
- Uses half the RAM
- More stable
- Faster responses
- Works with other apps open

#### **2. Qwen 7B** → Fast Backup
```bash
> /download q7b
> /q7b  # Fast alternative
```
- ✅ **Safe and stable** (~5-7GB RAM)
- ✅ Great quality/speed balance (⭐⭐⭐⭐)
- ✅ Fast (~1 second per response)
- ✅ Perfect for multitasking

#### **3. Qwen 3B** → Quick Tasks
```bash
> /download q3b
> /q3b  # For quick questions
```
- ✅ **Very fast** (~0.5 seconds)
- ✅ Perfect for simple questions
- ✅ Multitasking without slowdown

### 💾 Total Disk Space
- DeepSeek V2: **9GB**
- Qwen 7B: **4GB**
- Qwen 3B: **2GB**
- **Total:** ~15GB on disk (not in RAM simultaneously!)

### Alternative Setup: Quality Focused

```bash
> /download ds        # DeepSeek V2 - Best quality
> /download q14b      # Qwen 14B - Alternative
> /download q3b       # Qwen 3B - Quick tasks
# Total: ~20GB disk
```

---

## ⚡ 5. Performance Comparison

### Test: "Write a REST API with Flask and SQLAlchemy"

| Model | Response Time | Code Quality | Completeness | RAM Used |
|-------|--------------|--------------|--------------|----------|
| DeepSeek V2 (`/ds`) | ~1.8s | ⭐⭐⭐⭐⭐ | 100% | ~11GB |
| Qwen 14B (`/q14b`) | ~2.5s | ⭐⭐⭐⭐⭐ | 95% | ~11GB |
| Qwen 7B (`/q7b`) | ~1.5s | ⭐⭐⭐⭐ | 90% | ~6GB |
| Qwen 3B (`/q3b`) | ~0.8s | ⭐⭐⭐ | 75% | ~4GB |
| ~~Qwen 32B (`/q32b`)~~ | ~~3.2s~~ | ⭐⭐⭐⭐⭐ | ~~100%~~ | ❌ Crash |

**Conclusion:**
- **DeepSeek V2**: Best for complex projects
- **Qwen 14B**: Excellent alternative
- **Qwen 7B**: Daily coding
- **Qwen 3B**: Quick questions

### Real-World Performance (M4 Pro)

Thanks to M4 Pro's improved Neural Engine:
- ~30-40% faster than M1/M2 for same model
- Better memory bandwidth
- More efficient power usage

---

## 🎨 6. When to Use Which Model

### Use **DeepSeek V2** (`/ds`) for:
- ✅ Complex system architecture
- ✅ Refactoring legacy code
- ✅ In-depth code reviews
- ✅ Difficult debugging
- ✅ Production-ready code generation
- ✅ **Main development work**

### Use **Qwen 14B** (`/q14b`) for:
- ✅ Alternative to DeepSeek V2
- ✅ When DeepSeek feels slow
- ✅ Complex algorithms
- ✅ Large refactoring tasks

### Use **Qwen 7B** (`/q7b`) for:
- ✅ Daily development
- ✅ Rapid prototyping
- ✅ Scripts and automation
- ✅ Code documentation
- ✅ Simple testing and debugging
- ✅ When multitasking with other apps

### Use **Qwen 3B** (`/q3b`) for:
- ✅ Quick syntax questions
- ✅ Snippet explanations
- ✅ Language conversions
- ✅ Quick fixes
- ✅ When you need instant responses

---

## 💡 7. Tips & Tricks

### 🔧 M4 Pro Optimizations

#### 1. Free RAM Before Loading Large Models
```bash
# Close Chrome/heavy browsers
# Close unnecessary apps
# Then load DeepSeek V2
> /ds
```

#### 2. Pre-download Models
```bash
# Download models in advance (with good internet)
> /download ds
> /download q14b
> /download q7b
# Then work offline!
```

#### 3. Monitor RAM Usage
```bash
# In another terminal:
watch -n 2 'ps aux | grep mlx-code'
# Or use Activity Monitor
```

#### 4. Manage Disk Space
```bash
# See disk usage
> /installed

# Delete unused models
> /delete q1.5b
> /delete phi3
# Free ~3-4GB
```

### 🚀 Performance Tips

#### Speed Up Generation
```bash
# Reduce max tokens for faster responses
> /tokens 512  # Default is 1024

# For longer responses
> /tokens 2048
```

#### Increase Context Window
```bash
# Default 24000 characters
> /ctx 48000  # Double context for large projects
```

### 📊 Download Speed Comparison

#### Standard Method (HuggingFace Hub)
- Speed: ~5-10 MB/s
- Time for DeepSeek V2 (9GB): **~15-30 min**

#### With git-lfs (Recommended!)
```bash
# Install git-lfs once:
brew install git-lfs
git lfs install

# Then MLX-CODE will automatically use git-lfs
> /download ds
# Speed: 20-40 MB/s
# Time: **~5-10 min** ⚡
```

### ⌨️ Keyboard Shortcuts (v2.1+)

**NEW!** MLX-CODE now has advanced terminal input with `prompt-toolkit`:

```bash
# Install for better experience:
pip install prompt-toolkit
```

#### Features:

| Shortcut | Action |
|----------|--------|
| **↑ / ↓** | Navigate command history (previous/next commands) |
| **← / →** | Move cursor left/right to edit text |
| **Tab** | Auto-complete commands (e.g., `/mod` → `/models`) |
| **Ctrl+C** | Clear current input buffer (no more ^C symbols!) |
| **Ctrl+D** | Exit MLX-CODE |
| **Enter** | Send message (requires empty line or Enter twice) |

#### Benefits:

- ✅ **No more broken paste!** Paste multi-line code without issues
- ✅ **Command history** saved to `~/.mlx-code/command_history.txt`
- ✅ **Arrow keys work** like modern terminals (zsh, bash)
- ✅ **Edit typos easily** with left/right arrows
- ✅ **Tab completion** for all commands

**Example workflow:**
```bash
# Press ↑ to recall last command
> /download ds

# Press ← to move cursor and edit
> /download q7b  # Changed ds → q7b

# Press Tab to auto-complete
> /mod [Tab] → /models
```

---

## 🎓 8. Practical Examples

### Example 1: Complex Full-Stack Project

```bash
~/mlx-code

# Load most powerful model
> /ds

# Ask for complete architecture
> design a microservices architecture for an e-commerce platform with:
- API gateway
- user service
- product service
- payment service
- message queue
- database per service

# Model will generate detailed, production-ready architecture
```

### Example 2: Debug + Quick Fix

```bash
# Use DeepSeek for debugging
> /ds

# Open file with error
> /open src/main.py

# Ask for debug
> find the bug in the calculate_total function

# For quick fix, switch to Q3B
> /q3b
> how to fix this import error?
```

### Example 3: Optimized Workflow

```bash
# Morning: Project setup (use DeepSeek V2)
> /ds
> create a Flask project structure with SQLAlchemy

# Afternoon: Development (use DeepSeek or Q7B)
> /ds  # or /q7b
> implement CRUD API endpoints for users

# Evening: Quick fixes (use Q3B)
> /q3b
> explain this list comprehension syntax
```

---

## 🔧 9. Troubleshooting

### Issue: Out of Memory Error

**Symptoms:**
```
[WARNING] Generating with a model that requires 17577 MB...
libc++abi: terminating due to uncaught exception...
Insufficient Memory (kIOGPUCommandBufferCallbackErrorOutOfMemory)
```

**Solution:**
```bash
# Switch to smaller model
> /ds    # DeepSeek V2 - safe and stable
> /q14b  # Qwen 14B - alternative
> /q7b   # Qwen 7B - very safe
```

### Issue: Slow Generation

**Causes:**
- Model too large for available RAM
- Other apps using memory
- Swap memory being used

**Solutions:**
```bash
# 1. Switch to faster model
> /q7b

# 2. Reduce max tokens
> /tokens 512

# 3. Close other apps

# 4. Check RAM usage
# Activity Monitor → Memory tab
```

### Issue: Model Download Fails

**Solutions:**
```bash
# 1. Check internet connection
# 2. Try again (download resumes automatically)
# 3. Use git-lfs for faster, more reliable downloads
brew install git-lfs
git lfs install
> /download ds

# 4. Try smaller model first
> /download q3b
```

### Issue: Model Not Switching

**Solution:**
```bash
# Check installed models
> /installed

# If model not installed, download first
> /download ds

# Then switch
> /ds
```

---

## ❓ 10. FAQ

### **Q: Can I use Qwen 32B on M4 Pro 24GB?**
**A:** Not recommended. It requires ~20GB RAM and crashes with "Insufficient Memory". Use **DeepSeek V2** (`/ds`) instead - same quality, more stable!

### **Q: Is DeepSeek V2 really as good as Qwen 32B?**
**A:** YES! For coding tasks, it's equal or better. Specifically trained on code with excellent benchmark results.

### **Q: How much faster is M4 Pro vs M1/M2?**
**A:** M4 Pro is ~30-40% faster in MLX inference thanks to improved Neural Engine and memory bandwidth.

### **Q: Can I use even larger models?**
**A:** With 24GB, DeepSeek V2 (~12GB) and Qwen 14B (~12GB) are the maximum safe sizes. Models 32B+ require 48GB+ RAM.

### **Q: Do 4-bit quantized models lose quality?**
**A:** Minimal loss (~2-3%). 4-bit quantized models are excellent for Apple Silicon.

### **Q: Can I use mlx-code for commercial projects?**
**A:** Yes! Check individual model licenses (generally permissive like Apache 2.0).

### **Q: Which model for daily coding?**
**A:** **DeepSeek V2** (`/ds`) - Best balance of quality, speed, and stability for M4 Pro 24GB!

### **Q: Can I switch models during a session?**
**A:** Yes! Just use the model alias command (e.g., `/ds`, `/q7b`, `/q3b`) anytime.

---

## 🎯 Final Recommendations

### Optimal Setup for M4 Pro 24GB:

1. **Install these 3 models:**
   ```bash
   /download ds        # Best quality & stability
   /download q7b       # Fast backup
   /download q3b       # Quick tasks
   ```

2. **Set DeepSeek V2 as default:**
   - Edit line 45 in `~/mlx-code`:
   ```python
   DEFAULT_MODEL = "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit"
   ```

3. **Keep git-lfs installed:**
   ```bash
   brew install git-lfs
   git lfs install
   ```

### Model for Every Situation:

| Situation | Model | Command |
|-----------|-------|---------|
| 🏗️ System architecture | DeepSeek V2 | `/ds` |
| 💻 Daily development | DeepSeek V2 / Q7B | `/ds` or `/q7b` |
| ⚡ Quick questions | Qwen 3B | `/q3b` |
| 🐛 Complex debugging | DeepSeek V2 | `/ds` |
| 📝 Documentation | Qwen 7B | `/q7b` |
| 🧪 Testing | DeepSeek V2 | `/ds` |

### Quick Reference Card:

```
BEST:       /ds         DeepSeek V2 (~11GB) ⭐⭐⭐⭐⭐
FAST:       /q7b        Qwen 7B (~6GB)      ⭐⭐⭐⭐
QUICK:      /q3b        Qwen 3B (~4GB)      ⭐⭐⭐
ALT:        /q14b       Qwen 14B (~11GB)    ⭐⭐⭐⭐⭐
AVOID:      /q32b       Too large - CRASHES ❌
```

---

## 📞 Support

**GitHub Issues:** https://github.com/YOUR-REPO/mlx-code/issues
**Documentation:**
- [README.md](README.md) - Main guide
- [GUIDE-M1-16GB.md](GUIDE-M1-16GB.md) - For M1/M2/M3 16GB
- [CHANGELOG-27-NOV-2025.md](CHANGELOG-27-NOV-2025.md) - Latest changes

**Created with ❤️ for developers on Apple Silicon M4 Pro**

---

**Last Updated:** February 25, 2026
**Version:** 3.0
**Tested On:** M4 Pro 24GB with macOS Sequoia

**What's New in v3.0:** Streaming output, git integration, 7 new commands, auto-save, no env activation needed. See [CHANGELOG-25-FEB-2026.md](CHANGELOG-25-FEB-2026.md).
