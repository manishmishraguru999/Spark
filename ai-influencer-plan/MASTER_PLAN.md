# MASTER PLAN — AI Influencer Venture (AIINF-001)

- **Date:** 2026-10-22
- **Status:** Research + pipeline तैयार हैं, launch बाकी है
- **Labels:** VERIFIED (official/tool data) · REPORTED (secondary) · INFERENCE (मेरा तर्क)

---

## 1. North Star और ईमानदार targets

**North Star:** 6 महीने में एक भरोसेमंद, Hindi-first AI host brand, जो हर हफ़्ते बिना टूटे content बनाए और brand deals से अपना खर्च खुद निकाले।

| Milestone | Conservative | Base | Stretch | Label |
|---|---|---|---|---|
| Day 30 (सभी platforms मिलाकर followers) | 1,000 | 3,000 | 10,000 | INFERENCE |
| Day 90 | 5,000 | 15,000 | 50,000 | INFERENCE |
| Day 180 | 15,000 | 50,000 | 1,50,000 | INFERENCE |
| पहली brand deal | Month 4–6 | Month 3–4 | Month 2 | INFERENCE |

**1 लाख in 30 दिन** सिर्फ़ एक viral breakout से संभव है, इसकी guarantee नहीं (~1.3% channels ही 100K तक पहुँचते हैं, vidIQ 2026, REPORTED)। Plan breakout की संभावना बढ़ाता है, उस पर निर्भर नहीं करता।

---

## 2. Research से निकली 10 बातें जो plan तय करती हैं

1. **सिर्फ़ AI चेहरा होना moat नहीं है।** India के बड़े virtual influencers के followers घट रहे हैं: Naina ~4.15 लाख (2024) से ~3.69 लाख (Aug 2026), Kyra ~2.55 लाख से ~2.4 लाख (REPORTED: creatordb.app, shethepeople.tv)। **Content format + consistency + trust** ही असली moat है।
2. **Brands AI influencers के साथ deal करते हैं:** Kyra के साथ boAt, Amazon Prime Video, L'Oréal (REPORTED)।
3. **Micro-influencer rates (10K–100K followers):** ज़्यादातर sources ₹5,000–25,000 प्रति Reel बताते हैं; range ₹2,000–80,000; GST अलग (REPORTED: dazzlerr.com, kofluence.com, upgrowth.in)। ₹5K budget को देखें तो **10K followers पहला कमाई वाला gate है।**
4. **Regional और Hindi creators का engagement बेहतर है:** regional micro-creators को metro macro-creators से 2–3× engagement मिलता है (Reelax H1 2026 via Deccan Chronicle, REPORTED)।
5. **YouTube A/B testing Shorts पर नहीं चलता** (VERIFIED: support.google.com/youtube/answer/16391400)। इसलिए hook learning हमारे pipeline की reports से होगी।
6. **Instagram Trial Reels** पहले non-followers को दिखते हैं, और अच्छा perform करें तो 72 घंटे में अपने-आप publish हो सकते हैं। Eligibility conflicting है (Creator/Business account, कुछ sources 1,000 followers कहते हैं) (REPORTED)।
7. **YouTube अपने-आप AI label लगाता है।** C2PA में "AI-generated" marked files पर label permanent रहता है। Label से recommendation या monetization पर असर नहीं पड़ता, ऐसा YouTube का दावा है (REPORTED: heise.de, May 2026)। इसलिए हमारी disclose-by-default policy सही है।
8. **Shorts:** पहले 1–3 सेकंड decisive हैं; high-retention Shorts आमतौर पर 15–45s के होते हैं (REPORTED, vendor data, YouTube का official data नहीं)।
9. **YPP 1 Feb 2027 से सख़्त होगा:** नए applicants के लिए 2 करोड़ Shorts views या 8,000 घंटे (REPORTED: Tubefilter)। Ads पर भरोसा कम रखें, **brand deals + अपने products** पर ज़ोर दें।
10. **"What if" India में ~3.7 लाख searches/month** (VERIFIED: vidIQ)। छोटे Hindi channels ने इस format पर 1 करोड़+ views लिए हैं (VERIFIED: tool data)।

---

## 3. Phases और decision gates

### Phase 0: Setup + Proof (Week 1–2)

| काम | Tool / file |
|---|---|
| BEAST पर setup | `pipeline/setup.ps1` → `--demo` → `--doctor` |
| Telegram bot + `dry_run: true` | README Step 6 |
| 2 synthetic चेहरे बनाना (ComfyUI) | `01_assets/character/face_A.png`, `face_B.png` |
| **Benchmark चलाना** | `--benchmark` → `grid.mp4` + `results.csv` |
| Persona lock: नाम, चेहरा, आवाज़, 5 personality traits | Benchmark के winners |
| Accounts: YouTube, Instagram (Creator), Facebook Page, 2FA | अलग email |

**🚦 Gate 0 (आगे तभी बढ़ें जब ये सब true हों):**
- Lip-sync realism और sync पर 3 लोगों का average **≥ 4/5**
- 10 कठिन Hindi words में से **≥ 8 सही**
- एक Reel का end-to-end समय **≤ 2 घंटे** (आपका काम)

**Gate fail होने पर:** talking head को ≤ 5 सेकंड रखें (voiceover वाला format), या HeyGen trial लें। Research report §10 के हिसाब से budget तब भी ₹5K के अंदर रहेगा।

### Phase 1: Launch (Week 3–6)
- **हफ़्ता 3:** dry-run। रोज़ 1 Reel बने, लेकिन post न हो। Captions, QC और safety warnings पर tuning।
- **हफ़्ता 4–6:** live। रोज़ 1 Reel (19:00 IST) YouTube + Instagram + Facebook पर। Moj/ShareChat पर हफ़्ते में 3 बार (manual folder से)।
- **Format mix:** 60% "What-if" numbered series, 20% "अनोखे facts", 20% trend reaction (trend radar से, अपने angle के साथ)।
- हर Short 25–45s का, hook पहले 2 सेकंड में, `captions.mode: words`।

**🚦 Gate 1 (Day 30):**
- 30 Shorts publish
- Viewed-vs-swiped ≥ 60% (YouTube Studio; benchmark unofficial है)
- कम से कम 3 Shorts channel median के 3× से ऊपर

**Fail होने पर:** format बदलें, persona नहीं। Pet-POV या ranking format (file 08) आज़माएँ।

### Phase 2: Optimize (Week 7–12)
- **Hook library:** हर हफ़्ते `/report` से top 3 hooks निकालें और अगले हफ़्ते उनके pattern दोहराएँ।
- **Series:** "What-if #N" numbering, और हर 10वाँ episode community के सवाल से।
- **Instagram Trial Reels** (eligibility मिलते ही): नए formats पहले trial में चलाएँ।
- **Community:** Telegram Channel + WhatsApp Channel, और pinned comment में सवाल।

**🚦 Gate 2 (Day 90):** किसी एक platform पर ≥ 10K followers **या** ≥ 5 लाख monthly views → media kit बनाकर brands से बात शुरू करें।

### Phase 3: Monetize + Scale (Month 4–6)

| Step | कैसे |
|---|---|
| Media kit | Audience (16–30, India), avg views, engagement, AI disclosure policy |
| Brand categories (fit) | Tech gadgets, edtech, apps, books, science museums/events (health/finance नहीं) |
| Pricing start | ₹5,000–15,000 प्रति Reel (micro tier का निचला हिस्सा, REPORTED range) |
| Disclosure | Paid partnership tool + ASCI (verify) + "AI character" mention |
| Scale | `--new-project` से दूसरा venture या English/Tamil version (अलग channel) |

---

## 4. Weekly operating rhythm (आपके घंटे)

| समय | काम | Pipeline feature |
|---|---|---|
| रोज़ सुबह (10 min) | Report पढ़ें, trends देखें, 1 idea save करें | Daily report, `/trends`, `/idea` |
| रोज़ (20 min) | ChatGPT से script बनाकर `/new` भेजें, कल का preview approve करें | Safety gate, QC, preview buttons |
| रोज़ (5 min) | YouTube manual upload, `/yt <id> <link>`, Moj/ShareChat post | Manual folders + cover |
| Saturday (5–6 h) | 7 scripts batch में, character/face fixes, 1–2 hero shots Nuke/AE में, comments | ComfyUI queue (रात भर) |
| Sunday (1–2 h) | Weekly review: top 3 hooks, next week series plan | `/report` |
| Monthly | `--doctor`, benchmark re-check, backup verify, cost review | `--doctor`, `/backup` |

---

## 5. यह project क्यों मज़बूत है (moat)

1. **VFX-grade finishing:** ज़्यादातर AI channels raw output डालते हैं; आपके पास Nuke/AE की skill है। (INFERENCE)
2. **Compliance-by-default:** safety gate, AI metadata, C2PA option, disclosure line, approve step। Platforms के सख़्त होने पर भी channel सुरक्षित रहेगा।
3. **Auto QC:** काली screen, खामोशी, गलत loudness या size वाली video कभी publish नहीं होगी।
4. **Hindi word-pop captions:** trending style, अपने-आप।
5. **Data loop:** daily report, hook learning, trend radar और idea bank, ताकि content कभी न रुके।
6. **15 platforms का registry:** एक video, हर जगह, हर platform की limit के हिसाब से caption।
7. **Reusable engine:** `--new-project` से अगला venture minutes में शुरू।
8. **Local-first cost:** ~₹1,500–1,620/month (research report §10)।

---

## 6. Top risks

| Risk | Early warning | Response |
|---|---|---|
| Lip-sync अजीब लगे ("uncanny") | Comments में "fake / AI slop" | Talking head कम, voiceover visuals ज़्यादा |
| Mass-produced flag | Monetization या reach अचानक गिरे | हर Short में original angle, series variety, approve step |
| Viral facts गलत निकलें | Correction comments | Caption में source line, Ollama review, `claims_to_verify` |
| Persona fatigue (Kyra/Naina trend) | Followers flat हों | Format refresh, community questions, collab |
| PC या disk failure | Doctor/disk alerts | Weekly backup दूसरी drive पर, UPS |
| Platform API बदलाव | Publish errors | Manual hand-off fallback पहले से बना है |

---

## 7. अगले 7 कदम (इसी क्रम में)

1. BEAST पर `pipeline/setup.ps1` चलाएँ, फिर demo + doctor का screenshot भेजें।
2. Telegram bot बनाकर `dry_run` में `/new` test करें।
3. ComfyUI में 2 synthetic faces बनाएँ और workflow export करें (README Step 8)।
4. MuseTalk और LatentSync 1.5 install करके `--benchmark` चलाएँ।
5. 3 लोगों से `results.csv` में ratings भरवाएँ, फिर Gate 0 का फ़ैसला।
6. Persona sheet: नाम, चेहरा, आवाज़, traits, bio (AI disclosure के साथ)।
7. Accounts बनाकर Instagram profile पर AI-generated label लगाएँ, फिर Phase 1 शुरू।

---

## Sources (इस plan में नए)
- Virtual influencers India: https://www.shethepeople.tv/lifestyle/indian-ai-generated-influencers-naina-kyra-4739622 · https://creatordb.app/creatorstats/naina_avtr/ · https://campaignindia.in/article/role-and-relevance-of-virtual-influencers-in-india/500045
- Influencer rates India: https://www.dazzlerr.com/influencer-rates-india-2026/ · https://www.kofluence.com/?p=68787 · https://upgrowth.in/influencer-marketing-pricing-india-2026/ · https://www.deccanchronicle.com/amp/business/indias-influencer-marketing-boom-industry-nears-5000-crore-as-regional-creators-rise-1970876
- YouTube A/B testing (Shorts excluded): https://support.google.com/youtube/answer/16391400
- Instagram Trial Reels: https://postfa.st/blog/instagram-trial-reels · https://www.inro.social/blog/what-is-a-reel-trial-and-how-does-it-work
- YouTube auto AI labels: https://heise.de/-11309100
- Shorts hooks/length (vendor data): https://joinbrands.com/blog/youtube-shorts-best-practices/ · https://www.gofaceless.ai/en/blog/high-retention-youtube-shorts-attributes
- faster-whisper (MIT, word timestamps): https://awesome.ecosyste.ms/projects/github.com%2Fsystran%2Ffaster-whisper
- पहले की research: `claude_research_report.md`, `08_TRENDING_NICHES_AND_PER_AI_RESEARCH_PROMPTS.md`, `pipeline/PLATFORMS.md`, `pipeline/ROADMAP.md`
