# Changelog — November 26, 2025

## Main Changes

### 1. Default Model Changed: 3B → 1.5B

**Reason:**
- Faster download (~1GB vs ~2GB)
- Works on all Macs (even 8GB RAM)
- Clearly marked as "demo model" in documentation

**Modified files:**
- `mlx-code-v2.py` (line 44)
- `~/mlx-code` (updated with v2)

### 2. New Models Added

**Now available:**
- `/q1.5b` - Qwen 1.5B (default demo)
- `/q3b` - Qwen 3B
- `/q7b` - Qwen 7B
- `/q14b` - **NEW** Qwen 14B
- `/deepseek` or `/ds` - **NEW** DeepSeek-Coder-V2-Lite
- `/deepseek-1.3b` - **NEW** DeepSeek 1.3B
- `/mistral` or `/m7b` - Mistral 7B

**Modified file:**
- `mlx-code-v2.py` (lines 46-56)

### 3. Documentation Fully Updated

**README.md:**
- Clear warning: 1.5B is demo only
- Complete table with DeepSeek and 14B
- Quick upgrade guide
- RAM recommendations (8GB vs 16GB)

**quick-start.md:**
- Updated table with new models
- Warning about 1.5B
- Quick upgrade guide

**DOWNLOAD-MODELS.md:**
- Note at top about 1.5B demo
- DeepSeek instructions
- Qwen 14B instructions
- Dedicated M1 16GB RAM section
- How to delete old models

**GUIDE-M1-16GB.md:** NEW FILE
- Complete guide for M1/M2/M3 with 16GB
- Recommendation: DeepSeek is best
- How to delete 1.5B and 3B
- Model comparison table
- Troubleshooting

---

## Current Model Status

### Installed Models:
- Qwen 7B (~4GB) - already present
- Qwen 3B (~1.7GB) - auto-downloaded
- DeepSeek-V2-Lite (~10GB) - in cache, ready to use
- Qwen 1.5B - present or will download on first launch

### Optional Cleanup:
```bash
# Delete 3B if not needed (frees 1.7GB)
rm -rf ~/.cache/huggingface/hub/models--mlx-community--qwen2.5-coder-3b-instruct-4bit/

# Delete 1.5B if not needed (frees 1GB)
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-Coder-1.5B-Instruct-4bit/
```

---

## How to Use

### 1. Launch MLX-CODE:
```bash
~/mlx-code
```

### 2. Switch model immediately:
```bash
# Best for coding:
> /deepseek

# Or safe choice:
> /q7b
```

### 3. DeepSeek should load WITHOUT downloading (already cached)

---

## Final Recommendations

### For M1 16GB:

**Optimal Setup:**
1. **Delete** 1.5B and 3B (saves ~3GB)
2. **Keep** Qwen 7B (fast backup)
3. **Use** DeepSeek as primary

**Commands to use:**
- Serious coding → `/deepseek` (close Chrome)
- Quick tasks → `/q7b` (multitasking ok)
- **DON'T** use `/q1.5b` or `/q3b` (poor quality)

---

## Bug Fixes

### FIXED: `/deepseek` was not working
**Cause:** Was using old version of mlx-code
**Fix:** `~/mlx-code` now uses updated `mlx-code-v2.py`

### FIXED: 3B kept re-downloading
**Cause:** DEFAULT_MODEL was set to 3B
**Fix:** Changed to 1.5B

### FIXED: Confusing model documentation
**Cause:** Not clear which model to use
**Fix:** All docs updated with warnings and recommendations

---

## Modified/Created Files

### Modified:
- `mlx-code-v2.py` (DEFAULT_MODEL + new aliases)
- `~/mlx-code` (replaced with v2)
- `README.md` (model section completely redone)
- `quick-start.md` (model table updated)
- `DOWNLOAD-MODELS.md` (DeepSeek + 14B + M1 guide)

### Created:
- `GUIDE-M1-16GB.md` (complete guide)
- `CHANGELOG-26-NOV-2025.md` (this file)

---

## Suggested Next Steps

1. **Test `/deepseek`** in your updated MLX-CODE
2. **Delete 1.5B and 3B** if not needed (command above)
3. **Set DeepSeek as default** if you like it (edit line 44 in ~/mlx-code)
4. **Close browser** when using DeepSeek (to free RAM)

---

For questions or issues, see:
- [README.md](README.md) - Complete guide
- [GUIDE-M1-16GB.md](GUIDE-M1-16GB.md) - Hardware-specific guide
- [DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md) - Model details
