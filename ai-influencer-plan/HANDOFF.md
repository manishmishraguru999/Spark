# Continuation Handoff — AI Influencer Channel

- **Proposed Project OS ID:** `AIINF-001` (अभी PROJECT_REGISTRY.md में register नहीं है; आपके BEAST पर `X:\MANISH_AI_PROJECT_OS\_SYSTEM\PROJECT_REGISTRY.md` में जोड़ें)
- **Last updated:** 2026-10-21
- **Repo:** `manishmishraguru999/Spark`, branch `ccr-f5672010-m0n1ok`, folder `ai-influencer-plan/`

## Verified state

| Item | Status |
|---|---|
| Niche research (files 01–08) | Done, research only |
| Deep-research prompts (4 AI, platform-neutral) | Done (`research-prompts/`, copy page artifact) |
| Local बनाम paid research report + cost model | Done (`claude_research_report.md`, `cost_model.py`) |
| Pipeline architecture | Done (`10_AUTOMATED_PIPELINE_PHONE_CONTROL.md`) |
| Pipeline code | Done (`pipeline/`); 18 tests pass on Linux; **BEAST/Windows पर अभी नहीं चला** |
| Benchmark (voice / lip-sync / face) | Planned, not run |
| Persona | Realistic, fully synthetic human host; gender undecided; "what-if / अनोखे facts" (provisional) |
| Accounts / API keys | Not created |

## Locked decisions (user)
- Audience 16–30, India first, Hinglish; kids content out of scope
- Same master video on YouTube Shorts + Instagram Reels + Facebook Reels (≤ 90s)
- Budget ₹5,000/month, no loans; ChatGPT paid plan already exists
- BEAST PC always on; all rendering and files stay on PC; phone for control and review
- User time: weekdays 2–3 h, weekends 5–6 h+

## Next actions (in order)
1. BEAST पर `pipeline/README.md` के Step 1–5 (demo run)
2. Telegram bot (Step 6), `dry_run: true` के साथ
3. Benchmark: 2 synthetic faces × MuseTalk / LatentSync 1.5 / HeyGen free; Sarvam बनाम Indic Parler-TTS
4. Persona lock → character LoRA → ComfyUI workflows export (Step 8)
5. YouTube API audit apply; Instagram/Facebook app setup; एक हफ़्ता dry-run, फिर live

## Open questions
- ChatGPT का plan कौन सा है (Go, Plus या Pro), और Sora access है या नहीं
- Character का gender और look
- Instagram/Facebook API से AI label set होता है या नहीं (UNKNOWN)
