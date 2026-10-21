# claude_research_report.md
## AI Influencer Channel: Local Production बनाम Paid AI Tools — Research Report

- **Research date:** 2026-10-21 (vidIQ/Nextlev का channel data 2026-10-18 का है)
- **Stage:** सिर्फ़ research। कोई purchase, billable generation, software install, account change या publishing नहीं किया गया।
- **Evidence labels:** VERIFIED (official/primary source या live tool data) · REPORTED (secondary source) · INFERENCE (मेरा तर्क) · UNKNOWN · CONFLICT (sources में टकराव)
- **"Not tested":** इस report में किसी भी tool को मैंने खुद चलाकर नहीं परखा। सारी quality और speed की बातें sources से हैं, measurement नहीं।

---

## 1. Decision-ready findings (सबसे ज़रूरी 10 बातें)

1. **Recommended stack: Hybrid (C)।** Typical retry scenario में इसका खर्च ≈ **₹1,640/month** है, जो ₹5,000 budget में आराम से fit होता है। Paid-cloud-first stack (B) ≈ **₹16,350/month** का है, यानी budget का 3 गुना से ज़्यादा। (INFERENCE, cost model section 5 में)
2. **Local-first (A) सबसे सस्ता है (≈ ₹650/month cash),** लेकिन इसमें ~88 GPU-hours/month लगते हैं और human time भी सबसे ज़्यादा है। (INFERENCE)
3. **Hindi voice सबसे सस्ता cloud में मिलता है:** Sarvam Bulbul v3 का rate **₹30 per 10,000 characters** है (VERIFIED, official pricing page)। इस हिसाब से 55 min narration ≈ ₹200–270/month बनता है। ElevenLabs Creator **$22/month** है, जिसमें ~121 min मिलते हैं (VERIFIED)। Hindi quality की तुलना not tested है।
4. **Local Hindi voice:** AI4Bharat Indic Parler-TTS **Apache 2.0** है, यानी commercial use ठीक है (VERIFIED)। XTTS-v2 का license (Coqui Public Model License) **non-commercial only** है, इसलिए monetized channel पर इसका इस्तेमाल न करें (REPORTED, कई sources सहमत)।
5. **Local lip-sync free और commercial-safe है:**
   - MuseTalk: code MIT, model "any purpose, even commercially" (VERIFIED)
   - LatentSync 1.5: Apache-2.0, **8 GB VRAM** (VERIFIED)
   - LatentSync 1.6 को 18 GB चाहिए, जो RTX 3060 12GB पर नहीं चलेगा।
6. **Local video (Wan 2.2 TI2V-5B):** Apache 2.0 है, 720p@24fps, 5 सेकंड की clip (VERIFIED)। लेकिन official model card **"at least 24GB VRAM"** कहता है। Community reports 12GB पर offloading के साथ ~10–15 min/clip बताते हैं। **यह CONFLICT है,** benchmark से तय होगा।
7. **Platform rules अब सख़्त हैं:**
   - YouTube पर realistic AI content का disclosure ज़रूरी है (VERIFIED)।
   - Instagram पर AI-generated person वाले profile पर **"AI-generated profile" label** न लगाने से reach कम हो सकती है (REPORTED)।
   - Facebook पर unoriginal/duplicate content की reach घटाई जाती है (REPORTED)।
   - India में 20 Feb 2026 से IT Rules में synthetic content की labelling आ गई है (REPORTED)।
8. **एक ही video तीनों platforms पर चलाना संभव है,** बशर्ते video original हो, किसी दूसरे app का watermark न हो, और हर platform पर AI disclosure किया जाए। **Length ≤ 90 सेकंड रखना सबसे सुरक्षित है,** क्योंकि Facebook Reels की limit पर sources में conflict है।
9. **YPP:** अभी 1,000 subs + 4,000 watch hours या 90 दिन में 1 करोड़ Shorts views चाहिए। **1 Feb 2027 से नए applicants के लिए 8,000 hours या 2 करोड़ Shorts views** (REPORTED, Tubefilter)। Shorts-only plan के लिए monetization 2027 में और मुश्किल होगा।
10. **Provisional persona recommendation:** "What-if / अनोखे facts" host। India में "what if" की ~3.7 लाख monthly searches हैं (VERIFIED, vidIQ)। छोटे Hindi channels ने इस format पर 1 करोड़+ views लिए हैं (VERIFIED data)। यह **user-approved नहीं है,** सिर्फ़ सुझाव है।

---

## 2. Inputs, unknowns और assumptions

### 2.1 पहले से मिली जानकारी (बातचीत से)

| Field | Value | Status |
|---|---|---|
| Concept | AI-generated influencer persona; tutorial नहीं; kids content नहीं | User द्वारा दिया |
| Audience | 16–30 साल, India first, फिर global | User द्वारा दिया |
| Content language | Hinglish/Hindi पहले, बाद में और भाषाएँ | User द्वारा दिया |
| Persona | Fictional virtual face (लड़का/लड़की, कोई भी) | User द्वारा दिया |
| Platforms | YouTube Shorts + Instagram Reels + Facebook Reels, **एक ही content** | User द्वारा दिया |
| Budget | ₹5,000/month, कोई loan नहीं | User द्वारा दिया |
| PC | Windows, i9-12900K, RTX 3060 12GB, 64GB RAM, 2TB NVMe | User profile से |
| Experience | Senior VFX compositor (Nuke, AE, Blender, Resolve, ComfyUI) | User profile से |
| Baseline metrics | New account | User द्वारा दिया |
| Stated goal | 1 लाख followers 30 दिन में | पिछली research में unrealistic पाया गया |

### 2.2 Declared assumptions (provisional)

| Assumption | Value | क्यों |
|---|---|---|
| Hours/week | ~21 घंटे (3 घंटे/दिन) | पहले के plan में यही माना गया था |
| Existing paid subscriptions | कोई नहीं | Unknown |
| Monetization | Undecided; पहले ads + brand deals | Unknown |
| Start date | Research पूरी होने के बाद | Unknown |
| Reel length | 30 सेकंड final | Baseline के लिए |
| Long video length | 5 मिनट final | Baseline के लिए |
| AI-generated हिस्सा (per Reel) | 15 सेकंड talking avatar + 10 सेकंड generated video; बाकी stills/motion graphics | Final duration और generated duration अलग रखे हैं |
| AI-generated हिस्सा (per long video) | 2 मिनट avatar + 1 मिनट generated video | वही |
| USD→INR | **₹95/USD** (planning rate) | Sources में 94.46 (x-rates) से 96.52 (Pluang) तक; दोनों के timestamps साफ़ नहीं → CONFLICT |
| Electricity | ₹8/kWh | Maharashtra mid-slab ~₹7.9–10.3; Delhi कम (REPORTED) |
| PC power under load | ~0.35 kW | RTX 3060 TGP 170W (REPORTED, कई sources) + CPU + बाकी (INFERENCE) |

### 2.3 Concept के तीन provisional directions

| Direction | Evidence | Fit |
|---|---|---|
| **A. "What-if / अनोखे facts" host** (एक curious AI character) | IN में "what if" ~3,70,772 searches/month (VERIFIED vidIQ, 2026-10-21); Hindi what-if Short 1.13 करोड़ views, 14.9K subs channel (VERIFIED, 2026-10-18) | **Provisional recommendation** |
| B. Desi family/dosti story series (recurring AI characters) | 3.9K subs channel का story Short 92.6 लाख views (VERIFIED) | Emotional-manipulation policy risk ज़्यादा |
| C. Tech & AI news reaction host | "ai tools" IN ~2.25 लाख searches, competition 66 (VERIFIED, पिछली research) | Competition ज़्यादा, accuracy का भारी दबाव |

**Direction A क्यों:**
- Policy risk कम है।
- AI visuals इस concept में naturally fit होते हैं ("अगर ऐसा हो जाए तो…" वाले scenes)।
- एक ही video तीनों platforms पर चल सकता है।
- Evergreen है, यानी किसी एक event पर निर्भर नहीं।

---

## 3. Audience, competitors और opportunities

### 3.1 पाँच audience problems / viewing intentions (16–30, India)

| # | Problem / intention | Audience की अपनी भाषा में सवाल (example) | Evidence | Label |
|---|---|---|---|---|
| 1 | छोटे breaks में quick curiosity और मनोरंजन | "अगर सूरज गायब हो जाए तो क्या होगा?" | "what if sun disappears" IN ~30,974/month; "what if earth stopped spinning" ~27,201 | VERIFIED (demand), INFERENCE (intent) |
| 2 | "क्या आप जानते हैं" वाला knowledge, जो आगे share किया जा सके | "दुनिया का सबसे अनोखा घर कौन सा है?" | Hindi facts Short 90.5 लाख views; "facts in hindi" IN ~18,024/month | VERIFIED |
| 3 | AI और tech के बदलाव से FOMO | "AI से मेरी job जाएगी क्या?" | "ai tools" IN ~2.25 लाख; tech launches rising (पिछली research) | VERIFIED (demand), INFERENCE (intent) |
| 4 | Relatable family/hostel/dosti ज़िंदगी | "हर घर में ऐसी ननद होती है न?" | Family story Shorts 92.6 लाख views | VERIFIED (views), INFERENCE (intent) |
| 5 | Imagination और "future" वाले scenarios | "2100 में India कैसा दिखेगा?" | "Earth 6030 future" series avg 96 लाख views (Nextlev) | VERIFIED |

**Note:** Search demand सीधे Instagram reach या YouTube audience का proof नहीं है। यह सिर्फ़ curiosity का signal है।

### 3.2 Competitor / example observations

सभी observations 2026-10-18 के हैं। ये title और metadata से हैं; videos देखे नहीं गए। Follower count को success का proof नहीं माना गया है।

| # | Channel / video | URL | Language | Niche | Format (observed) | Public numbers (observed) |
|---|---|---|---|---|---|---|
| 1 | Movies Ka Adda — "अगर 24 करोड़ साल पहले डायनासोरों की दुनिया में एक बांस गिर जाये तो" | https://www.youtube.com/watch?v=BuJYXaWk6aA | Hindi | What-if | 179s Short, imagination scenario | 14.9K subs; 1.13 करोड़ views |
| 2 | Concrete World — "हवा में टिका है पूरा घर! नीचे सिर्फ एक खंभा" | https://www.youtube.com/watch?v=bML1uQrLFYM | Hindi | Engineering wonders | 16s Short, visual surprise | 13K subs; 1.05 करोड़ views; engagement 0.4% |
| 3 | Info Truth Hub — "क्या आप जानते हैं कि एशिया के 9 सबसे ज्यादा…" | https://www.youtube.com/watch?v=zRRDfDxuL9o | Hindi | Facts / ranking | 153s Short | 51.8K subs; 90.5 लाख views |
| 4 | Ani Tadka Tales — "अमीर ननद ने उड़ाया मजाक, भाभी ने बचाई पूजा!" | https://www.youtube.com/watch?v=Ssb9BSQCEgI | Hindi | Family story | 180s Short | 3.88K subs; 92.6 लाख views |
| 5 | KahaniJunction — "मॉम के दुपट्टे से बनाई Haldi और Mehndi Dress… #aistory" | https://www.youtube.com/watch?v=EbcFnFfHPUo | Hindi | AI story | 60s Short, AI-tagged | 2.28L subs; 19.5 लाख views |
| 6 | Gapputomato — "रानी आज फिर से चिंटू को स्कूल ले गयी" | https://www.youtube.com/watch?v=I0JbsU6isrQ | Hindi | Pet character story | 71s Short | 1.32L subs; 29.2 लाख views |
| 7 | HeroRanking — "Ranking Diving Super Heroes" | https://www.youtube.com/watch?v=bSfNt8qwnWk | English | Ranking (AI) | Ranking Short | 39.6K subs, 9 uploads; ~2.5 करोड़ views |
| 8 | ZawPolyShorts — "What Your Cat Thinks You're Doing When You Leave The House?" | https://www.youtube.com/watch?v=I_0fY2sCfaQ | English | Pet psychology (AI) | "You"-framed curiosity title | 1.18L subs, 10 uploads; ~2 करोड़ views |

**Observation बनाम interpretation:**
- **Observed:** छोटे Hindi channels (4K–15K subs) के single Shorts 90 लाख से 1.1 करोड़ views तक गए।
- **Interpretation (INFERENCE):** Hindi Shorts में format और hook, subscriber base से ज़्यादा मायने रखते हैं। लेकिन survivorship bias है: fail हुए channels इस data में नहीं दिखते। Retention, revenue या bought views के बारे में public data से कुछ नहीं कहा जा सकता।

### 3.3 Differentiation opportunities (evidence-supported)

1. **एक recurring, नाम वाला AI host:** ऊपर के ज़्यादातर Hindi viral examples में कोई consistent character नहीं है। Mimi (AI cat) जैसे examples में named character ने काम किया (Nextlev, पिछली research)। (INFERENCE)
2. **Hinglish + Devanagari captions + साफ़ AI disclosure:** "AI host, real facts" वाली positioning trust बना सकती है। (INFERENCE)
3. **VFX-grade visual quality:** ज़्यादातर examples basic quality के हैं। आपकी compositing skill visual quality में फ़र्क ला सकती है। (INFERENCE)
4. **Numbered series** ("What-if #17"): series format ने English channels में repeat viewers बनाए (Nextlev data)। Hindi में इसका कम इस्तेमाल दिखा। (INFERENCE)
5. **Fact-checked what-if:** viral facts channels में accuracy पर सवाल उठते हैं। हर Short में description में एक source line देने से differentiation बनेगा। (INFERENCE)

---

## 4. Tool और hardware comparison

### 4.1 Stage-wise comparison (local बनाम paid)

Abbreviations: **TTS** = text-to-speech, **VRAM** = GPU memory, **IVC** = instant voice cloning, **API** = प्रति-उपयोग billing (subscription से अलग)।

| Task | Tool / model | Local/Cloud | Hindi quality evidence | Character consistency | Hardware (min / practical) | Setup | Main limitation | Commercial license | Data/privacy | Watermark/export | Monthly price | Annual | Limits | Extra cost | Best fit | Source + date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1. Script | Ollama (any open LLM) | Local | Model पर निर्भर; not tested | — | 8–12GB VRAM छोटे models के लिए (INFERENCE) | आसान | Hindi writing quality छोटे models में कमज़ोर | License repo में; MIT माना जाता है (इस session में confirm नहीं) | Data PC पर रहता है | — | ₹0 | — | Hardware | Electricity | Privacy चाहने वाले | github.com/ollama/ollama, 2026-10-21 |
| 1. Script | LM Studio | Local | वही | — | वही | बहुत आसान (GUI) | वही | **Work use free** (VERIFIED) | Local | — | ₹0 | — | — | — | Beginner local | lmstudio.ai/blog/free-for-work, 2026-10-21 |
| 1. Script | ChatGPT Go / Plus | Cloud | Hindi अच्छी (REPORTED, general) | — | Browser | आसान | Usage limits | Commercial use OK (terms check करें) | Cloud | — | Go ₹399 · Plus ₹1,999 (REPORTED, Aug 2025 launch coverage) | — | Plan limits | — | Budget creator | techcrunch.com 2025-08-18; chatgpt.com/pricing (INR नहीं दिखा), 2026-10-21 |
| 1. Script | Claude Pro | Cloud | Not tested | — | Browser | आसान | Usage limits | Terms check करें | Cloud | — | $20 monthly | $17/mo ($200 upfront) | Plan limits | — | Research + writing | claude.com/pricing, 2026-10-21 (VERIFIED) |
| 2. Images/character | ComfyUI + SDXL / FLUX.1 schnell | Local | — | LoRA/IP-Adapter से अच्छी (INFERENCE) | 8GB / 12GB | Medium (आपके लिए आसान) | Consistency के लिए LoRA training का समय | ComfyUI: license file मौजूद, GPL-3.0 माना जाता है (confirm नहीं) · FLUX.1 schnell: Apache 2.0 (REPORTED) · **FLUX.1 dev: local outputs commercial = CONFLICT** | Local | No watermark | ₹0 | — | GPU time | Electricity | VFX artist | github.com/Comfy-Org/ComfyUI; help.bfl.ai; 2026-10-21 |
| 2. Images | Runway Gen-4 Images | Cloud | — | Reference images | Browser | आसान | Credits | Terms check करें | Cloud | Standard में no watermark (VERIFIED) | $15 (625 credits ≈ 78 images) | $12/mo | Credits | — | Quick tests | runwayml.com/pricing, 2026-10-21 |
| 3. Hindi voice | **Indic Parler-TTS** (AI4Bharat) | Local | Hindi NSS 83.4–84.8% (model card), 107 hrs Hindi data | Text description से voice style | GPU recommended; exact VRAM UNKNOWN | Medium | Voice cloning नहीं; prosody control सीमित | **Apache 2.0** (VERIFIED) | Local | — | ₹0 | — | — | Electricity | Free, commercial-safe | huggingface.co/ai4bharat/indic-parler-tts, 2026-10-21 |
| 3. Hindi voice | XTTS-v2 | Local | Hindi supported | Voice clone | 6–8GB (INFERENCE) | Medium | **Non-commercial license** | **No** (REPORTED, CPML) | Local | — | ₹0 | — | — | — | सिर्फ़ personal tests | huggingface.co/coqui/XTTS-v2; bentoml.com, 2026-10-21 |
| 3. Hindi voice | **Sarvam Bulbul v3** (API) | Cloud | Indian languages के लिए बना (REPORTED); not tested | Fixed voices | Browser/API | आसान–medium (API) | Beta pricing | Terms check करें | Indian company, cloud | — | **₹30 / 10K chars** (pay-as-you-go) | — | Per character | Free ₹1,000 credits (official) | Budget Hindi narration | docs.sarvam.ai/api/pricing, 2026-10-21 (VERIFIED) |
| 3. Hindi voice | ElevenLabs | Cloud | 74 languages (VERIFIED); Hindi quality not tested | IVC/PVC voice clone | Browser | आसान | Credits जल्दी खत्म | **Starter से commercial** (VERIFIED) | Cloud | — | Starter $6 (30 min) · Creator $22 (121 min; पहला month $11) | Starter $5/mo · Creator $18.33/mo | Credits | INR pricing page पर नहीं दिखी | Premium voice | elevenlabs.io/pricing, 2026-10-21 (VERIFIED) |
| 4. Lip-sync | **MuseTalk** | Local | Language-independent (audio-driven) (INFERENCE) | Same face image | 4GB laptop GPU पर test हुआ; 8s video ≈ 5 min (official) | Medium | Face crop/angle सीमित | **Code MIT; model any purpose incl. commercial** (VERIFIED) | Local | — | ₹0 | — | — | Electricity | Free avatar | github.com/TMElyralab/MuseTalk, 2026-10-21 |
| 4. Lip-sync | **LatentSync 1.5** | Local | Not tested | Same face | **8 GB** (1.6 के लिए 18 GB) | Medium | 1.6 3060 पर नहीं चलेगा | **Apache-2.0** (VERIFIED) | Local | — | ₹0 | — | — | Electricity | Better quality local | github.com/bytedance/LatentSync, 2026-10-21 |
| 4. Talking avatar | HeyGen | Cloud | Hindi support claimed (REPORTED) | Avatar consistent | Browser | आसान | Credits; plan details में conflict | Terms check करें | Cloud | Free plan में watermark (REPORTED) | Creator $29 (REPORTED) | $24/mo (REPORTED) | ~30 min Avatar IV **या** 10 min → CONFLICT | — | Fastest avatar | creatify.ai, eesel.ai, arcade.software (official page पर details नहीं मिले), 2026-10-21 |
| 5. Video gen | **Wan 2.2 TI2V-5B** | Local | — | Image-to-video से character बना रहता है | Official: **≥24GB**; community: 12GB पर offloading (CONFLICT) | Medium–hard | धीमा; 5s clip | **Apache 2.0** (VERIFIED) | Local | — | ₹0 | — | 720p@24fps, 5s | Electricity | Patience + GPU | huggingface.co/Wan-AI/Wan2.2-TI2V-5B, 2026-10-21 |
| 5. Video gen | Runway | Cloud | — | References | Browser | आसान | Credits जल्दी खत्म | Terms check करें | Cloud | Standard: no watermark | Standard $15 (≈104s Gen-4 Turbo) · Pro $35 (≈375s) · Max $95 (≈1,900s) | $12 / $28 / $76 | Credits | — | High quality shots | runwayml.com/pricing, 2026-10-21 (VERIFIED) |
| 5. Video gen | Kling | Cloud | — | Reference image | Browser | आसान | Credits roll over नहीं होते | Terms check करें | Cloud | UNKNOWN | Standard ~$6.99 first month, ~$8.80 renewal, 660 credits (REPORTED) | $79.20/yr (REPORTED) | Credits/clip UNKNOWN | — | Budget hero shots | eesel.ai, cloudzero.com (official page तक पहुँच नहीं हुई), 2026-10-21 |
| 6. Edit | DaVinci Resolve (free) | Local | — | — | आपके PC पर चलेगा | आसान (आपके लिए) | कुछ AI features Studio-only हैं (UNKNOWN कौन से) | Free version commercial use OK (INFERENCE; EULA check करें) | Local | No watermark | ₹0 | Studio one-time $236 (sale; पहले $295) | — | — | Main editor | blackmagicdesign.com, 2026-10-21 (VERIFIED price) |
| 6. Subtitles | Whisper large-v3 | Local | Hindi WER ~26.8% (Vaani leaderboard) या 34.1 (paper) → CONFLICT; हाथ से correction ज़रूरी | — | 10GB तक (INFERENCE) | Medium | Hindi accuracy सीमित | **MIT (code + weights)** (VERIFIED) | Local | — | ₹0 | — | — | — | Free subtitles | github.com/openai/whisper; benchmarklist.com; arxiv.org/pdf/2606.21408, 2026-10-21 |
| 7. Scheduling | Meta Business Suite | Cloud | — | — | Browser | आसान | Scheduled Reels में trending audio शायद न मिले (REPORTED, single source) | — | Meta | — | ₹0 | — | 75 दिन पहले तक schedule | — | IG + FB एक साथ | blog.nuelink.com, 2026-10-21 (REPORTED) |
| 7. Scheduling | YouTube Studio | Cloud | — | — | Browser | आसान | — | — | Google | — | ₹0 | — | — | — | Shorts | इस session में verify नहीं हुआ (INFERENCE: built-in scheduling) |
| 7. Analytics | YouTube Studio + Instagram/Meta Insights | Cloud | — | — | — | आसान | Cross-platform एक जगह नहीं | — | — | — | ₹0 | — | — | — | सभी | — |

**Stage 4 और 5 के लिए note:** Local talking-avatar के ready-made, high-quality, one-click विकल्प कम हैं। Local lip-sync के लिए पहले एक base video या image चाहिए, फिर audio sync होता है। Quality cloud avatars से कम हो सकती है (INFERENCE, not tested)।

### 4.2 Personal computer feasibility (profiles)

**आपका profile = Profile 3** (RTX 3060 12GB, 64GB RAM)। Exact render speeds नहीं दिए गए हैं, क्योंकि test नहीं किए।

| Profile | Text (LLM) | Image | Voice (TTS) | Lip-sync | Video gen | Storage need | Setup | Main bottleneck |
|---|---|---|---|---|---|---|---|---|
| 1. Integrated GPU, 8–16GB RAM | छोटे quantized models, धीमे | बहुत धीमा, practical नहीं | CPU पर छोटे TTS models | Practical नहीं | Practical नहीं | 50GB | आसान | GPU का न होना → cloud लें |
| 2. 6–8GB VRAM, 16–32GB RAM | 7–8B quantized models | SDXL 1024px, धीमा | Indic Parler-TTS (INFERENCE) | MuseTalk (4GB पर test हुआ, official) | Wan 5B सिर्फ़ low res + offloading; crashes का risk | 150–250GB | Medium | VRAM + system RAM |
| **3. 12–16GB+ VRAM, 32GB+ RAM (आपका)** | 7–14B quantized | SDXL/FLUX schnell + LoRA training | Indic Parler-TTS | MuseTalk, **LatentSync 1.5 (8GB)** | Wan 2.2 5B offloading के साथ (official 24GB कहता है → test करें) | 250–400GB (models + cache + projects) | Medium (आपके लिए आसान) | Video gen की speed; 12GB VRAM |
| 4. Apple Silicon (unified memory) | अच्छा (unified memory) | Medium | Medium | CUDA-only tools नहीं चलते (INFERENCE) | सीमित | 250GB | Medium | CUDA support नहीं |

**Note:** Quantization (model को छोटा करना), resolution और clip duration speed को बहुत बदलते हैं। Speed के सारे आँकड़े section 6 के benchmark से ही तय होंगे।

---

## 5. तीन production stacks और असली costs

### 5.1 Common baseline

- **Volume:** 30 Reels (हर एक 30s final) + 8 long videos (हर एक 5 min final)। 4 optional extra long videos अलग से priced हैं।
- **Narration per month:** 55 min (12 long videos के साथ 75 min)।
- **AI-generated हिस्सा:** avatar 23.5 min + generated video 780s (13 min) = **36.5 AI-generated minutes**।
- **Retry multipliers (TTS / lip-sync / video-gen):** low 1.1/1.2/1.5 · typical 1.3/1.5/2.0 · high 1.6/2.0/3.0।
- **Formula:** Monthly cost = subscriptions + API/credits + retries (credits वाले tools में retries billed credits में ही गिने गए हैं, दोबारा नहीं) + storage (मौजूदा 2TB, ₹0) + electricity + hardware allocation (अलग दिखाया)।

### 5.2 Stacks

| Stack | Script | Voice | Images | Avatar/lip-sync | Video gen | Edit/subs | Schedule |
|---|---|---|---|---|---|---|---|
| **A. Local-first** | ChatGPT Go ₹399 (optional) या LM Studio | Indic Parler-TTS (local) | ComfyUI (local) | MuseTalk / LatentSync 1.5 | Wan 2.2 5B (local) | Resolve free + Whisper | Meta Business Suite + YT Studio |
| **B. Paid-cloud-first** | ChatGPT Plus ₹1,999 | ElevenLabs Creator $22 | Runway | HeyGen Creator $29 | Runway (Max $95 ज़रूरी बनता है) | Resolve free | वही |
| **C. Hybrid (recommended)** | ChatGPT Go ₹399 | **Sarvam Bulbul v3 API** | ComfyUI (local) | MuseTalk / LatentSync 1.5 (local) | 70% Wan local + 30% Kling Standard hero shots | Resolve free + Whisper | वही |

### 5.3 Monthly cost (code से calculated, INR, ₹95/USD, ₹8/kWh)

**Baseline: 30 Reels + 8 long videos**

| Retry scenario | A Local-first | B Paid-cloud-first | C Hybrid |
|---|---|---|---|
| Low | ₹590 (GPU 68 hrs) | ₹15,869 | ₹1,565 (GPU 53 hrs) |
| **Typical** | **₹646 (GPU 88 hrs)** | **₹16,351** | **₹1,641 (GPU 69 hrs)** |
| High | ₹755 (GPU 127 hrs) | ₹19,520 | ₹1,772 (GPU 98 hrs) |

**+4 optional long videos (कुल 12)**

| Retry scenario | A | B | C |
|---|---|---|---|
| Low | ₹648 | ₹16,585 | ₹1,676 |
| Typical | ₹722 | ₹18,118 | ₹1,778 |
| High | ₹865 | ₹24,410 | ₹1,952 |

### 5.4 Per-unit cost (typical, 8 long videos)

| Unit | A | B | C |
|---|---|---|---|
| Per usable Reel (0.5 min) | ~₹6 | ~₹149 | ~₹15 |
| Per usable long video (5 min) | ~₹59 | ~₹1,487 | ~₹149 |
| Per AI-generated minute (36.5 min/month) | ~₹18 | ~₹448 | ~₹45 |

### 5.5 Cash, annual और hardware

- **Monthly cash बनाम annual upfront:** Runway Standard $12/mo annual, ElevenLabs Creator $18.33/mo annual, Claude Pro $200 upfront। Annual plans ~15–20% बचाते हैं, लेकिन पैसा upfront जाता है। **पहले 3 महीने monthly plan ही लें।**
- **First-period discounts:** ElevenLabs Creator पहला महीना $11, Kling ~$6.99 → renewal पर कीमत बढ़ती है।
- **Hardware:** मौजूदा PC पर नया cash ₹0 है। Optional amortization formula: (PC value ÷ 36 महीने)। उदाहरण के लिए, अगर PC ₹1,50,000 का है, तो ≈ ₹4,167/month (assumption, cash खर्च नहीं)।
- **Taxes:** GST या foreign transaction fee शामिल नहीं हैं (UNKNOWN)। ElevenLabs page पर INR pricing नहीं दिखी।

### 5.6 Human time (INFERENCE, not tested)

| Stack | Per Reel | Per long video | Monthly total |
|---|---|---|---|
| A | ~2 hrs | ~6 hrs | ~108 hrs |
| B | ~1 hr | ~3 hrs | ~54 hrs |
| C | ~1.5 hrs | ~5 hrs | ~85 hrs |

Assumed 21 hrs/week ≈ 90 hrs/month के हिसाब से **A थोड़ा over है, C fit होता है।**

### 5.7 Break-even: कब कौन सा stack बेहतर है

- **B तब बेहतर है जब** आपके एक घंटे की value ≥ (₹16,351 − ₹646) ÷ ~54 बचे हुए घंटे ≈ **₹290/hr** हो, **और** budget ₹16K+ हो। आपका budget ₹5K है, इसलिए अभी B fit नहीं होता। (INFERENCE)
- **A तब बेहतर है जब** time ज़्यादा हो और cash कम। GPU रात भर चल सकता है।
- **C तब तक सही है जब तक** Kling/Sarvam का खर्च ~₹3,000 से कम रहे। Generated video 3 गुना होने पर Kling Pro (~$32.56 renewal, REPORTED) लेना पड़ेगा, और C ≈ ₹4,000 तक पहुँचेगा।

### 5.8 Recommendation और कमज़ोरियाँ

**Recommended: C (Hybrid)।**

कमज़ोरियाँ:
- Sarvam और local lip-sync की Hindi quality untested है।
- Wan 2.2 5B का 12GB पर चलना CONFLICT है।
- Kling की official pricing तक पहुँच नहीं हुई।
- Human time ~85 hrs/month है, जो ज़्यादा है।

**B पर कब जाएँ:** जब revenue ₹16K+/month हो जाए, या time बचाना cost से ज़्यादा ज़रूरी हो जाए।

---

## 6. Fair benchmark protocol

**Status: Planned. अभी कोई test नहीं चला है।** इस request में billable generation और installation authorized नहीं थे।

### 6.1 Fixed inputs (सभी tools के लिए एक जैसे)

- एक Hindi script (~75 words, 30 सेकंड), जिसमें मुश्किल words हों: "क्षितिज", "ज्ञान", "श्रृंखला", और English words "AI", "WhatsApp"
- एक ही character reference image (front face, 1024px)
- Output 1080×1920, 30fps, 30 सेकंड
- Target quality: "Shorts पर publish करने लायक"

### 6.2 Test matrix

| Stage | Option 1 | Option 2 | Option 3 |
|---|---|---|---|
| Voice | Indic Parler-TTS (local) | Sarvam Bulbul v3 (free ₹1,000 credits) | ElevenLabs (free 10k credits) |
| Lip-sync | MuseTalk (local) | LatentSync 1.5 (local) | HeyGen free tier (watermark चलेगा) |
| Video 5s clip | Wan 2.2 5B (local, offload) | Kling free daily credits | Runway free 125 credits |

### 6.3 Metrics (हर test के लिए)

| Metric | कैसे मापें |
|---|---|
| Usable-output rate | 10 attempts में से कितने publish लायक |
| Pronunciation | 10 कठिन words में से कितने सही (3 लोगों से blind rating) |
| Lip-sync | 1–5 scale, 3 raters |
| Character consistency | 5 clips में चेहरा वही लगा? (हाँ/नहीं) |
| Total production time | Stopwatch से (setup अलग रखें) |
| Retries | गिनती |
| Cost per usable minute | (खर्च ÷ usable minutes) |

**Rule:** Results के लिए "Measured" column अलग रखें। Estimate और measured को कभी मिलाएँ नहीं।

---

## 7. Platform requirements (official sources पहले)

| Requirement | Platform | Rule (संक्षेप) | Status | Source | Verified on |
|---|---|---|---|---|---|
| AI/altered content disclosure | YouTube | Realistic synthetic content (real person, real event, या realistic दिखने वाला scene) पर upload के समय "altered content" setting ज़रूरी। Disclose न करने पर YouTube खुद label लगा सकता है। | VERIFIED (official page) | https://support.google.com/youtube/answer/14328491 | 2026-10-21 |
| Inauthentic / reused content | YouTube | Mass-produced, template, बिना value-add वाला content monetize नहीं होता। AI as a tool allowed है। | REPORTED (पिछली research; official page इस बार नहीं पढ़ा) | https://support.google.com/youtube/answer/1311392 | 2026-10-18 |
| YPP eligibility | YouTube | अभी: 1,000 subs + 4,000 hrs/12 months **या** 1 करोड़ Shorts views/90 दिन। 1 Feb 2027 से नए applicants: 8,000 hrs या 2 करोड़ Shorts views। | REPORTED (Tubefilter); official blog में qualified views की परिभाषा | https://www.tubefilter.com/2026/08/10/youtube-partner-program-ad-eligibility-requirements-shorts/ · https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/ | 2026-10-21 |
| AI label (post) | Instagram | Industry signals वाले AI content पर "AI info" label; कुछ cases में label ज़रूरी। | VERIFIED (help page मौजूद) / details REPORTED | https://help.instagram.com/761121959519495 | 2026-10-21 |
| AI-generated profile label | Instagram | AI-generated person वाले account को profile पर "AI-generated profile" label लगाना होगा, नहीं तो recommendations से बाहर हो सकते हैं। | REPORTED (news, ~31 Aug) | freepressjournal.in; outlookbusiness.com | 2026-10-21 |
| Unoriginal content | Facebook | दूसरों का content बार-बार repost करने पर monetization और reach कम होती है; duplicate videos की distribution घटाई जाती है। | REPORTED (July 2025 announcement coverage) | https://www.tubefilter.com/2025/07/15/ai-slop-unoriginal-repetitive-content-monetization-facebook-meta/ | 2026-10-21 |
| Synthetic content labelling (India law) | सभी | IT Rules amendment notified 10 Feb 2026, effective 20 Feb 2026: synthetically generated information पर labelling और provenance। April 2026 draft (पूरे video में continuous label) का status UNKNOWN है। | REPORTED (law firms, newsonair) | https://www.hoganlovells.com/en/publications/india-introduces-mandatory-labelling-for-ai-and-3hour-takedown-for-illegal-content · https://ssrana.in/articles/india-tightens-oversight-on-ai-generated-content-under-it-rules/ | 2026-10-21 |
| Video length | YT / IG / FB | Shorts ≤ 3 min (Oct 2024 से)। IG Reels: 90s बनाम 3 min बनाम 20 min (CONFLICT; >3 min recommend नहीं होते)। FB Reels ≤ 90s (2025 source)। → **एक video के लिए ≤ 90s रखें।** | REPORTED / CONFLICT | argil.ai; kontentino.com; learn.headliner.app | 2026-10-21 |
| Branded / affiliate disclosure | सभी | ASCI influencer guidelines और platform के paid-partnership tools। | UNKNOWN (इस session में verify नहीं हुआ) | ascionline.in (check करें) | — |
| Music / voice / likeness | सभी | Platform की audio library या licensed music इस्तेमाल करें। असली लोगों की आवाज़ या चेहरा clone न करें। | INFERENCE + YouTube privacy guidelines | https://support.google.com/youtube/answer/7671399 | 2026-10-21 |

**ज़रूरी बात:** AI का इस्तेमाल अपने-आप न monetization की guarantee देता है, न उसे रोकता है। फ़ैसला originality, value-add और disclosure पर होता है।

---

## 8. Evidence ledger

| Claim | Direct URL | Source date | Access date | Status |
|---|---|---|---|---|
| ElevenLabs: Free 10k credits, no commercial; Starter $6/30k credits (commercial); Creator $22/121k, पहला महीना $11; annual = 10 महीने का भाव | https://elevenlabs.io/pricing | — | 2026-10-21 | Verified |
| Runway: Standard $15/625 credits ≈ 52s Gen-4.5 / 104s Gen-4 Turbo; Pro $35/2,250; Max $95/9,500; annual $12/$28/$76 | https://runwayml.com/pricing | — | 2026-10-21 | Verified |
| Claude Pro $20 monthly / $17 annual ($200 upfront) | https://claude.com/pricing | — | 2026-10-21 | Verified |
| ChatGPT Go ₹399, Plus ₹1,999 (India) | https://techcrunch.com/2025/08/18/openai-launches-a-sub-5-chatgpt-plan-in-india | 2025-08-18 | 2026-10-21 | Estimated (official page पर INR नहीं दिखा) |
| DaVinci Resolve free; Studio $236 (पहले $295) | https://www.blackmagicdesign.com/products/davinciresolve | — | 2026-10-21 | Verified |
| Wan 2.2 TI2V-5B: Apache 2.0, 720p 24fps 5s, ≥24GB VRAM, <9 min (official GPU पर) | https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B | — | 2026-10-21 | Verified |
| Wan 2.2 5B 12GB पर offloading से चलता है, ~10–15 min/clip | nextdiffusion.ai; civarchive.com (पिछली research) | — | 2026-10-18 | Estimated (Conflict with official) |
| Indic Parler-TTS: Apache 2.0, Hindi 107 hrs, NSS 83.4/84.8% | https://huggingface.co/ai4bharat/indic-parler-tts | — | 2026-10-21 | Verified |
| XTTS-v2 = Coqui Public Model License, non-commercial | https://huggingface.co/coqui/XTTS-v2 · https://bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models | — | 2026-10-21 | Verified (license name) / Estimated (non-commercial interpretation) |
| LatentSync: Apache-2.0; 8GB (1.5), 18GB (1.6) | https://github.com/bytedance/LatentSync | — | 2026-10-21 | Verified |
| MuseTalk: code MIT, model commercial OK; 8s ≈ 5 min on RTX 3050 Ti 4GB | https://github.com/TMElyralab/MuseTalk | — | 2026-10-21 | Verified |
| LM Studio work use free | https://lmstudio.ai/blog/free-for-work | — | 2026-10-21 | Verified |
| Whisper code + weights MIT | https://github.com/openai/whisper | — | 2026-10-21 | Verified |
| Whisper large-v3 Hindi WER 26.8% / 34.1 | https://benchmarklist.com/benchmarks/vaani_benchmark_v1/ · https://arxiv.org/pdf/2606.21408 | 2026 | 2026-10-21 | Conflict |
| ComfyUI license GPL-3.0; Ollama MIT | github.com/Comfy-Org/ComfyUI · github.com/ollama/ollama (LICENSE file मौजूद, नाम नहीं पढ़ा) | — | 2026-10-21 | Unknown (believed) |
| FLUX.1 schnell Apache 2.0; dev local outputs commercial unclear | https://help.bfl.ai/articles/9272590838-self-serve-dev-license-overview-pricing | — | 2026-10-21 | Conflict |
| Sarvam Bulbul v3 ₹30/10K chars, v2 ₹15; ₹1,000 free credits | https://docs.sarvam.ai/api/pricing | — | 2026-10-21 | Verified |
| HeyGen Creator $29, 600 credits (≈30 min Avatar IV) बनाम 200 credits/10 min | creatify.ai · eesel.ai · arcade.software | 2026 | 2026-10-21 | Conflict |
| Kling Standard ~$6.99 first / ~$8.80 renewal, 660 credits | https://www.eesel.ai/en/blog/kling-ai-pricing · https://www.cloudzero.com/blog/kling-ai-pricing/ | 2026 | 2026-10-21 | Estimated |
| USD/INR 94.46 – 96.52 | https://www.x-rates.com/calculator/?from=USD&to=INR&amount=1 · https://pluang.com/en/tools/currency-converter/usd-inr | timestamps अस्पष्ट | 2026-10-21 | Conflict |
| Maharashtra slabs ₹4.71–11.79/unit | https://www.voltflow.net/blog/electricity-rates-india-by-state-2026 | 2026-04-03 | 2026-10-21 | Estimated |
| RTX 3060 TGP 170W | https://www.kitguru.net/?p=500774 · notebookcheck.net | 2021 | 2026-10-21 | Verified (consistent) |
| YouTube AI disclosure rules | https://support.google.com/youtube/answer/14328491 | — | 2026-10-21 | Verified |
| YPP thresholds और Feb 2027 change | Tubefilter (ऊपर) · blog.youtube (ऊपर) | 2026-08-10/12 | 2026-10-21 | Estimated |
| Instagram AI-generated profile label | freepressjournal.in · help.instagram.com/761121959519495 | ~2026-08-31 | 2026-10-21 | Estimated |
| Meta unoriginal content rules | tubefilter.com 2025-07-15 | 2025-07 | 2026-10-21 | Estimated |
| India IT Rules SGI notified 10 Feb, effective 20 Feb 2026 | hoganlovells.com · ssrana.in · newsonair.gov.in | 2026 | 2026-10-21 | Estimated |
| "what if" IN 3,70,772/month; "facts in hindi" 18,024 | vidIQ keyword research (tool) | — | 2026-10-21 | Verified (tool data) |
| Competitor video numbers (section 3.2) | vidIQ trending + Nextlev (tool) | — | 2026-10-18 | Verified (tool data) |
| Cost model results | इस report का code (`cost_model.py`) | — | 2026-10-21 | Estimated (assumptions पर आधारित) |

### Tools actually used

| Tool | किस काम में | Limitation |
|---|---|---|
| vidIQ | Keyword demand (IN), trending Hindi Shorts, outliers | Search demand ≠ IG/YT reach; Hindi rising keywords का result खाली आया |
| Nextlev | नए fast-growing Shorts channels, viral small channels | India country filter ने 0 results दिए |
| Firecrawl | Official pricing और license pages पढ़ने के लिए | Rate limit; HeyGen और ChatGPT pages पर details नहीं मिलीं |
| Web search | Policies, secondary pricing, benchmarks | ज़्यादातर secondary sources |

### Tools not used

- **Exa, Tavily:** इस session में उपलब्ध नहीं थे।
- **Ahrefs, Semrush:** उपलब्ध थे, लेकिन web search demand को IG/YT का proof नहीं माना जाता, इसलिए skip किया।
- **Google Drive, Notion:** आपने कोई documents नहीं दिए थे।
- कोई private analytics इस्तेमाल नहीं हुआ।

---

## 9. Strategy handoff (अगले assistant के लिए)

| Item | Value |
|---|---|
| Proposed persona | एक recurring, नाम वाला AI host (gender test से तय होगा): "curious, मज़ेदार, fact-checked" what-if / अनोखे facts presenter। **Provisional, user-approved नहीं।** |
| Audience | 16–30, India first; Hinglish + Devanagari captions |
| Unique angle | VFX-quality what-if visuals + हर Short में source line + numbered series + साफ़ AI disclosure |
| Platforms | YouTube Shorts + Instagram Reels + Facebook Reels: **एक ही master video (≤ 90s),** बिना दूसरे app के watermark के; हर platform पर caption, title और cover अलग |
| Budget | ₹5,000/month; recommended stack C ≈ ₹1,640/month typical; बाकी buffer |
| Time | ~21 hrs/week assumed; C के लिए ~85 hrs/month चाहिए (tight) |
| Chosen stack | C Hybrid: ChatGPT Go (script) · Sarvam Bulbul v3 (voice) · ComfyUI + LoRA (character) · MuseTalk / LatentSync 1.5 (lip-sync) · Wan 2.2 5B + Kling Standard (video) · Resolve free + Whisper (edit/subs) · Meta Business Suite + YT Studio (schedule) |
| Constraints | XTTS-v2 commercial use नहीं; LatentSync 1.6 और 24GB models नहीं चलेंगे; FLUX.1 dev के local outputs का license confirm करें; India SGI labelling लागू है |
| Content opportunities | Section 3.1 की 5 audience problems; section 3.3 के 5 differentiation points |
| Before production starts | (1) Section 6 का benchmark चलाएँ (2) Voice और face test के बाद persona lock करें (3) Instagram profile label और YouTube disclosure की SOP बनाएँ (4) ASCI guidelines verify करें (5) Kling और HeyGen की official pricing verify करें |

### Uncertainty decisions पर कैसे असर डालती है

- **Wan 2.2 5B 3060 पर practical न निकले:** Kling पर ज़्यादा निर्भरता होगी, और C का खर्च ~₹3,000–4,000 तक जाएगा।
- **Sarvam की Hindi quality कमज़ोर निकले:** ElevenLabs Creator ($22 ≈ ₹2,090) लेना होगा, और C ≈ ₹3,500 होगा। फिर भी budget के अंदर रहेगा।
- **Local lip-sync quality कमज़ोर निकले:** HeyGen Creator ($29 ≈ ₹2,755) जोड़ना पड़ेगा, और C ≈ ₹4,400 होगा, जो budget के किनारे पर है। तब विकल्प है talking-head कम करके voiceover + visuals वाला format।

### Open questions (अधिकतम 5, high-impact)

1. हफ़्ते में असल में कितने घंटे दे सकते हो? 85 hrs/month का estimate आपके लिए realistic है?
2. पहले से कोई paid subscription है? (Adobe CC, ChatGPT, वगैरह)
3. Persona: इंसान जैसा realistic चेहरा चाहिए, या stylized/3D? Realistic होने पर Instagram profile label और लोगों का trust दोनों ज़्यादा sensitive होते हैं।
4. Monetization में पहले क्या चाहिए: ads, brand deals, या अपना digital product?
5. Long-form YouTube (8 videos/month) सच में करना है, या शुरुआत में सिर्फ़ Shorts/Reels? सिर्फ़ Shorts से खर्च और समय दोनों ~40% कम होंगे (INFERENCE)।
