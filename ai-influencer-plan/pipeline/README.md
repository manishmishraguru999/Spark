# BEAST Pipeline: Phone से Control, PC पर Production

Telegram से script भेजो → BEAST PC पर voice, images, clips, lip-sync और captions बनते हैं → 480p preview phone पर आता है → ✅ Approve → तय समय पर Instagram + Facebook पर post होता है, और YouTube file phone पर upload के लिए तैयार मिलती है।

**Status:** Code इस repo में test हो चुका है (18 automated tests, Linux पर)। आपके Windows PC पर अभी नहीं चलाया गया है। पहला run नीचे के Step 5 (demo) से करें।

---

## कैसे काम करता है

```
Phone (ChatGPT app → Telegram bot)
        │  /new + script
        ▼
BEAST PC: run_pipeline.py
  tts → images (ComfyUI) → clips (Wan, optional) → lipsync (optional) → assemble (FFmpeg) → preview
        │  480p preview + buttons
        ▼
Phone: ✅ Approve / 🔁 नई images / 🎙️ नई voice / ❌ Cancel
        │  approve
        ▼
Scheduled slot (19:00 IST) → Instagram + Facebook (API) · YouTube (manual folder, audit के बाद API)
```

- **Security:** Bot सिर्फ़ PC से बाहर की तरफ़ connect करता है, इसलिए कोई port नहीं खुलता। सिर्फ़ `allowed_chat_ids` वाले chat के messages माने जाते हैं।
- **Crash-safe:** हर job का हर stage SQLite में save होता है। PC restart होने पर काम वहीं से आगे चलता है।

---

## Setup (Windows, BEAST)

### Step 1: ज़रूरी software
1. **Python 3.11+** (python.org से; install करते समय "Add to PATH" ✔)
2. **FFmpeg:** `winget install Gyan.FFmpeg`, फिर नया terminal खोलकर `ffmpeg -version` से check करें
3. **ComfyUI** (आपके पास पहले से है) — इसे `127.0.0.1:8188` पर ही चलाएँ

### Step 2: Folder
इस `pipeline` folder को `X:\AI_INFLUENCER\pipeline\` में copy करें।

### Step 3: Python environment
```bat
cd /d X:\AI_INFLUENCER\pipeline
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### Step 4: Config
```bat
copy config.example.yaml config.yaml
```
`config.yaml` में `paths.root` = `X:/AI_INFLUENCER` रखें। पहली बार के लिए `tts.provider: silent` कर दें (test tone, कोई API नहीं लगेगा)।

### Step 5: Demo run (Telegram के बिना)
```bat
venv\Scripts\python run_pipeline.py --config config.yaml --demo
```
`Demo OK` दिखना चाहिए। `X:\AI_INFLUENCER\03_renders\` में video खोलकर देखें कि Hindi captions सही दिख रहे हैं।

### Step 6: Telegram bot (5 मिनट)
1. Telegram में **@BotFather** → `/newbot` → नाम दें → **token** copy करें।
2. Windows में token को environment variable बनाएँ:
   ```bat
   setx TELEGRAM_BOT_TOKEN "123456:ABC..."
   ```
3. अपना chat ID जानें: bot को कोई भी message भेजें, फिर browser में `https://api.telegram.org/bot<TOKEN>/getUpdates` खोलें और `"chat":{"id": ...}` वाला number देखें।
4. `config.yaml` में `allowed_chat_ids: [आपका_ID]` लिखें।
5. नया terminal खोलें और यह चलाएँ:
   ```bat
   venv\Scripts\python run_pipeline.py --config config.yaml
   ```
   Phone पर "🟢 BEAST pipeline चालू है" message आना चाहिए।

### Step 7: Voice (Sarvam)
1. sarvam.ai पर account बनाएँ (₹1,000 free credits, official pricing page) और API key लें।
2. `setx SARVAM_API_KEY "..."` चलाएँ, फिर `config.yaml` में `tts.provider: sarvam` करें।
3. Sarvam docs से `speaker` का नाम चुनें। **Language वाले field का नाम (`target_language_code`) भी docs से confirm करें।**
- **Local voice चाहिए तो:** Indic Parler-TTS का एक छोटा script बनाएँ जो `--text-file` और `--out` ले, फिर `tts.provider: command` करें।

### Step 8: ComfyUI images
1. ComfyUI में अपना realistic workflow बनाएँ (character LoRA के साथ)।
2. **Settings → Enable Dev mode → "Export (API)"** से workflow export करें।
3. JSON में prompt की जगह `"{{PROMPT}}"`, negative की जगह `"{{NEGATIVE}}"`, seed की जगह `"{{SEED}}"`, और SaveImage prefix की जगह `"{{PREFIX}}"` लिखें। Example: `workflows/scene_image_api.example.json`।
4. `config.yaml` में `comfyui.enabled: true` और `image_workflow` का path दें।
5. **Motion clips (Wan 2.2):** image-to-video workflow में input image की जगह `"{{IMAGE}}"` लिखें, फिर `clips_enabled: true` करें।

### Step 9: Lip-sync (MuseTalk / LatentSync 1.5)
दोनों tools अपने अलग venv में install करें। एक छोटा wrapper script बनाएँ जो `--face --audio --out` ले। फिर `lipsync.enabled: true` करें। Character की face image `character.face_image` में दें (**पूरी तरह synthetic चेहरा**)।

### Step 10: Publishing
- **पहला हफ़्ता `publish.dry_run: true` रखें।** Pipeline सब कुछ करेगा, लेकिन post नहीं करेगा।
- **YouTube (`mode: manual`):** `05_published/youtube_upload` folder को Google Drive या OneDrive से phone पर sync करें। हर video के साथ एक `.txt` file में title और description होगा। YouTube app से upload करें और **"Altered or synthetic content = Yes"** चुनें।
  - Google का नियम: बिना audit वाले API project से uploads private पर lock रहते हैं। Audit पास होने के बाद `mode: api` करें; तब `containsSyntheticMedia=true` अपने-आप set होगा।
- **Instagram:** Professional account बनाएँ। developers.facebook.com पर App बनाएँ → Instagram API (Instagram Login) → अपने account को **Instagram Tester** बनाएँ → access token लें → `setx IG_ACCESS_TOKEN "..."` चलाएँ और `ig_user_id` दें। Token हर ~50 दिन पर अपने-आप refresh होगा।
- **Facebook Page:** उसी App से Page access token लें (permissions: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`), फिर `setx FB_PAGE_TOKEN "..."` चलाएँ और `page_id` दें।
- **Profile पर एक बार manually:** Instagram पर "AI-generated profile" label, और Bio में "AI-generated character" लिखें।

### Step 11: Auto-start
- **Task Scheduler** → Create Task → Trigger: "At log on" → Action: `X:\AI_INFLUENCER\pipeline\start_pipeline.bat`
- ComfyUI के लिए भी ऐसा ही एक task बनाएँ।
- `start_pipeline.bat` crash होने पर 30 सेकंड में pipeline अपने-आप फिर शुरू कर देता है।

---

## Phone से रोज़ का इस्तेमाल

| काम | कैसे |
|---|---|
| नया Reel | ChatGPT (template: `CHATGPT_SCRIPT_TEMPLATE.md`) → output copy → bot को भेजें |
| Review | Bot पर preview आएगा → ✅ / 🔁 / 🎙️ / ❌ |
| Status | `/status` |
| रद्द करना | `/cancel <job_id>` |
| YouTube | Sync folder से YouTube app में upload |

---

## Tests (developers के लिए)
```bat
venv\Scripts\pip install pytest
venv\Scripts\python -m pytest -q tests
```

## Folder map
```
X:\AI_INFLUENCER\
 00_inbox  01_assets  02_jobs  03_renders  04_previews  05_published  06_logs (pipeline.log, jobs.sqlite)  07_secrets
```

## अभी क्या नहीं है (अगले versions)
- रोज़ सुबह views/retention report (YouTube Analytics और Instagram Insights API)
- Whisper से word-level caption timing (अभी timing text की लंबाई के हिसाब से है)
- Comments के reply drafts
