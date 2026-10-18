# 05 — Full Plan: AI Influencer (Any Gender) · Local PC · Low Cost · With Proof

Date: 2026-10-18
Goal stated: 1 lakh subscribers in 1 month
Budget: ₹5,000 / month · Hardware: RTX 3060 12GB, 64GB RAM
Legend: VERIFIED (live tool) · REPORTED (web, conflicting) · INFERENCE · UNKNOWN

---

## 0. Reality check — 1 lakh subscribers in 1 month

**Plan cannot guarantee this.** Honest numbers:

| Proof point | Source | Status |
|---|---|---|
| Only ~1.3% of ~61 million YouTube channels have 1 lakh+ subscribers | vidIQ 2026 benchmark | REPORTED |
| Median monthly growth for channels at 1L–10L subs is 0.30% | vidIQ 2026 benchmark | REPORTED |
| Channels at 10K–1L gained a median ~0.97% subs per month | TubeAI Sep 2026 study | REPORTED |
| No dataset found for "new channel reaching 1L in first month" | Searched, not found | UNKNOWN |
| Jan 2026: YouTube terminated 16 mass-produced/AI channels (35M subs combined) | Press reports | REPORTED |

**Conclusion (INFERENCE):** 1 lakh in 30 days needs a viral breakout, which is random. A plan can raise the odds of a breakout. It cannot promise one. Realistic 30-day target for a well-run AI Shorts channel: **1,000–5,000 subscribers** (INFERENCE, not guaranteed).

**Do not buy subscribers or use bot/view services.** That breaks YouTube policy and can terminate the channel.

**Do not borrow money (loan / credit) for this.** Keep spend within ₹5,000 until real data shows which format works.

---

## 1. What works for fast reach (and what gets banned)

| Approach | Risk | Verdict |
|---|---|---|
| Faceless, template, mass-produced AI videos | High. Mass-produced content is the enforcement target (REPORTED) | **Avoid** |
| One AI persona (any gender) with original script, opinions, reactions, daily-life or commentary | Low. AI as tool + original commentary stays eligible (REPORTED) | **Recommended** |
| Trending-topic reaction and commentary Shorts (short, hook-first) | Low–medium (use your own script and opinions) | **Recommended** |
| Buying subs, bots, view farms | Very high | **Never** |

**Recommended format:** One consistent AI character (human-like or stylized, your choice) speaking to camera in short 15–40s Shorts. Hook in first 2 seconds, one clear opinion or story per video, strong ending CTA. Language: Hinglish first (widest reach in India), add English and other languages later.

**Persona choice (you decide):** Boy or girl character both work. Test 2 characters for 2 weeks each, keep the one with better retention. Do not decide on gender alone (INFERENCE).

---

## 2. Local PC pipeline — what really runs on RTX 3060 12GB

| Step | Tool | Local? | Speed on your PC | Notes |
|---|---|---|---|---|
| Script (Hinglish) | Any free LLM or local LLM | Yes | Fast | Write your own opinions |
| Voice (TTS) | Piper / XTTS (free) · ElevenLabs Starter (paid) | Yes / cloud | Fast | Start free; pay only if quality is not enough |
| Character image | ComfyUI + SDXL-type model + LoRA | Yes | Seconds to a minute per image | Keep one face for consistency |
| Talking/motion video | Wan 2.2 5B (ComfyUI, TI2V) | Yes | ~several minutes per 5s clip at 480p; 10–15 min at higher res (REPORTED) | Fits 12GB with offloading (REPORTED) |
| Hero shots (higher quality) | Kling / Veo / Pika (cloud, paid) | No | Minutes, no local load | Use only for best shots |
| Edit + subtitles | DaVinci Resolve (free) | Yes | Fast | Devanagari subtitles supported via text tracks |

**Easy-run setup:** ComfyUI Portable (Windows) + Wan 2.2 5B model + Piper voice. One-click style, no coding needed.

**Limits (honest):**
- Local video is slow. Plan for ~1 finished 5s clip per 10–15 min. A 30s Short needs ~6 clips → plan 2–3 hours per Short with local only.
- Run one heavy job at a time. Close browser tabs first (12GB VRAM).
- LTX-Video on 12GB + 16GB RAM crashes (REPORTED). Your 64GB RAM avoids that.

**Speed fix:** Make Shorts mostly from **still character images + voice + subtitles + motion effects** (fast, local), and use Wan video only for 1–2 key shots per Short. This keeps output at 1 Short per day.

---

## 3. Cloud video tools — low-cost options (USD list prices, REPORTED, conflicting)

Conversion used: ~₹84 per USD (REPORTED from one source; verify today's rate).

| Tool | Entry plan (USD/mo) | Approx ₹/mo | Notes | Verify |
|---|---|---|---|---|
| Kling | ~$6.99 first period, ~$8.80 renewal | ~₹590–740 | Lowest entry headline; 10s clip cap per one source | Check INR at checkout |
| Pika | ~$10 (700 credits) | ~₹840 | Watermark-free on paid | Check India pricing |
| Hailuo | ~$9.99–20 | ~₹840–1,680 | Commercial licence limited (REPORTED) | Check terms |
| Veo (Google) | ~$4.99/mo (one source); API ~$0.05/sec (Veo 3.1 Lite) | ~₹420 | Pay-per-second option is cheapest for short clips | Check Google AI plan |
| Vidu | UNKNOWN | — | No pricing found | Check |
| Pay-per-use API (fal.ai, Replicate) | UNKNOWN | — | Often cheapest for low volume | Check |

**Cheapest plan for ₹5,000 budget (INFERENCE):**
- 1 cloud tool: Kling (~₹740) or Veo pay-per-second (~₹400–800 depending on use)
- ElevenLabs Starter (~₹420, REPORTED)
- Remaining ~₹3,800 kept as buffer. Do not spend it all in week 1.

---

## 4. Budget allocation — ₹5,000 / month

| Item | ₹ / month | Priority |
|---|---|---|
| ElevenLabs Starter (Hindi/English voice) | 420 | 1 |
| Kling Standard or Veo pay-per-use (hero shots) | 740 | 2 |
| Buffer / test credits | 3,840 | Keep unspent until week 2 |
| **Total planned** | **~1,160 (+ buffer)** | Under ₹5,000 |

Free items (₹0): ComfyUI, Wan 2.2 5B, Piper, DaVinci Resolve, free LLM for scripts.

---

## 5. Growth system (what to actually do)

| Element | Rule |
|---|---|
| Upload frequency | 1 Short per day for 30 days (≈30 Shorts). Consistency matters more than length |
| Hook | First 2 seconds: question, bold claim, or visual surprise |
| Length | 15–40 seconds. Retention drives reach |
| Title (≤60 chars) | Number + power word + emotion. Example: "3 AI tools jo 2026 mein sab badal denge" |
| Thumbnail | Character face big, bold color, curiosity gap (no fear, no clickbait lies) |
| Description | Primary keyword in first 100 characters, max 3 hashtags |
| Series | Same character, same format, weekly "Top 3" or "Reaction" series |
| Trend use | Commentary on trending topics within 24h, in your own words |
| Disclosure | Label realistic AI content as altered or synthetic (REPORTED policy) |

**Test plan:** Days 1–14 test 2 characters and 3 formats. Days 15–30 double down on the format with best retention and Shorts views.

---

## 6. 30-day plan

| Week | Goal | Output | Check |
|---|---|---|---|
| 1 | Setup + persona test | Channel created, 2 characters, 14 Shorts planned | ComfyUI runs one image and one Wan clip |
| 2 | Production rhythm | 7 Shorts uploaded, retention checked | Avg view duration per Short |
| 3 | Double down | 7 Shorts in winning format, 1 cloud hero shot per week | CTR, views per Short |
| 4 | Scale what works | 7 Shorts, pick top 3 formats for month 2 | Subscriber trend |

**KPI targets (INFERENCE, not guaranteed):**

| Metric | Day 30 target |
|---|---|
| Shorts published | 30 |
| Subscribers | 1,000–5,000 (stretch: 10,000 if a Short breaks out) |
| Avg view duration | 60%+ of Short length |
| Monthly spend | ≤ ₹2,000 |

---

## 7. Risks

| Risk | Level | Mitigation |
|---|---|---|
| Channel flagged as mass-produced | High if faceless/template | Original scripts, real persona, own commentary |
| Subscriber goal missed | High (statistically rare) | Judge by views and retention, not only subs |
| Voice or likeness misuse | Medium | Use own or licensed voices only |
| Local GPU overheating or crash | Medium | One heavy job at a time; close apps |
| Cloud price changes | Medium | Verify INR price at checkout |

---

## 8. Next actions (this week)

1. Choose two character options (boy/girl/stylized) to test.
2. Install ComfyUI Portable + Wan 2.2 5B + Piper (free).
3. Open an ElevenLabs Starter account and check INR price.
4. Write 14 scripts (Hinglish, original opinions).
5. Publish first 3 Shorts and track retention for 3 days.

---

## Sources (from research)
- vidIQ YouTube Subscriber Benchmarks 2026: https://vidiq.com/research/youtube-subscriber-benchmarks-2026/
- TubeAI channel growth study (Sep 2026), via search results (no direct URL captured)
- AI video generator pricing (REPORTED, multiple blogs): costbench.com, rangy.ai, frameo.ai (see search results)
- YouTube faceless / mass-produced enforcement (press reports): air.io, letsdatascience.com
- ComfyUI Wan 2.2 on RTX 3060 timing (REPORTED): nextdiffusion.ai, civarchive.com
