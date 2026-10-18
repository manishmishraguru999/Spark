# 01 — Research Notes: AI Kids-Content Influencer (Hindi, India)

Research date: 2026-10-18
Status legend: VERIFIED (live tool data) · REPORTED (secondary web sources, conflicting) · INFERENCE · UNKNOWN

---

## A. Demand data — VIDIQ connector (VERIFIED, live, country = IN)

Seed: "kids stories in hindi"

| Keyword | Est. monthly searches (global) | India volume | Competition (0-100) | 30-day trend | Note |
|---|---|---|---|---|---|
| hindi story | 402,827 | ~234,982 | 38.6 | +4% | Very high demand, mid competition |
| hindi stories | 282,133 | ~138,547 | 54 | +16% | Very high |
| moral stories in hindi | 278,100 | ~167,862 | 38.6 | +44% | Strongest growth among big terms |
| story in hindi | 247,950 | ~178,933 | 31.7 | -29% | Lowest competition in top group |
| kids stories | 283,138 | ~70,158 | 39.1 | -18% | Global, PK/IN mixed |
| kids story | 292,853 | ~125,151 | 37.1 | -6% | India share ~43% |
| moral stories for kids | 92,878 | ~29,024 | 45.6 | -8% | Parenting intent |
| moral story in hindi | 58,450 | ~49,221 | 40.6 | +74% | Rising, IN 84% |
| kids story in hindi | 50,127 | ~34,462 | 42 | +5% | Good exact-match target |
| hindi stories for kids | 8,918 | — | 49.5 | +42% | Long-tail, low competition |
| stories for kids in hindi | 4,596 | — | 50.5 | — | Long-tail |
| hindi kahaniya for kids | 10,710 | — | 45.5 | — | Hinglish-search opportunity |

**Key insight (INFERENCE from data):**
- Hindi moral/kids stories = huge, steady demand. Best targets: "moral story in hindi" (rising +74%), "moral stories in hindi" (+44%), "kids story in hindi".
- Competition is moderate (30–50), so a new channel can rank with Shorts + consistent series.
- Caveat: many searches come from Pakistan too (PK share 15–40% on some terms). Hindi content still works, but audience split is not 100% India.

**Not found:** Rising-keyword list and trending Shorts for "kids AI animation" returned empty (`vidiq_trending_videos` → `{"videos":[]}`). Treat AI-kids Shorts momentum as UNKNOWN; re-run later or with broader title query.

---

## B. Policy & risk — WEB (REPORTED, conflicting, verify before launch)

**YouTube (AI / inauthentic content):**
- AI use is NOT banned. Channels stay monetizable; realistic synthetic content needs disclosure. (REPORTED)
- Policy renamed "repetitious" → "inauthentic content" (Jul 2025); clarified guidance Jul 2026. (REPORTED)
- Risk groups: (1) template/near-identical videos with little originality, (2) emotionally manipulative/clickbait, (3) AI personas on sensitive topics (health, finance, legal). (REPORTED)
- Enforcement is channel-level, not per upload. (REPORTED)
- Slideshows with same voice-over and no added value = inauthentic. (REPORTED)
- Partner Program overhaul (effective 1 Feb 2027, doubled thresholds, Shorts revenue floor) — ONE secondary source, UNVERIFIED. Check YouTube's own page.

**Kids-content rules:** Search returned NOTHING specific. (UNKNOWN)
- Must check: YouTube "Made for Kids" setting (COPPA in US; India DPDP Act 2023 child-data rules). Personalized ads, comments, and data collection are restricted for kids content. Treat as mandatory checklist item, verify on official pages.

**Instagram Reels AI / kids policy:** Nothing verified. (UNKNOWN)

---

## C. Local vs Paid AI tools — tool research

### C1. Paid cloud tools (pricing = REPORTED, conflicting; check vendor page)

| Tool | Use | Reported entry price | Notes |
|---|---|---|---|
| HeyGen | Talking-avatar video | Starter ~$29/mo (15 credits) · Pro ~$89/mo (60 credits) | Source disagreement; "contact vendor" on Capterra |
| Synthesia | Avatar video | Free basic 1,200 credits/mo (~10 min std video) · Starter $14–19/mo · Creator $59–89/mo | Sources conflict on Starter price |
| Runway | Image-to-video, Gen models | Starter ~$15/mo (625 credits) · Pro ~$40/mo (2,250 credits) | Credit-based |
| Kling | Video gen | ~$7.99/mo (660 credits) · ~$25.90/mo (3,000 credits); free ~66 credits/day | Annual rates; monthly 30–50% higher |
| ElevenLabs | Hindi TTS / voice | UNKNOWN (no reliable plan data found) | Verify; Hindi voice quality is the reason to pay |

**Reality check (INFERENCE):** Credit-based pricing makes cost per minute hard to compare. Estimate per finished minute by testing 1 real Short on each tool's free tier before paying.

### C2. Local system (BEAST: RTX 3060 12GB, i9-12900K, 64GB RAM)

| Tool | Use | Feasibility on RTX 3060 12GB | Confidence |
|---|---|---|---|
| ComfyUI | Node pipeline for images/video | Yes | VERIFIED-ish (widely used) |
| Wan 2.2 **5B TI2V** | Local image/text → video | Good: 720p in ~8GB reported; community min 6GB, recommended 8GB+ | REPORTED |
| Wan 2.2 14B (GGUF Q3/Q4) | Higher quality video | Tight: Q5 needs ~11–16GB | REPORTED |
| Wan 2.2 27B MoE | Best quality | No (needs 16–24GB+) | REPORTED |
| LTX-Video 2 / 2.3 | Fast video | Only with FP8/GGUF + low res; bf16 needs ~24GB. Crashes reported on 3060 + 16GB RAM | REPORTED, conflicting |
| Local TTS (XTTS / Piper / Coqui) | Hindi voice | Feasible; Hindi quality usually below ElevenLabs | INFERENCE |
| Local face/avatar (lip-sync) | Talking character | Feasible but slower; test | UNKNOWN |

**Bottleneck note:** 12GB VRAM + 16GB system RAM = crashes. Your 64GB RAM is a real advantage — keep it.

### C3. Recommendation (INFERENCE, to test)

| Pipeline step | Recommended | Why |
|---|---|---|
| Script (Hindi) | Free LLM / Claude / local LLM | Cheap, fast |
| Hindi voice | Start local (Piper/XTTS) → pay ElevenLabs only if quality needs it | Save cost first |
| Character images | Local ComfyUI + SDXL/Flux-type model | Free, consistent style with LoRA |
| Motion clips | Wan 2.2 5B locally for short shots; paid Kling/Runway for hero shots | Hybrid saves credits |
| Avatar talking head | Paid HeyGen/Synthesia (only if face-talking format needed) | Local lip-sync is hard |
| Edit / thumbnails | DaVinci Resolve (free) + After Effects (you already know it) | Your existing skills |
| Animation for kids | Blender / Unity (your skills) for repeatable characters | Consistency, no AI drift |

---

## D. Connectors used in this research

| Connector | Used for | Status |
|---|---|---|
| WebSearch | Pricing, GPU, policy | Done — conflicting results |
| VIDIQ `vidiq_keyword_research` | Hindi kids keyword demand (IN) | Done — VERIFIED data |
| VIDIQ `vidiq_trending_videos` | Shorts trend for AI kids | Empty result |
| Nextlev (YouTube analytics) | Could check faceless/AI kids channels & RPM | Available, NOT run yet (next step) |
| Ahrefs / Semrush / Ubersuggest | Website SEO — not needed for Shorts/Reels | Skipped |

---

## E. Open questions for you (UNKNOWN — needs your input)
1. Final persona/character name and voice (boy/girl, age group 3–8 or 6–12?).
2. Language: pure Hindi, Hinglish, or Hindi + English?
3. Target platform first: YouTube Shorts, Reels, or long-form stories?
4. Budget per month for paid tools (₹ or $)?
5. Is this channel "Made for Kids" (strict rules: no comments, no personalized ads)?
