# 03 — Update: Audience 16–30 · All Languages · Budget ₹5,000/month

Date: 2026-10-18
Supersedes: kids-audience assumptions in 01_RESEARCH.md and 02_REFINED_MASTER_PROMPT.md

Legend: VERIFIED (live tool) · REPORTED (web, conflicting) · INFERENCE · UNKNOWN

---

## 1. Changes from previous plan

| Item | Old (kids 4–10) | New (confirmed) |
|---|---|---|
| Audience | Kids + parents | 16–30 year olds |
| Language | Hindi | All languages (Hindi-first, English, Hinglish, subtitles in more) |
| Budget | Not set | ₹5,000 / month |
| Made for Kids | Assumed yes | **No** (INFERENCE: audience is adult. Still self-declare correctly on upload) |
| Kids rules (COPPA / DPDP child data) | Mandatory | Not needed for this audience |
| Still mandatory | — | AI disclosure, voice/likeness rights, copyright music, inauthentic-content rules |

---

## 2. Demand data — VIDIQ (VERIFIED, country = IN, 2026-10-18)

| Keyword | Est. monthly searches | India volume | Competition | 30-day trend |
|---|---|---|---|---|
| ai tools | 696,005 | 225,309 | 66 | -11% |
| best ai tools | 118,593 | 39,531 | 62 | -15% |
| free ai video generator | — | 429,437 | — | (country volume only) |
| ai video generator | — | 137,944 | — | (country volume only) |
| best ai video generator | — | 116,195 | — | (country volume only) |
| google flow ai video generator | — | 84,171 | — | (country volume only) |
| grok ai video generator | — | 35,337 | — | (country volume only) |
| ai tools for students | 55,598 | 18,533 | 51.5 | **-51%** |
| best ai tools for students | 45,739 | 19,602 | 61 | -14% |
| ai tools for students for exam | 5,022 | — | 39.5 | -47% |
| ai tools for students in hindi | 3,948 | — | 44 | (Hindi variant is small) |

**Insights (INFERENCE from data):**
1. **"Free AI video generator" is the biggest intent in India** (~4.3 lakh/month in-country). Creators and students want free AI video tools. This is a strong niche for tutorial and comparison content.
2. **Student-focused "AI tools" searches fell about 50%** in the last 30 days. Do not build the whole channel on student keywords alone.
3. **Hindi-specific AI keywords are small** (~4K). Broad English keywords have far more demand, so a Hinglish or English-first channel with Hindi captions gets more reach than Hindi-only.
4. Competition for "ai tools" is high (66). A small channel should target specific angles ("free AI video generator without watermark", "Google Flow vs Kling") rather than generic "AI tools".

**Trending check:** `vidiq_trending_videos` for "kids AI animation" returned nothing earlier. Not re-run for 16–30 yet. Run it once the niche is locked.

---

## 3. Budget plan — ₹5,000 / month

Exchange rate used for conversion: about ₹84 per USD (REPORTED from one source; verify on the day you pay).

| Tool | Role | Price (REPORTED) | Approx ₹/month | Decision |
|---|---|---|---|---|
| ElevenLabs Starter | Hindi + English voice (AI voice) | ~₹420 (Starter, one source) | ~₹420 | **Buy first.** Check INR checkout and UPI. |
| ElevenLabs Creator | More minutes, voice cloning | ~₹1,850 (one source) | ~₹1,850 | Only if Starter runs out of credits |
| Kling Standard | Hero video shots | ~$8.80 renewal (~₹740) | ~₹740 | Buy when local Wan 2.2 quality is not enough |
| CapCut Pro | Editing, captions | ~$9.99 (~₹840), region dependent | ~₹840 | Optional. DaVinci Resolve (free) can replace it |
| Canva Pro | Thumbnails | UNKNOWN (no data found) | — | Use free Canva or local design tools first |
| ComfyUI + Wan 2.2 5B | Local video | ₹0 (your GPU) | ₹0 | Core of the pipeline |
| Piper / XTTS | Local voice (backup) | ₹0 | ₹0 | Test as free fallback |
| DaVinci Resolve | Edit | ₹0 (free) | ₹0 | Core |

### Suggested allocation (fits ₹5,000)

| Bucket | Amount | What it covers |
|---|---|---|
| ElevenLabs Starter | ₹420 | Voice |
| Kling Standard | ₹740 | ~2–3 hero shots per week |
| CapCut Pro (optional) | ₹840 | Captions and quick edits |
| Reserve / buffer | ~₹3,000 | Price changes, extra credits, one-off tools |
| **Total planned** | **~₹2,000** | Within ₹5,000 with buffer |

**Rule:** If the ElevenLabs Creator plan (₹1,850) is needed, drop CapCut. Total stays under ₹3,000.

**Warning (INFERENCE):** Kling and Runway credits run out fast. Test each shot with the free local Wan 2.2 5B first, and send only final hero shots to paid tools.

---

## 4. Recommended working niche (ASSUMPTION, confirm)

Since you did not name the niche, I am proposing a working option, based on the data above:

**"AI video tools for creators in Hinglish"**: free and affordable AI video tutorials, comparisons and workflows, with an AI-character host.

| Why | Evidence |
|---|---|
| Biggest demand in India | "free ai video generator" ~4.3 lakh/month in IN (VERIFIED) |
| Fits 16–30 creators and students | Young audience uses free tools (INFERENCE) |
| Your skills match | VFX, Nuke, After Effects, ComfyUI (from your profile) |
| Can be made with ₹5k budget | Local ComfyUI + ElevenLabs Starter + Kling for hero shots |

**Other options (if you prefer):**
- Motivation or study tips for students (demand falling, −51%): **not recommended**
- Storytelling / kids-style content: **no longer fits** 16–30 audience
- VFX / Blender / Unreal tutorials for 16–30 hobbyists: good fit with your skills, demand UNKNOWN (not researched yet)

---

## 5. Policy notes for 16–30 audience

- **AI disclosure:** Label realistic synthetic content. Required by YouTube (REPORTED).
- **Inauthentic content:** Avoid template-based, near-identical Shorts. Add original commentary (REPORTED).
- **Voice cloning:** Use only your own voice or licensed voices. Do not clone real people (INFERENCE, check each tool's terms).
- **Music:** Use royalty-free or licensed tracks only.
- **Made for Kids:** Answer "No" for this audience (INFERENCE). Confirm during upload.

---

## 6. Open items (UNKNOWN, need you)

1. Confirm the niche (Section 4) or name another.
2. Character: name, look (human-like or stylized), voice gender.
3. Platform priority: YouTube Shorts, Instagram Reels, or long-form.
4. Language mix: Hindi-first, Hinglish, or English-first with Hindi captions.
5. Check ElevenLabs Starter price at checkout (INR) before buying.
