# InfiniteTalk Studio

Automated pipeline to turn text scripts into talking avatar videos — powered by **ElevenLabs** (TTS) + **WaveSpeed InfiniteTalk** (avatar video) + **Remotion** (stitching).

```
Text Script → ElevenLabs Audio → WaveSpeed Avatar Video → Remotion Final MP4
```

All parts are processed **fully in parallel** for maximum speed.

---

## Features

- 🎙️ **ElevenLabs v3** — high-quality multilingual TTS with natural pacing
- 🎬 **WaveSpeed InfiniteTalk** — 720p talking avatar video from image + audio
- 🎞️ **Remotion** — stitch all parts into one final MP4 with crossfade transitions
- ⚡ **Parallel processing** — audio generation, WaveSpeed submit and polling all run simultaneously
- 🔁 **Resume support** — interrupted pipelines continue from where they left off
- 📐 **Portrait & Landscape** — auto-detects 9:16 or 16:9 from your reference image
- 🎨 **B-Roll compositions** — animated motion graphics via Remotion
- 🎛️ **Per-script config** — different image, voice, format and enhance settings per script

---

## Requirements

- Python 3.10+
- Node.js 18+
- ElevenLabs API key (Creator Plan recommended)
- WaveSpeed API key

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/MediaAI-AT/infinitetalk-studio.git
cd infinitetalk-studio
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**3. Install Remotion dependencies**
```bash
cd remotion && npm install && cd ..
```

**4. Add your API keys**
```bash
cp .env.example .env
# Edit .env and add your keys
```

**5. Add your reference image**
```
images/avatar.jpg   ← your photo here
```

**6. Write your script**
```
scripts/my-script.txt
```

**7. Register it in config.json**
```json
"scripts": {
  "1": {
    "title": "My Video",
    "file": "scripts/my-script.txt"
  }
}
```

---

## Usage

```bash
# Dry run — check chunk split, no API calls
python generate.py --script 1 --dry-run

# Generate audio only (listen before spending on video)
python generate.py --script 1 --audio-only

# Full pipeline — audio + video
python generate.py --script 1

# Stitch all parts into final MP4
python stitch.py --script 1

# Check progress
python generate.py --status
```

---

## Config Options

```json
{
  "image": "images/avatar.jpg",
  "voice": {
    "id": "YOUR_ELEVENLABS_VOICE_ID",
    "settings": {
      "stability": 0.40,
      "similarity_boost": 0.75,
      "style": 0.00,
      "use_speaker_boost": true,
      "speed": 0.90
    }
  },
  "pipeline": {
    "max_chunk_words": 100,
    "max_audio_duration_sec": 55,
    "concurrent_limit": 5,
    "resolution": "720p"
  },
  "scripts": {
    "1": {
      "title": "My Video",
      "file": "scripts/my-script.txt",
      "image": "images/custom.jpg",
      "voice_id": "OPTIONAL_OVERRIDE",
      "format": "9:16",
      "enhance": true
    }
  }
}
```

| Option | Description |
|--------|-------------|
| `image` | Reference image for avatar (jpg/png/webp) |
| `voice.id` | ElevenLabs Voice ID |
| `voice.settings.speed` | Speech speed (0.85–1.0 recommended) |
| `pipeline.max_chunk_words` | Max words per chunk (~100 = ~45s) |
| `pipeline.resolution` | `480p` or `720p` |
| `scripts.*.enhance` | `true` = ElevenLabs text normalization on |
| `scripts.*.format` | `9:16` portrait or `16:9` landscape |

---

## Costs

| Service | Cost |
|---------|------|
| WaveSpeed InfiniteTalk 720p | ~$1.20 / 20 sec video |
| ElevenLabs Creator Plan | $22/month for 100 min audio |

A typical 5-minute video (6 chunks) costs approximately **$18–22** in WaveSpeed credits.

---

## Output Structure

```
output/
├── audio/        ← generated MP3 files per chunk
├── videos/       ← individual MP4 parts
└── final/        ← stitched final MP4
```

---

## Remotion Compositions

| Composition | Description |
|-------------|-------------|
| `Stitcher` | Combines video parts with crossfade transitions |
| `BRoll` | Animated motion graphics (tech/AI aesthetic) |
| `CombinedVideo` | Main video + B-Roll overlays at timed intervals |

---

## Built With

- [ElevenLabs](https://elevenlabs.io) — Text to Speech
- [WaveSpeed AI](https://wavespeed.ai) — InfiniteTalk avatar video
- [Remotion](https://remotion.dev) — Programmatic video rendering

---

## License

MIT
