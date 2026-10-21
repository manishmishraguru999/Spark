# Platforms: Research और Pipeline Support

- **Research date:** 2026-10-21
- **Labels:** VERIFIED (official doc) · REPORTED (secondary) · UNKNOWN
- **Rule:** एक ही master video (≤ 90s) सभी platforms पर। हर platform के लिए caption, hashtags और limits अपने-आप adjust होते हैं (`beast/publish/registry.py`)।

## 1. Support table

| Platform | Pipeline में | API status | Video limit | Caption / hashtags | ज़रूरी बातें | Source |
|---|---|---|---|---|---|---|
| **YouTube Shorts** | ✅ plugin (manual + API) | Ready; बिना audit वाले project से upload private-locked रहता है | ≤ 3 min | 5000 / 3 | `containsSyntheticMedia` | VERIFIED: developers.google.com/youtube/v3 |
| **Instagram Reels** | ✅ plugin | Ready (Instagram Login, own account dev mode) | Feed में ≤ 3 min recommend | 2200 / 5 | 100 posts/24h (पुराने docs: 50) | VERIFIED: developers.facebook.com content-publishing |
| **Facebook Reels** | ✅ plugin | Ready (`video_reels`) | **3–90 s** | 5000 / 5 | 30 API reels/24h | VERIFIED: Meta Reels Publishing guide |
| **Threads** | ✅ plugin (default manual) | API है, लेकिन video **public URL** से fetch होता है | ≤ 5 min (REPORTED) | 500 / 1 | 250 posts/24h | VERIFIED: developers.facebook.com/documentation/threads/posts |
| **Pinterest** | ✅ plugin | Ready (register → S3 upload → status → pin); trial app सिर्फ़ अपने account पर | ≤ 5 min (INFERENCE) | 500 / 5 | Cover frame; 401 issue reported | REPORTED: bundle.social, postproxy.dev, community.pinterest.biz |
| **Telegram Channel** | ✅ plugin | Ready (Bot API) | 50 MB bot limit | 1024 / 5 | Bot को channel admin बनाएँ | INFERENCE (Bot API) |
| **X (Twitter)** | 📲 manual | **Paid:** free tier नए projects के लिए 6 Feb 2026 से बंद; pay-per-use (~$0.015/post, link वाले post ~$0.20) | ≤ 2:20 (INFERENCE) | 280 / 2 | Media upload के लिए OAuth 1.0a चाहिए | REPORTED: socialcrawl.dev, postproxy.dev, opentweet.io |
| **Bluesky** | 📲 manual (plugin बाकी) | Video API है | ≤ 10 min, 300 MB (Aug 2026) | 300 / 3 | Video service auth अलग है | REPORTED: engadget.com, opentweet.io |
| **Snapchat Spotlight** | 📲 manual | Public Profile API: सिर्फ़ Business account | ≤ 60 s, 32 MB (REPORTED) | 160 / 3 | Ads Manager organization चाहिए | REPORTED: ayrshare.com, zernio.com |
| **Moj / ShareChat / Josh** | 📲 manual | **कोई public API नहीं मिला** | ~60 s (INFERENCE) | 500 / 5 | Indian audience के लिए अच्छे | UNKNOWN (search में कुछ नहीं मिला) |
| **WhatsApp Channel** | 📲 manual | Channel posting API नहीं मिला | ~90 s (INFERENCE) | 1000 / 0 | Phone से forward करें | UNKNOWN |
| **LinkedIn** | 📲 manual | API है (plugin नहीं बनाया) | — | 3000 / 3 | 16–30 entertainment के लिए कम fit | INFERENCE |
| **TikTok** | ⛔ blocked | **India में June 2020 से banned**; Aug 2025 में सरकार और TikTok दोनों ने confirm किया | — | — | Enable करने पर error आएगा | REPORTED: techcrunch.com (2025-08-22), storyboard18.com |

**📲 manual का मतलब:** video और उस platform के हिसाब से बना caption `05_published/manual/<platform>/` में आ जाएगा, और phone पर checklist आएगी। Folder को phone पर sync करें, फिर app से 1 मिनट में post करें।

## 2. Priority (16–30, India) — INFERENCE

1. **YouTube Shorts + Instagram Reels + Facebook Reels** (पहले से)
2. **Moj / ShareChat / Josh:** Hindi audience बड़ी है, लेकिन API नहीं है, इसलिए manual
3. **Snapchat Spotlight:** India में Gen Z के बीच popular (INFERENCE)। Business account बनने के बाद plugin
4. **Threads / X / Telegram Channel / WhatsApp Channel:** community और repeat viewers के लिए
5. **Pinterest / Bluesky / LinkedIn:** कम priority

## 3. नया platform कैसे जोड़ें (developer guide)

1. `beast/publish/registry.py` में `PLATFORMS` dict के अंदर एक `Spec` जोड़ें:
   ```python
   "newplat": Spec("New Platform", max_seconds=90, max_caption=1000, max_hashtags=3, api="ready", notes="..."),
   ```
2. **API नहीं है?** कुछ और मत लिखें। Manual hand-off अपने-आप काम करेगा।
3. **API है?** `beast/publish/plugins.py` में यह function लिखें:
   ```python
   def publish_newplat(ctx: PublishContext) -> dict:
       # ctx.video, ctx.formatted_caption(), ctx.title, ctx.cfg (config section)
       ...
       return {"platform": "newplat", "id": "...", "url": "..."}
   ```
   HTTP के लिए `_http()` इस्तेमाल करें, ताकि tests में fake session डाला जा सके।
4. `config.yaml` में section जोड़ें:
   ```yaml
   publish:
     newplat:
       enabled: true
       mode: manual      # API तैयार होने तक
   ```
5. `tests/test_platforms.py` में एक fake-session test लिखें, फिर `python -m pytest -q tests` चलाएँ।

## 4. अपने-आप होने वाली safety checks

- **Video length:** platform limit से लंबी video उस platform पर skip होती है और phone पर सूचना आती है। उदाहरण: 95s video Facebook पर नहीं जाएगी।
- **Caption:** हर platform की character और hashtag limit के हिसाब से अपने-आप छोटा होता है।
- **Disclosure line:** हर caption में `publish.disclosure_line` जुड़ता है।
- **Blocked platform (TikTok):** enable करने पर error आता है, कुछ post नहीं होता।
- **Partial publish:** अगर एक platform fail हो, तो बाकी platforms दोबारा post नहीं होते। सिर्फ़ fail वाला 10 मिनट बाद retry होता है (अधिकतम 3 बार)।

## Sources
- TikTok India: https://techcrunch.com/2025/08/22/tiktok-denies-india-comeback-after-reports-of-website-going-live · https://www.storyboard18.com/brand-makers/tiktok-ban-in-india-still-stands-company-clarifies-after-brief-website-access-79505.htm
- X API pricing: https://www.socialcrawl.dev/blog/x-twitter-api-2026 · https://postproxy.dev/blog/x-api-pricing-2026
- Threads: https://developers.facebook.com/documentation/threads/posts
- Pinterest: https://bundle.social/blog/pinterest-pin-api · https://postproxy.dev/blog/pinterest-api-posting-integration-guide/
- Bluesky: https://engadget.com/2244638/bluesky-now-supports-10-minute-videos-larger-file-sizes/ · https://opentweet.io/tools/bluesky-video-checker
- Snapchat: https://www.ayrshare.com/docs/apis/post/social-networks/snapchat · https://zernio.com/snapchat-api
- Facebook Reels: https://developers.facebook.com/docs/video-api/guides/reels-publishing
- Instagram: https://developers.facebook.com/docs/instagram-platform/content-publishing
