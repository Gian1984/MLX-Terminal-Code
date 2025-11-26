# 📝 Changelog - 26 Novembre 2024

## 🎯 Modifiche Principali

### 1. ✅ Modello Default Cambiato: 3B → 1.5B

**Motivo:**
- Download più veloce (~1GB vs ~2GB)
- Funziona su tutti i Mac (anche 8GB RAM)
- Chiaramente indicato come "demo model" nella documentazione

**File modificati:**
- `mlx-code-v2.py` (linea 44)
- `~/mlx-code` (aggiornato con v2)

### 2. ✅ Aggiunti Nuovi Modelli

**Modelli disponibili ora:**
- `/q1.5b` - Qwen 1.5B (default demo)
- `/q3b` - Qwen 3B
- `/q7b` - Qwen 7B
- `/q14b` - **NUOVO** Qwen 14B
- `/deepseek` o `/ds` - **NUOVO** DeepSeek-Coder-V2-Lite
- `/deepseek-1.3b` - **NUOVO** DeepSeek 1.3B
- `/mistral` o `/m7b` - Mistral 7B

**File modificato:**
- `mlx-code-v2.py` (linee 46-56)

### 3. ✅ Documentazione Completamente Aggiornata

**README.md:**
- ⚠️ Warning chiaro: 1.5B è solo demo
- Tabella completa con DeepSeek e 14B
- Guida upgrade rapida
- Raccomandazioni per RAM (8GB vs 16GB)

**quick-start.md:**
- Tabella aggiornata con nuovi modelli
- Warning su 1.5B
- Quick upgrade guide

**DOWNLOAD-MODELS.md:**
- Nota in alto su 1.5B demo
- Istruzioni DeepSeek
- Istruzioni Qwen 14B
- Sezione dedicata M1 16GB RAM
- Come eliminare modelli vecchi

**GUIDA-M1-16GB.md:** ✨ NUOVO FILE
- Guida completa per M1/M2/M3 con 16GB
- Raccomandazione: DeepSeek migliore
- Come eliminare 1.5B e 3B
- Tabella confronto modelli
- Troubleshooting

---

## 📊 Situazione Attuale Modelli

### Modelli Installati (dall'output utente):
- ✅ Qwen 7B (~4GB) - già presente
- ✅ Qwen 3B (~1.7GB) - riscaricato automaticamente
- ✅ DeepSeek-V2-Lite (~10GB) - nella cache, pronto all'uso
- ⚠️ Qwen 1.5B - probabilmente presente o si scaricherà al primo avvio

### Da Eliminare (opzionale):
```bash
# Elimina 3B se non serve (libera 1.7GB)
rm -rf ~/.cache/huggingface/hub/models--mlx-community--qwen2.5-coder-3b-instruct-4bit/

# Elimina 1.5B se non serve (libera 1GB)
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-Coder-1.5B-Instruct-4bit/
```

---

## 🚀 Come Usare Ora

### 1. Avvia MLX-CODE:
```bash
~/mlx-code
```

### 2. Cambia modello subito:
```bash
# Migliore per coding:
> /deepseek

# Oppure safe choice:
> /q7b
```

### 3. DeepSeek dovrebbe caricarsi SENZA download (già presente)

---

## 🎓 Raccomandazioni Finali

### Per M1 16GB (la tua config):

**Setup Ottimale:**
1. **Elimina** 1.5B e 3B (risparmi ~3GB)
2. **Tieni** Qwen 7B (backup veloce)
3. **Usa** DeepSeek come principale

**Comandi da usare:**
- Coding serio → `/deepseek` (chiudi Chrome)
- Quick tasks → `/q7b` (multitasking ok)
- **NON** usare `/q1.5b` o `/q3b` (scarsi)

---

## 🐛 Fix Problemi Noti

### ✅ RISOLTO: `/deepseek` non funzionava
**Causa:** Stava usando vecchia versione di mlx-code
**Fix:** `~/mlx-code` ora usa `mlx-code-v2.py` aggiornato

### ✅ RISOLTO: 3B si riscaricava sempre
**Causa:** DEFAULT_MODEL era 3B
**Fix:** Cambiato a 1.5B

### ✅ RISOLTO: Documentazione confusa su modelli
**Causa:** Non chiaro quale usare
**Fix:** Tutte le doc aggiornate con warning e raccomandazioni

---

## 📁 File Modificati/Creati

### Modificati:
- ✏️ `mlx-code-v2.py` (DEFAULT_MODEL + nuovi aliases)
- ✏️ `~/mlx-code` (sostituito con v2)
- ✏️ `README.md` (sezione modelli completamente rifatta)
- ✏️ `quick-start.md` (tabella modelli aggiornata)
- ✏️ `DOWNLOAD-MODELS.md` (DeepSeek + 14B + M1 guide)

### Creati:
- ✨ `GUIDA-M1-16GB.md` (guida italiana completa)
- ✨ `CHANGELOG-26-NOV-2024.md` (questo file)

---

## 🎯 Prossimi Passi Suggeriti

1. **Testa `/deepseek`** nel tuo MLX-CODE aggiornato
2. **Elimina 1.5B e 3B** se non servono (comando sopra)
3. **Imposta DeepSeek come default** se ti piace (edit linea 44 in ~/mlx-code)
4. **Chiudi browser** quando usi DeepSeek (per avere RAM libera)

---

**Tutto fatto! 🎉**

Per domande o problemi, vedi:
- [README.md](README.md) - Guida completa
- [GUIDA-M1-16GB.md](GUIDA-M1-16GB.md) - Guida specifica per te
- [DOWNLOAD-MODELS.md](DOWNLOAD-MODELS.md) - Dettagli modelli
