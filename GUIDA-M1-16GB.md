# 🍎 Guida Rapida: MLX-CODE su M1 MacBook Pro 16GB

**Creato:** 26 Novembre 2024
**Per:** M1/M2/M3 MacBook Pro con 16GB RAM

---

## 🎯 Raccomandazione Finale

### Per te (M1 16GB) il modello MIGLIORE è:

**DeepSeek-Coder-V2-Lite**
- ⭐⭐⭐⭐⭐ Qualità eccellente per codice
- ~9GB RAM (devi chiudere Chrome/Slack)
- Molto meglio di Qwen 7B per coding
- Vale la pena chiudere altre app

---

## 📥 Come Scaricare DeepSeek

### Metodo 1: Automatico (dentro MLX-CODE)
```bash
# Lancia MLX-CODE
~/mlx-code

# Dentro MLX-CODE digita:
/deepseek
```
Aspetta 10-30 minuti per il download.

### Metodo 2: Manuale (più veloce e affidabile)
```bash
# Installa git-lfs se non l'hai
brew install git-lfs
git lfs install

# Scarica il modello
cd /tmp
git clone https://huggingface.co/mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit

# Sposta nella cache
mkdir -p ~/.cache/huggingface/hub
mv /tmp/DeepSeek-Coder-V2-Lite-Instruct-4bit \
   ~/.cache/huggingface/hub/models--mlx-community--DeepSeek-Coder-V2-Lite-Instruct-4bit

# Verifica
ls -lh ~/.cache/huggingface/hub/
```

---

## 🗑️ Eliminare Qwen 1.5B e 3B

Libera ~3GB di spazio:

```bash
# Vedi quanto occupano i modelli attuali
du -sh ~/.cache/huggingface/hub/models--mlx-community--*/

# Elimina Qwen 1.5B
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-Coder-1.5B-Instruct-4bit/

# Elimina Qwen 3B
rm -rf ~/.cache/huggingface/hub/models--mlx-community--qwen2.5-coder-3b-instruct-4bit/

# Controlla che siano spariti
ls -lh ~/.cache/huggingface/hub/
```

**Nota:** Puoi sempre scaricarli di nuovo con `/q1.5b` o `/q3b`

---

## 🚀 Tutti i Modelli Disponibili

Ora hai questi comandi in MLX-CODE:

| Comando | Modello | RAM | Qualità | Velocità |
|---------|---------|-----|---------|----------|
| `/q1.5b` | Qwen 1.5B | ~2GB | ⭐⭐ | ⚡⚡⚡ |
| `/q3b` | Qwen 3B | ~3GB | ⭐⭐⭐ | ⚡⚡ |
| `/q7b` | Qwen 7B | ~5GB | ⭐⭐⭐⭐ | ⚡⚡ |
| `/q14b` | Qwen 14B | ~9GB | ⭐⭐⭐⭐ | ⚡ |
| **`/deepseek`** | **DeepSeek-V2-Lite** | **~9GB** | **⭐⭐⭐⭐⭐** | **⚡** |
| `/ds` | DeepSeek (alias) | ~9GB | ⭐⭐⭐⭐⭐ | ⚡ |
| `/mistral` | Mistral 7B | ~4GB | ⭐⭐⭐⭐ | ⚡⚡ |

---

## ⚡ Setup Ottimale per M1 16GB

### Prima di usare DeepSeek/14B:

1. **Chiudi Chrome** → libera 2-4GB
2. **Chiudi Slack/Discord** → libera 500MB-1GB
3. **Chiudi VSCode** se non lo usi → libera 300-500MB
4. **Controlla RAM libera** con Activity Monitor

### Durante l'uso:

```bash
# Monitora uso RAM (in altro terminale)
watch -n 2 'ps aux | grep mlx | head -1'

# Se vedi swap/memoria gialla in Activity Monitor → chiudi qualcosa
```

---

## 🎓 Quando Usare Quale Modello

### **DeepSeek** (`/deepseek`) → Coding serio
- ✅ Scrivere codice complesso
- ✅ Refactoring
- ✅ Bug fixing
- ✅ Spiegazioni di algoritmi

### **Qwen 7B** (`/q7b`) → Uso quotidiano
- ✅ Coding semplice
- ✅ Quick fixes
- ✅ Quando hai browser aperto
- ✅ Multitasking

### **Qwen 14B** (`/q14b`) → Raramente
- ⚠️ Solo se DeepSeek non basta
- ⚠️ Chiudi TUTTO il resto
- ⚠️ Non per uso quotidiano

---

## 🐛 Problemi Comuni

### "Out of memory" / Mac lentissimo
```bash
# Switcha a modello più piccolo
/q7b

# O chiudi altre app
```

### "Model not found" dopo download manuale
```bash
# Controlla che la directory sia corretta
ls ~/.cache/huggingface/hub/models--mlx-community--DeepSeek-Coder-V2-Lite-Instruct-4bit/

# Deve contenere: config.json, *.safetensors, tokenizer.json
```

### Download troppo lento
```bash
# Usa git-lfs invece del download automatico
# Vedi "Metodo 2: Manuale" sopra
```

---

## 📊 Confronto con Claude Code (quello che usiamo ora)

| Aspetto | MLX-CODE + DeepSeek | Claude Code |
|---------|---------------------|-------------|
| **Costo** | ✅ Gratis | ❌ A pagamento |
| **Internet** | ✅ Offline | ❌ Serve sempre |
| **Qualità** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Velocità** | ⚡ Media | ⚡⚡ Veloce |
| **RAM** | ❌ 9GB | ✅ Minima |
| **Privacy** | ✅ Locale | ⚠️ Cloud |

**Conclusione:**
- **Claude Code** per lavoro importante/pagato
- **MLX-CODE + DeepSeek** per progetti personali/studio

---

## 📚 Documentazione Completa

- [DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md) - Tutti i metodi di download
- [README.md](README.md) - Guida completa MLX-CODE
- [quick-start.md](quick-start.md) - Quick start

---

**Buon coding! 🚀**
