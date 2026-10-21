# Cost model for 3 production stacks. All inputs are declared assumptions or sourced prices.
FX = 95.0            # INR per USD (planning rate; sources show 94.46-96.52, see report)
KWH = 8.0            # INR per kWh (assumption; Maharashtra mid-slab, Delhi lower)
SYS_KW = 0.35        # whole-PC draw under GPU load (assumption: RTX 3060 TGP 170W + CPU + rest)

# Baseline volume (declared assumptions)
REELS, LONG, LONG_OPT = 30, 8, 4
REEL_SEC, LONG_MIN = 30, 5
REEL_AVATAR_S, REEL_GEN_S = 15, 10     # seconds per Reel that must be AI-generated
LONG_AVATAR_S, LONG_GEN_S = 120, 60    # seconds per long video that must be AI-generated
CHARS_PER_MIN = 1000                   # TTS chars per spoken minute (assumption)
IMAGES = REELS*4 + LONG*20             # stills per month

def volumes(n_long):
    narr_min = (REELS*REEL_SEC)/60 + n_long*LONG_MIN
    avatar_min = (REELS*REEL_AVATAR_S + n_long*LONG_AVATAR_S)/60
    gen_sec = REELS*REEL_GEN_S + n_long*LONG_GEN_S
    return narr_min, avatar_min, gen_sec

RETRY = {"low": (1.1, 1.2, 1.5), "typical": (1.3, 1.5, 2.0), "high": (1.6, 2.0, 3.0)}  # tts, lipsync, video-gen

def local_hours(narr, avatar, gen, r):
    tts_h = narr*r[0]*1.0/60            # ~1 min compute per audio min (not tested)
    lip_h = avatar*r[1]*37/60           # MuseTalk README: 8s in ~5 min on 4GB laptop GPU -> ~37 min per min (upper bound)
    vid_h = (gen*r[2]/5)*12/60          # Wan2.2-5B offloaded: ~10-15 min per 5s clip (community reports)
    img_h = IMAGES*1.3*0.5/60           # ~30s per still incl. retries (not tested)
    return tts_h, lip_h, vid_h, img_h

def run(n_long, scen):
    narr, avatar, gen = volumes(n_long); r = RETRY[scen]
    out = {}
    # A: Local-first
    t = local_hours(narr, avatar, gen, r); gpu_h = sum(t)
    elec = gpu_h*SYS_KW*KWH
    out["A Local-first"] = dict(cash=399+elec, subs=399, elec=elec, gpu_h=gpu_h)
    # B: Paid-cloud-first
    tts_min = narr*r[0]
    el = 22 if tts_min <= 121 else 99                         # ElevenLabs Creator / Pro
    hey = 29 if avatar*r[1] <= 30 else 29 + (avatar*r[1]-30)/30*29   # HeyGen Creator ~30 min Avatar IV (REPORTED)
    gen_need = gen*r[2]
    rw = 15 if gen_need <= 104 else 35 if gen_need <= 375 else 95 if gen_need <= 1900 else 95*gen_need/1900  # Runway Gen-4 Turbo seconds
    usd = el + hey + rw
    out["B Paid-cloud-first"] = dict(cash=usd*FX + 1999, subs=usd*FX + 1999, elec=0, gpu_h=0, usd=usd)
    # C: Hybrid (cloud voice + local avatar/images + local video with cloud hero shots)
    sarvam = narr*r[0]*CHARS_PER_MIN/10000*30           # Bulbul v3 Rs30 per 10K chars
    t = local_hours(narr, avatar, gen*0.7, r)          # 70% of generated seconds local
    t = (0, t[1], t[2], t[3])                            # voice is cloud
    gpu_h = sum(t); elec = gpu_h*SYS_KW*KWH
    kling = 8.80*FX                                      # Kling Standard renewal (REPORTED) for 30% hero shots
    out["C Hybrid"] = dict(cash=399 + sarvam + kling + elec, subs=399 + kling, api=sarvam, elec=elec, gpu_h=gpu_h)
    return out, (narr, avatar, gen)

for n_long in (LONG, LONG + LONG_OPT):
    print(f"\n=== Baseline: {REELS} Reels + {n_long} long videos ===")
    for scen in RETRY:
        out, v = run(n_long, scen)
        print(f"-- {scen} retries | narration {v[0]:.1f} min, avatar {v[1]:.1f} min, generated {v[2]} s")
        for k, d in out.items():
            usable_min = v[0]  # usable finished narrated minutes
            print(f"   {k:20s} cash/month Rs {d['cash']:8.0f} | GPU hours {d['gpu_h']:6.1f} | elec Rs {d['elec']:5.0f}"
                  f" | per Reel-equivalent Rs {d['cash']/(REELS+n_long*10):6.1f} | per finished min Rs {d['cash']/usable_min:6.1f}")
