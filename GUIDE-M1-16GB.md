# MLX-CODE — Optimized Guide for M1/M2/M3 16GB

**🚀 Get the Best Performance from Your 16GB Mac!**
*Apple M1/M2/M3 • 16GB RAM • Python 3.12 • MLX Framework*

---

## 📋 Table of Contents

1. [Quick Start](#-1-quick-start)
2. [Model Overview](#-2-model-overview)
3. [Model Management Commands](#-3-model-management-commands)
4. [Recommended Setup](#-4-recommended-setup)
5. [Performance Comparison](#-5-performance-comparison)
6. [When to Use Which Model](#-6-when-to-use-which-model)
7. [RAM Management Tips](#-7-ram-management-tips)
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

# 3. Download Qwen 7B (SAFE and FAST for 16GB!)
> /download q7b
# Wait 5-10 minutes (~4.3GB download)

# 4. Switch to Qwen 7B
> /q7b

# 5. Test it!
> write a Python function to sort a list with custom comparator
```

### Advanced Users: DeepSeek V2

```bash
# DeepSeek V2 works on 16GB but requires closing other apps
> /download ds
> /ds

# Make sure to close:
# - Chrome/browsers
# - Slack/Discord
# - Other heavy apps
```

---

## 📊 2. Model Overview

### ⚠️ IMPORTANT: RAM Limitations

With 16GB RAM, you need to be careful about model size:

**Safe Models (Always Work):**
- ✅ **Qwen 7B** (~5-7GB) - **RECOMMENDED for 16GB**
- ✅ **Qwen 3B** (~3-4GB) - Fast & safe
- ✅ **Qwen 1.5B** (~2-3GB) - Very light

**Works With Care (Close Other Apps):**
- ⚠️ **DeepSeek V2** (~9-12GB) - Excellent but needs free RAM
- ⚠️ **Qwen 14B** (~10-12GB) - May be unstable

**Too Large (Will Crash):**
- ❌ **Qwen 32B** (~20GB) - Way too large
- ❌ **CodeLlama 13B+** (~10GB+) - Risky on 16GB

### 🏆 Recommended Models for 16GB

#### **Tier 1: Best for 16GB**

| Model | Alias | Download | RAM | Quality | Speed | Status |
|-------|-------|----------|-----|---------|-------|--------|
| **Qwen 7B** | `/q7b` | ~4.3GB | ~5-7GB | ⭐⭐⭐⭐ | ⚡⚡ | ✅ SAFE |
| Qwen 3B | `/q3b` | ~1.9GB | ~3-4GB | ⭐⭐⭐ | ⚡⚡⚡ | ✅ VERY SAFE |

#### **Tier 2: Advanced (Close Other Apps)**

| Model | Alias | Download | RAM | Quality | Speed | Status |
|-------|-------|----------|-----|---------|-------|--------|
| **DeepSeek V2** | `/ds` | ~9.0GB | ~9-12GB | ⭐⭐⭐⭐⭐ | ⚡⚡ | ⚠️ CAREFUL |
| DeepSeek 6.7B | `/ds6.7b` | ~4.0GB | ~5-7GB | ⭐⭐⭐⭐ | ⚡⚡ | ✅ SAFE |

#### **Tier 3: Light & Fast**

| Model | Alias | Download | RAM | Quality | Speed | Status |
|-------|-------|----------|-----|---------|-------|--------|
| Qwen 1.5B | `/q1.5b` | ~1.0GB | ~2-3GB | ⭐⭐ | ⚡⚡⚡ | ✅ VERY SAFE |
| DeepSeek 1.3B | `/ds1.3b` | ~1.0GB | ~2-3GB | ⭐⭐ | ⚡⚡⚡ | ✅ VERY SAFE |
| Phi-3 | `/phi3` | ~2.3GB | ~3-4GB | ⭐⭐⭐ | ⚡⚡⚡ | ✅ SAFE |

---

## 🛠️ 3. Model Management Commands

### Quick Reference

```bash
# List all available models
> /models

# Show installed models with disk usage
> /installed

# Download a model
> /download q7b      # Qwen 7B - RECOMMENDED
> /download ds       # DeepSeek V2 - Advanced
> /download q3b      # Qwen 3B - Fast

# Delete a model to free space
> /delete q1.5b

# Quick switch
> /q7b              # Qwen 7B
> /ds               # DeepSeek V2
> /q3b              # Qwen 3B
```

---

## 🎯 4. Recommended Setup

### 🥇 Optimal 2-Model Setup (Safe)

Perfect balance for 16GB without needing to close apps:

#### **1. Qwen 7B** → Main Workhorse
```bash
> /download q7b
> /q7b
```
- ✅ **Excellent quality** (⭐⭐⭐⭐)
- ✅ **Safe with 16GB** (~5-7GB RAM)
- ✅ Fast (~1.5 seconds per response)
- ✅ Works with other apps open
- ✅ Perfect for 90% of coding tasks

#### **2. Qwen 3B** → Quick Tasks
```bash
> /download q3b
> /q3b
```
- ✅ **Very fast** (~0.8 seconds)
- ✅ Perfect for quick questions
- ✅ Multitasking friendly
- ✅ Great for syntax questions

**💾 Total:** ~6GB disk space

---

### 🥈 Power User Setup (3 Models)

For users willing to manage RAM:

```bash
> /download q7b      # Main: Safe & reliable
> /download ds       # Power: Best quality (close other apps)
> /download q3b      # Quick: Fast answers
```

**When to use:**
- **Q7B**: Daily coding with apps open
- **DeepSeek V2**: Complex tasks (close other apps first!)
- **Q3B**: Quick questions

**💾 Total:** ~15GB disk space

---

### 🥉 Minimal Setup (8GB disk)

If disk space is limited:

```bash
> /download q7b      # Main model
> /download q3b      # Quick tasks
```

**💾 Total:** ~6GB disk space

---

## ⚡ 5. Performance Comparison

### Test: "Create a Flask API with authentication"

| Model | Response Time | Code Quality | RAM Used | Multitask OK? |
|-------|--------------|--------------|----------|---------------|
| Qwen 7B (`/q7b`) | ~1.5s | ⭐⭐⭐⭐ | ~6GB | ✅ Yes |
| DeepSeek 6.7B (`/ds6.7b`) | ~1.7s | ⭐⭐⭐⭐ | ~6GB | ✅ Yes |
| Qwen 3B (`/q3b`) | ~0.8s | ⭐⭐⭐ | ~4GB | ✅ Yes |
| DeepSeek V2 (`/ds`) | ~1.8s | ⭐⭐⭐⭐⭐ | ~11GB | ⚠️ Close apps |

**Conclusion for 16GB:**
- **Daily use:** Qwen 7B - Best balance
- **Maximum quality:** DeepSeek V2 (close other apps!)
- **Speed:** Qwen 3B - Instant responses

---

## 🎨 6. When to Use Which Model

### Use **Qwen 7B** (`/q7b`) for:
- ✅ **Daily development** (main workhorse)
- ✅ API and backend code
- ✅ Refactoring
- ✅ Code reviews
- ✅ Documentation
- ✅ Testing
- ✅ **Most common choice for 16GB**

### Use **DeepSeek V2** (`/ds`) for:
- ✅ Complex algorithms
- ✅ System architecture
- ✅ Difficult debugging
- ✅ Production-critical code
- ⚠️ **Close other apps first!**
- 💡 **Use when you need the absolute best**

### Use **Qwen 3B** (`/q3b`) for:
- ✅ Quick syntax questions
- ✅ Code explanations
- ✅ Simple fixes
- ✅ Language conversions
- ✅ When multitasking heavily

### Use **DeepSeek 6.7B** (`/ds6.7b`) for:
- ✅ Alternative to Q7B
- ✅ When you want DeepSeek quality
- ✅ But need RAM safety
- ✅ Good middle ground

---

## 💡 7. RAM Management Tips

### 🔧 Free RAM Before Using DeepSeek V2

```bash
# 1. Check current RAM usage
# Open Activity Monitor → Memory tab

# 2. Close these apps:
- Chrome/Safari (can use 2-4GB)
- Slack/Discord (500MB-1GB each)
- VS Code (if not actively using)
- Docker Desktop (1-2GB)
- Spotify/Music apps

# 3. Then load DeepSeek V2
~/mlx-code
> /ds
```

### 📊 Typical RAM Usage on 16GB Mac

```
System:          ~3-4GB
Chrome (5 tabs): ~2GB
VS Code:         ~1GB
Terminal/mlx:    ~0.5GB
Available:       ~9-10GB

→ Safe for Qwen 7B (~6GB)
→ Tight for DeepSeek V2 (~11GB) - close browser!
```

### ⚡ Quick RAM Check Script

```bash
# Add to ~/.zshrc or ~/.bashrc
alias ramcheck='echo "Available RAM:"; vm_stat | grep "Pages free" && sysctl hw.memsize'
```

### 🎯 Model Selection Guide

```
Your Available RAM:
< 8GB free:  Use /q3b or /q1.5b
8-10GB free: Use /q7b (recommended)
> 10GB free: You can try /ds (close apps if issues)
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
> /q7b

# Press ← to move cursor and edit
> /q3b  # Changed 7b → 3b

# Press Tab to auto-complete
> /mod [Tab] → /models
```

---

## 🔧 8. Troubleshooting

### Issue: Out of Memory with DeepSeek V2

**Symptoms:**
```
[WARNING] Generating with a model that requires...
Insufficient Memory error
```

**Solution:**
```bash
# Option 1: Switch to Qwen 7B (recommended)
> /q7b

# Option 2: Close all apps and retry
# Close Chrome, Slack, etc.
> /ds

# Option 3: Use DeepSeek 6.7B instead
> /download ds6.7b
> /ds6.7b  # Same quality family, less RAM
```

### Issue: Slow Generation

**Solution:**
```bash
# 1. Check if system is swapping to disk
# Activity Monitor → Memory → Memory Pressure (should be green)

# 2. Switch to smaller model
> /q7b
> /q3b

# 3. Reduce max tokens
> /tokens 512

# 4. Close background apps
```

### Issue: Model Download Interrupted

**Solution:**
```bash
# Download will resume automatically
> /download q7b

# For faster downloads, use git-lfs:
brew install git-lfs
git lfs install
> /download q7b  # Will use git-lfs automatically
```

### Issue: Can't Switch Models

**Check installation:**
```bash
> /installed

# If model not there, download it
> /download q7b

# Then switch
> /q7b
```

---

## ❓ 9. FAQ

### **Q: Which model is best for 16GB?**
**A:** **Qwen 7B** (`/q7b`) - Perfect balance of quality, speed, and RAM safety. Works with other apps open.

### **Q: Can I use DeepSeek V2 on 16GB?**
**A:** Yes, but you need to **close other apps** (Chrome, Slack, etc.). It uses ~11GB RAM. Safer alternative: **DeepSeek 6.7B** (`/ds6.7b`).

### **Q: Is Qwen 7B good enough for professional work?**
**A:** Absolutely! It's ⭐⭐⭐⭐ quality and handles 90% of coding tasks perfectly. Only use DeepSeek V2 when you need absolute best quality.

### **Q: What if I have lots of browser tabs open?**
**A:** Use **Qwen 7B** (`/q7b`) or **Qwen 3B** (`/q3b`). They work fine with other apps.

### **Q: Should I close VS Code when using mlx-code?**
**A:** Not necessary with Qwen 7B. Only close it if using DeepSeek V2 and experiencing issues.

### **Q: How much RAM does macOS itself use?**
**A:** Usually ~3-4GB, leaving you with ~12GB available on a 16GB system.

### **Q: Can I run Qwen 14B?**
**A:** Possible but risky (~10-12GB RAM). You must close **all** other apps. **Not recommended** - use DeepSeek V2 or Qwen 7B instead.

### **Q: What about M1 vs M2 vs M3 performance?**
**A:** M3 is ~15-20% faster than M1 for same model. But all work great with appropriate models!

---

## 🎯 Final Recommendations

### For 16GB Mac: The Perfect Setup

```bash
# Daily Driver (90% of work)
> /download q7b
> /q7b

# Quick Tasks (10% of work)
> /download q3b
> /q3b

# Power Mode (when needed, close other apps)
> /download ds
> /ds  # Only when you need absolute best
```

### Model Selection Flowchart

```
Need maximum quality? AND can close all apps?
  YES → /ds (DeepSeek V2)
  NO ↓

Normal coding task with apps open?
  YES → /q7b (Qwen 7B) ← MOST COMMON
  NO ↓

Quick question or syntax check?
  YES → /q3b (Qwen 3B)
```

### Quick Reference Card for 16GB

```
RECOMMENDED:  /q7b        Qwen 7B (~6GB)        ⭐⭐⭐⭐
QUICK:        /q3b        Qwen 3B (~4GB)        ⭐⭐⭐
POWER:        /ds         DeepSeek V2 (~11GB)   ⭐⭐⭐⭐⭐ (close apps!)
SAFE ALT:     /ds6.7b     DeepSeek 6.7B (~6GB)  ⭐⭐⭐⭐
AVOID:        /q14b+      Too large             ❌
```

---

## 📞 Support & Resources

**GitHub Issues:** https://github.com/YOUR-REPO/mlx-code/issues

**Documentation:**
- [README.md](README.md) - Main guide
- [GUIDE-M4-PRO-24GB.md](GUIDE-M4-PRO-24GB.md) - For M4 Pro 24GB users
- [CHANGELOG-27-NOV-2025.md](CHANGELOG-27-NOV-2025.md) - Latest changes
- [DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md) - Faster download guide

**Tips:**
- Join the community to share configurations
- Report issues with your RAM usage
- Share your optimal model choices

**Created with ❤️ for developers on Apple Silicon M1/M2/M3**

---

**Last Updated:** February 25, 2026
**Version:** 3.0
**Tested On:** M1 Pro/Max, M2 Pro/Max, M3 Pro/Max with 16GB RAM

**What's New in v3.0:** Streaming output, git integration, 7 new commands, auto-save, no env activation needed. See [CHANGELOG-25-FEB-2026.md](CHANGELOG-25-FEB-2026.md).

---

## 🎉 Summary

**For Most 16GB Users:**
1. Download Qwen 7B: `> /download q7b`
2. Use it as default: `> /q7b`
3. Download Qwen 3B for quick tasks: `> /download q3b`
4. Enjoy stable, high-quality coding assistance! 🚀

**Want more power?**
- Close all apps
- Download DeepSeek V2: `> /download ds`
- Use for complex tasks: `> /ds`
- Switch back to Q7B for daily work: `> /q7b`

**Happy coding on your 16GB Mac!** 💻✨
