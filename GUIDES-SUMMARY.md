# 📚 MLX-CODE Guides - Complete Summary

**Comprehensive English guides for all Apple Silicon Macs**

---

## 📖 Available Guides

### **For M4 Pro 24GB Users**

- **[GUIDE-M4-PRO-24GB.md](GUIDE-M4-PRO-24GB.md)** ⭐
  - Complete guide for M4 Pro with 24GB RAM
  - Includes Q32B warning (crashes with OOM)
  - Recommends DeepSeek V2 as best choice
  - 3-model optimal setup
  - Performance benchmarks
  - Troubleshooting section

---

### **For M1/M2/M3 16GB Users**

- **[GUIDE-M1-16GB.md](GUIDE-M1-16GB.md)** ⭐
  - Optimized for 16GB RAM
  - Safe model recommendations
  - RAM management tips
  - When to close apps
  - Tier-based model selection
  - Troubleshooting for 16GB

---

## 🎯 Quick Navigation

### Pick Your Guide:

```
┌─────────────────────────────────────────┐
│ What Mac do you have?                   │
├─────────────────────────────────────────┤
│ M4 Pro 24GB                             │
│  → GUIDE-M4-PRO-24GB.md                 │
│                                         │
│ M1/M2/M3 Pro/Max 16GB                   │
│  → GUIDE-M1-16GB.md                     │
│                                         │
│ M1/M2/M3 8GB                            │
│  → Coming soon (use Qwen 3B for now)    │
└─────────────────────────────────────────┘
```

---

## 🚀 What's Inside Each Guide

### GUIDE-M4-PRO-24GB.md

**Sections:**
1. Quick Start
2. Model Overview (with Q32B warning)
3. Model Management Commands
4. Recommended Setup (DeepSeek V2 + Q7B + Q3B)
5. Performance Comparison
6. When to Use Which Model
7. Tips & Tricks
8. Practical Examples
9. Troubleshooting (OOM errors)
10. FAQ

**Key Recommendations:**
- ✅ **Best:** DeepSeek V2 (`/ds`) - 9-12GB RAM
- ✅ **Alternative:** Qwen 14B (`/q14b`) - 10-12GB RAM
- ✅ **Fast:** Qwen 7B (`/q7b`) - 5-7GB RAM
- ❌ **Avoid:** Qwen 32B - Crashes!

---

### GUIDE-M1-16GB.md

**Sections:**
1. Quick Start
2. Model Overview (RAM-focused)
3. Model Management Commands
4. Recommended Setup (Q7B + Q3B)
5. Performance Comparison
6. When to Use Which Model
7. **RAM Management Tips** (unique to 16GB)
8. Troubleshooting
9. FAQ

**Key Recommendations:**
- ✅ **Best:** Qwen 7B (`/q7b`) - 5-7GB RAM (safe!)
- ✅ **Quick:** Qwen 3B (`/q3b`) - 3-4GB RAM
- ⚠️ **Power:** DeepSeek V2 (`/ds`) - Close other apps first!
- ❌ **Avoid:** Anything 14B+ - Too risky

---

## 📊 Model Recommendations by RAM

### 24GB RAM (M4 Pro)
```bash
# Primary workflow
/ds          # DeepSeek V2 - BEST CHOICE
/q7b         # Qwen 7B - Fast backup
/q3b         # Qwen 3B - Quick tasks
```

### 16GB RAM (M1/M2/M3 Pro/Max)
```bash
# Primary workflow
/q7b         # Qwen 7B - MAIN MODEL
/q3b         # Qwen 3B - Quick tasks
/ds          # DeepSeek V2 - Power mode (close apps)
```

### 8GB RAM (M1/M2/M3)
```bash
# Primary workflow
/q3b         # Qwen 3B - MAIN MODEL
/q1.5b       # Qwen 1.5B - Lightweight
```

---

## 🔥 Important Lessons Learned

### ⚠️ Qwen 32B Warning

After real-world testing on M4 Pro 24GB:

**Problem:**
```
Qwen 32B requires ~17.6GB to load + 3-4GB for generation = ~21GB total
On 24GB Mac with macOS using 4-5GB = CRASH!
Error: "Insufficient Memory (kIOGPUCommandBufferCallbackErrorOutOfMemory)"
```

**Solution:**
```
Use DeepSeek V2 instead:
- Same or better code quality
- Uses ~11GB (safe!)
- Faster responses
- Works with apps open
```

**All guides updated** with this critical information!

---

## 📝 Guide Features

### What's Included:

1. **Better Structure**
   - Clearer sections
   - More actionable headings
   - Better navigation

2. **Real-World Testing**
   - Q32B crash documented
   - Actual RAM measurements
   - Tested recommendations

3. **Tier System (16GB guide)**
   - Tier 1: Safe models
   - Tier 2: Requires care
   - Tier 3: Lightweight

4. **RAM Management Section (16GB)**
   - When to close apps
   - How to check RAM
   - Model selection based on free RAM

5. **Troubleshooting**
   - Common issues
   - Step-by-step solutions
   - Alternative approaches

---

## 🎯 How to Use These Guides

### First Time Setup:

1. **Pick your guide** based on RAM
2. **Read "Quick Start"** section
3. **Follow recommended setup**
4. **Bookmark for reference**

### As Reference:

- **Model selection:** Check "When to Use Which Model"
- **Performance issues:** Check "Troubleshooting"
- **RAM management:** Check "Tips & Tricks"
- **Specific questions:** Check "FAQ"

---

## 📚 Complete Documentation Set

### Main Guides:
- ✅ [GUIDE-M4-PRO-24GB.md](GUIDE-M4-PRO-24GB.md) - M4 Pro 24GB
- ✅ [GUIDE-M1-16GB.md](GUIDE-M1-16GB.md) - 16GB Macs

### Supporting Docs:
- ✅ [README.md](README.md) - Main documentation
- ✅ [CHANGELOG-27-NOV-2025.md](CHANGELOG-27-NOV-2025.md) - v2.1 changes
- ✅ [DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md) - Faster downloads with git-lfs
- ✅ [quick-start.md](quick-start.md) - Quick start guide

---

## 🎉 Summary

**Two comprehensive guides available:**

1. **GUIDE-M4-PRO-24GB.md**
   - 10 sections
   - ~600 lines
   - Tested recommendations
   - Q32B warning included

2. **GUIDE-M1-16GB.md**
   - 9 sections
   - ~550 lines
   - RAM-focused approach
   - Safe model recommendations

**Both guides include:**
- ✅ Real-world testing results
- ✅ Step-by-step examples
- ✅ Troubleshooting sections
- ✅ Performance comparisons
- ✅ Best practices
- ✅ FAQ sections

**All documentation:**
- 🌍 Professional English
- 📊 Based on actual testing
- ✅ Up-to-date with v2.1
- 🚀 Production-ready

---

## 🚀 Next Steps

1. **Read your appropriate guide:**
   - M4 Pro 24GB → [GUIDE-M4-PRO-24GB.md](GUIDE-M4-PRO-24GB.md)
   - M1/M2/M3 16GB → [GUIDE-M1-16GB.md](GUIDE-M1-16GB.md)

2. **Follow the recommended setup**

3. **Bookmark the guide for reference**

4. **Join the community and share feedback!**

---

**Happy coding! 🎉**
