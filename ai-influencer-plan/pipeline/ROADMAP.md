# Roadmap: Pipeline को आगे और ताक़तवर कैसे बनाएँ

**Research date:** 2026-10-21 · **Labels:** VERIFIED · REPORTED · INFERENCE

## Done
- **v2:** Safety gate · Auto QC · AI metadata + optional C2PA · disk guard + cleanup · daily report · idea bank · doctor · new-project · 15-platform registry · one-click setup
- **v3:** Benchmark mode · Whisper word-pop captions · Trend radar · Cover frame + IG thumb_offset · Weekly backup

## Next (priority order)

| # | Feature | क्यों | Research basis |
|---|---|---|---|
| 1 | **Hook A/B**: एक video के 2 hooks, बेहतर retention वाला अगली बार default | Data से सीखना | INFERENCE |
| 2 | **Multi-language dubbing**: Hindi master → English/Tamil/Telugu versions, अलग channels पर | Gen Z translated content देखता है (YouTube India report, REPORTED) | Sarvam 11 भाषाएँ (REPORTED) |
| 3 | **Postiz backend (optional)**: 28+ platforms का open-source scheduler, self-hosted, REST API | जब 5+ platforms API से चलाने हों | AGPL-3.0, Docker 4–8 GB RAM, v2.12+ में Temporal चाहिए (REPORTED: railway.com, mintlify docs) |
| 4 | **Comment reply drafts**: Telegram पर approve करके reply | Engagement | Human approval ज़रूरी (policy) |
| 5 | **Instagram Trial Reels via API**: नए formats पहले non-followers पर test | सुरक्षित experiments | API parameter अभी unverified (REPORTED) |
| 6 | **Media kit generator**: report data से brand deck | Phase 3 monetization | MASTER_PLAN §3 |
| 7 | **Long-form mode**: 5–8 min videos के लिए chapters के साथ | Report baseline में 8 long videos/month थे | Research report §5 |

## Design rules (इन्हें कभी न तोड़ें)
1. **Human approve step** हमेशा रहेगा (mass-produced content पर policy risk)।
2. **AI disclosure** हर जगह: file metadata, caption line, platform toggle, profile label।
3. **Secrets** सिर्फ़ environment variables में। Config या Git में कभी नहीं।
4. **हर नया feature** एक test के साथ आएगा: `python -m pytest -q tests`।
5. **Local first**, cloud सिर्फ़ जहाँ quality या समय में साफ़ फ़ायदा हो।

## Sources
- C2PA / c2patool: https://opensource.contentauthenticity.org/docs/sdk-repos/c2pa-rs/cli/docs/manifest · https://docs.amazonaws.cn/en_us/mediaconvert/latest/ug/c2pa-manifest-verification.html
- YouTube automatic AI labels + C2PA (May 2026, REPORTED): https://heise.de/-11309100 · https://c2paviewer.com/articles/youtube-ai-labels-c2pa
- Instagram और IPTC DigitalSourceType (REPORTED, older): https://iptc.org/news/ai-disclosure-on-social-media-a-work-in-progress/
- Ollama structured outputs: https://fossies.org/linux/ollama/docs/api.md
- FFmpeg QC pattern: https://dev.to/morinaga/four-pre-upload-video-checks-i-run-with-ffprobe-before-any-youtube-video-goes-live-423h
- Instagram insights "views" metric: https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/
- Postiz: https://railway.com/deploy/postiz-open-source-social-media-scheduler-for-30-platforms--deploy-postiz · https://www.mintlify.com/gitroomhq/postiz-app/self-hosting/overview
