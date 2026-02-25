# Alternative Model Download Methods

**Last Updated:** February 25, 2026

**⚠️ Important:** MLX-CODE starts with **Qwen 1.5B** (1GB) by default for fast setup. This is **only a demo model** with limited quality. For real coding work, **upgrade to 7B, 14B, or DeepSeek** using this guide.

This guide explains different methods to download AI models for MLX-CODE, with **git-lfs being the recommended approach** for better reliability.

---

## 🚀 Recommended Method: git-lfs Clone

**Why git-lfs is better:**
- ✅ **Much faster** (typically 3-5x faster than HuggingFace Hub)
- ✅ **More reliable** with unstable connections
- ✅ **Automatic resume** if interrupted
- ✅ **Better for slow connections** (doesn't timeout/stall)
- ✅ **Verifies file integrity** automatically

### Step 1: Install git-lfs

```bash
# Install git-lfs via Homebrew
brew install git-lfs

# Configure git-lfs
git lfs install
```

### Step 2: Download Models Using git clone

**For Qwen 1.5B (Default - ~1GB):**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit
```

**For Qwen 3B (~1.9GB):**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/qwen2.5-coder-3b-instruct-4bit
```

**For Qwen 7B (~4.3GB):**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/qwen2.5-coder-7b-instruct-4bit
```

**For Qwen 14B (~8.5GB) - Better quality, requires 16GB+ RAM:**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/Qwen2.5-Coder-14B-Instruct-4bit
```

**For DeepSeek-Coder-V2-Lite (~9GB) - Best code quality:**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit
```

**For DeepSeek-Coder 1.3B (~800MB) - Smallest, fast:**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/DeepSeek-Coder-1.3B-Instruct-4bit
```

**For Mistral 7B (~4GB):**
```bash
cd /tmp
git clone https://huggingface.co/mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

### Step 3: Move to HuggingFace Cache

After the clone completes, move the model to the correct location:

```bash
# Create the models directory if it doesn't exist
mkdir -p ~/.cache/huggingface/hub

# Move the cloned model (example for Mistral)
mv /tmp/Mistral-7B-Instruct-v0.3-4bit ~/.cache/huggingface/hub/models--mlx-community--Mistral-7B-Instruct-v0.3-4bit

# Or for Qwen models:
mv /tmp/qwen2.5-coder-3b-instruct-4bit ~/.cache/huggingface/hub/models--mlx-community--qwen2.5-coder-3b-instruct-4bit

# For Qwen 14B:
mv /tmp/Qwen2.5-Coder-14B-Instruct-4bit ~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-Coder-14B-Instruct-4bit

# For DeepSeek-Coder-V2-Lite:
mv /tmp/DeepSeek-Coder-V2-Lite-Instruct-4bit ~/.cache/huggingface/hub/models--mlx-community--DeepSeek-Coder-V2-Lite-Instruct-4bit

# For DeepSeek-Coder 1.3B:
mv /tmp/DeepSeek-Coder-1.3B-Instruct-4bit ~/.cache/huggingface/hub/models--mlx-community--DeepSeek-Coder-1.3B-Instruct-4bit
```

**Note:** After moving, MLX-CODE will detect and use the model automatically!

### Step 4: Verify Installation

```bash
# Check the model is in the cache
ls -lh ~/.cache/huggingface/hub/models--mlx-community--*/

# Launch MLX-CODE and switch to the model
cd ~/Documents/Progetti/your-project
~/mlx-code   # No env activation needed in v3.0+

# Inside MLX-CODE:
/mistral    # or /q3b, /q7b, /q14b, /deepseek, /ds, etc.
```

---

## 🔄 Alternative Method: HuggingFace Hub (Default)

This is the method MLX-CODE uses automatically when you switch models with `/q3b`, `/mistral`, etc.

**Pros:**
- Automatic - just use the `/model` command
- No manual file management

**Cons:**
- ❌ Can be slow with some connections
- ❌ May stall/timeout on unstable networks
- ❌ Harder to resume if interrupted

### Usage:

Simply use the model switch commands in MLX-CODE:

```
/q1.5b       # Switch to Qwen 1.5B (downloads if not cached)
/q3b         # Switch to Qwen 3B
/q7b         # Switch to Qwen 7B
/q14b        # Switch to Qwen 14B (requires 16GB+ RAM)
/deepseek    # Switch to DeepSeek-Coder-V2-Lite (best for code)
/ds          # Alias for DeepSeek
/mistral     # Switch to Mistral 7B
```

The first time you use a model, it will download automatically. This may take 5-30 minutes depending on your internet speed.

---

## 🆘 Troubleshooting Downloads

### Download is Very Slow (< 500 KB/s)

**Solution:** Use git-lfs method instead (see above). It's typically 3-5x faster.

### Download Keeps Stalling/Timing Out

**Solution:** Use git-lfs method. Git handles network interruptions much better than the HuggingFace Hub API.

**If git-lfs also stalls:**
1. Check your internet connection
2. Try downloading at a different time (off-peak hours)
3. Consider using a VPN to a different location
4. As a last resort, use a smaller model:
   - If 7B fails, try 3B
   - If 3B fails, try 1.5B

### "Model not found" After Manual Download

Make sure you moved the model to the correct directory name format:

```bash
# Correct format:
~/.cache/huggingface/hub/models--mlx-community--Mistral-7B-Instruct-v0.3-4bit/

# NOT:
~/.cache/huggingface/hub/Mistral-7B-Instruct-v0.3-4bit/  # ❌ Wrong
```

The directory must start with `models--` and use `--` instead of `/` in the repo path.

### Clean Up Failed Downloads

If you have incomplete downloads cluttering your cache:

```bash
# See what's taking up space
du -sh ~/.cache/huggingface/hub/models--mlx-community--*/

# Remove a specific incomplete model
rm -rf ~/.cache/huggingface/hub/models--mlx-community--MODEL-NAME/

# Or clean everything and start fresh
rm -rf ~/.cache/huggingface/hub/
```

---

## 📊 Download Speed Comparison

Based on real-world testing with a typical home connection:

| Method | Average Speed | 4GB Model Time | Reliability |
|--------|---------------|----------------|-------------|
| **git-lfs clone** | 3-5 MB/s | 15-20 min | ⭐⭐⭐⭐⭐ |
| HuggingFace Hub | 150-500 KB/s | 2-4 hours | ⭐⭐⭐ |
| Browser download | N/A | Manual setup | ⭐⭐ |

**Recommendation:** Always use git-lfs for models larger than 1GB.

---

## 🎯 Quick Reference Commands

```bash
# Install git-lfs (one-time setup)
brew install git-lfs && git lfs install

# Download Mistral 7B (recommended for best quality)
cd /tmp && git clone https://huggingface.co/mlx-community/Mistral-7B-Instruct-v0.3-4bit

# Monitor download progress (in another terminal)
watch -n 5 'du -sh /tmp/Mistral-7B-Instruct-v0.3-4bit'

# Move to cache after complete
mv /tmp/Mistral-7B-Instruct-v0.3-4bit ~/.cache/huggingface/hub/models--mlx-community--Mistral-7B-Instruct-v0.3-4bit

# Use in MLX-CODE
~/mlx-code
/mistral
```

---

## 💡 Tips

1. **Download during off-peak hours** (late night/early morning) for faster speeds
2. **Use a wired connection** instead of Wi-Fi when possible
3. **Close other internet-heavy applications** during download
4. **Consider downloading smaller models first** to test your connection
5. **Keep terminal window open** - don't let your Mac sleep during download

---

## 💻 Recommended Models for M1/M2 MacBook Pro 16GB RAM

If you have an M1/M2/M3 MacBook Pro with 16GB RAM, here are the best model choices:

### ⭐ Best Overall: DeepSeek-Coder-V2-Lite (~9GB)
```bash
# In MLX-CODE:
/deepseek

# Or download manually:
cd /tmp && git clone https://huggingface.co/mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit
mv /tmp/DeepSeek-Coder-V2-Lite-Instruct-4bit ~/.cache/huggingface/hub/models--mlx-community--DeepSeek-Coder-V2-Lite-Instruct-4bit
```
**Pros:** Best code quality, specialized for programming
**Cons:** Uses ~9GB RAM, may slow down with many apps open
**Recommendation:** ⭐⭐⭐⭐⭐ Best if you close other apps while coding

### 🎯 Safe Choice: Qwen 7B (~5GB)
```bash
# In MLX-CODE:
/q7b
```
**Pros:** Good balance, leaves RAM for other apps
**Cons:** Not as good as DeepSeek for complex code
**Recommendation:** ⭐⭐⭐⭐ Best for multitasking

### ⚠️ Advanced: Qwen 14B (~9GB)
```bash
# In MLX-CODE:
/q14b
```
**Pros:** Better quality than 7B
**Cons:** Uses significant RAM, **close all other apps**
**Recommendation:** ⭐⭐⭐ Only if you need max quality and can close everything

### 📊 RAM Usage Comparison

| Model | RAM Used | Quality | Speed | Multitasking |
|-------|----------|---------|-------|--------------|
| Qwen 1.5B | ~2GB | ⭐⭐ | ⚡⚡⚡ | ✅✅✅ |
| Qwen 3B | ~3GB | ⭐⭐⭐ | ⚡⚡ | ✅✅✅ |
| **Qwen 7B** | ~5GB | ⭐⭐⭐⭐ | ⚡⚡ | ✅✅ |
| **DeepSeek-V2-Lite** | ~9GB | ⭐⭐⭐⭐⭐ | ⚡ | ✅ |
| Qwen 14B | ~9GB | ⭐⭐⭐⭐ | ⚡ | ⚠️ |

### 💡 Tips for 16GB RAM:

1. **Close Chrome/Browser** before using 14B models (saves 2-4GB)
2. **Close Slack/Discord** (saves 500MB-1GB)
3. **Use Activity Monitor** to check available RAM
4. **Start with 7B**, upgrade to DeepSeek if needed
5. **Avoid 14B** unless you really need it

### 🔧 How to Delete Old Models

If you want to free up space and remove Qwen 1.5B and 3B:

```bash
# Check current models and sizes
du -sh ~/.cache/huggingface/hub/models--mlx-community--*/

# Delete Qwen 1.5B (~1GB freed)
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-Coder-1.5B-Instruct-4bit/

# Delete Qwen 3B (~2GB freed)
rm -rf ~/.cache/huggingface/hub/models--mlx-community--qwen2.5-coder-3b-instruct-4bit/

# Verify they're gone
ls -lh ~/.cache/huggingface/hub/
```

**Note:** You can always re-download them later with `/q1.5b` or `/q3b`

---

*For more help, see [README.md](README.md) or [quick-start.md](quick-start.md)*
