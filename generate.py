#!/usr/bin/env python3
"""
InfiniteTalk Pipeline — ElevenLabs + WaveSpeed InfiniteTalk
Converts a text script into a talking avatar video in segments.

Pipeline per chunk:
  1. Split script at sentence boundaries (max 100 words, ~55s audio)
  2. Generate speech via ElevenLabs TTS
  3. Submit image + audio to WaveSpeed InfiniteTalk (720p)
  4. Poll until complete, download MP4

Usage:
  python generate.py                   # Full pipeline (all scripts)
  python generate.py --dry-run         # Split only, no API calls
  python generate.py --script 1        # Process script key "1"
  python generate.py --max-parts 1     # Limit to 1 chunk (test)
  python generate.py --status          # Show pipeline progress
"""

import os
import sys
import json
import base64
import time
import argparse
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

try:
    import requests
except ImportError:
    print("[ERROR] requests not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from mutagen.mp3 import MP3
except ImportError:
    print("[ERROR] mutagen not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


CONFIG_FILE = "config.json"
STATE_FILE = "state.json"

WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

WAVESPEED_BASE = "https://api.wavespeed.ai/api/v3"
ELEVENLABS_BASE = "https://api.elevenlabs.io/v1"


# ─── Config ──────────────────────────────────────────────────────────────────

def load_config():
    if not Path(CONFIG_FILE).exists():
        print(f"[ERROR] {CONFIG_FILE} not found.")
        sys.exit(1)

    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    errors = []
    if not WAVESPEED_API_KEY:
        errors.append("Set WAVESPEED_API_KEY in .env")
    if not ELEVENLABS_API_KEY:
        errors.append("Set ELEVENLABS_API_KEY in .env")

    voice_id = config.get("voice", {}).get("id", "")
    if not voice_id or voice_id.startswith("YOUR_"):
        errors.append("Set voice.id in config.json")

    image_path = config.get("image", "")
    if not image_path or not Path(image_path).exists():
        errors.append(
            f"Image not found: '{image_path}' — "
            "place your photo in images/ and set 'image' in config.json"
        )

    if errors:
        print("[ERROR] Configuration issues:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    return config


# ─── State ───────────────────────────────────────────────────────────────────

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"scripts": {}}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ─── Script Splitting ─────────────────────────────────────────────────────────

def split_script(text, max_words=100):
    """Split text into chunks at sentence boundaries, max_words per chunk."""
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current = []
    current_count = 0

    for sentence in sentences:
        wc = len(sentence.split())
        if current_count + wc > max_words and current:
            chunks.append(" ".join(current).strip())
            current = [sentence]
            current_count = wc
        else:
            current.append(sentence)
            current_count += wc

    if current:
        chunks.append(" ".join(current).strip())

    return [c for c in chunks if c]


# ─── Audio Generation ─────────────────────────────────────────────────────────

def generate_audio(text, voice_id, voice_settings, output_path, enhance=True):
    """Generate speech via ElevenLabs TTS and save as MP3."""
    url = f"{ELEVENLABS_BASE}/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_v3",
        "voice_settings": voice_settings,
        "apply_text_normalization": "off" if not enhance else "auto",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs {resp.status_code}: {resp.text[:200]}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(resp.content)


def get_audio_duration(audio_path):
    """Return duration in seconds, or None on failure."""
    try:
        return MP3(audio_path).info.length
    except Exception:
        return None


# ─── File Encoding ────────────────────────────────────────────────────────────

def file_to_data_uri(file_path):
    """Encode a local file as a base64 data URI for API submission."""
    ext = Path(file_path).suffix.lower().lstrip(".")
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "m4a": "audio/mp4",
    }
    mime = mime_map.get(ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime};base64,{b64}"


# ─── WaveSpeed API ────────────────────────────────────────────────────────────

def submit_infinitetalk(image_data, audio_data, resolution="720p", prompt=None):
    """Submit image + audio to WaveSpeed InfiniteTalk. Returns response dict."""
    url = f"{WAVESPEED_BASE}/wavespeed-ai/infinitetalk"
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "image": image_data,
        "audio": audio_data,
        "resolution": resolution,
        "seed": -1,
    }
    if prompt:
        payload["prompt"] = prompt

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"WaveSpeed {resp.status_code}: {resp.text[:200]}")

    body = resp.json()
    # API wraps result in {"code":200, "data": {...}}
    return body.get("data", body)


def poll_status(prediction_id, get_url=None, timeout_sec=1200, interval_sec=15, part=None):
    """Poll WaveSpeed until status is 'completed' or 'failed'."""
    if get_url is None:
        get_url = f"{WAVESPEED_BASE}/predictions/{prediction_id}/result"

    label = f"Part {part}" if part else prediction_id[:8]
    headers = {"Authorization": f"Bearer {WAVESPEED_API_KEY}"}
    deadline = time.time() + timeout_sec

    while time.time() < deadline:
        resp = requests.get(get_url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Poll {resp.status_code}: {resp.text[:200]}")

        body = resp.json()
        data = body.get("data", body)
        status = data.get("status", "unknown")

        if status == "completed":
            return data
        elif status == "failed":
            raise RuntimeError(f"Job failed: {json.dumps(data)[:200]}")

        print(f"  [{label}] {status} — waiting {interval_sec}s...")
        time.sleep(interval_sec)

    raise RuntimeError(f"Timeout after {timeout_sec}s for prediction {prediction_id}")


def download_video(url, output_path):
    """Download a video from URL to a local file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=180, stream=True)
    if resp.status_code != 200:
        raise RuntimeError(f"Download {resp.status_code}")

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)


# ─── Pipeline ────────────────────────────────────────────────────────────────

def process_script(script_key, config, state, dry_run=False, max_parts=None, audio_only=False):
    script_cfg = config["scripts"].get(str(script_key))
    if not script_cfg:
        print(f"[ERROR] Script '{script_key}' not in config.json")
        return

    title = script_cfg["title"]
    script_file = script_cfg["file"]
    print(f"\n=== Script {script_key}: {title} ===")

    if not Path(script_file).exists():
        print(f"[ERROR] File not found: {script_file}")
        return

    text = Path(script_file).read_text(encoding="utf-8").strip()
    max_words = config["pipeline"].get("max_chunk_words", 100)
    max_duration = config["pipeline"].get("max_audio_duration_sec", 55)
    concurrent_limit = config["pipeline"].get("concurrent_limit", 6)

    chunks = split_script(text, max_words=max_words)
    if max_parts:
        chunks = chunks[:max_parts]

    print(f"  {len(chunks)} chunk(s) | {len(text.split())} total words")

    # Save split scripts to disk
    for i, chunk in enumerate(chunks, 1):
        path = f"output/scripts/{script_key}-part-{i}.txt"
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(chunk, encoding="utf-8")
        print(f"  Part {i}: {len(chunk.split())} words")

    if dry_run:
        print("  [dry-run] Skipping API calls.")
        return

    # Initialize state
    if script_key not in state["scripts"]:
        state["scripts"][script_key] = {"title": title, "chunks": []}

    chunk_states = state["scripts"][script_key]["chunks"]
    while len(chunk_states) < len(chunks):
        chunk_states.append({
            "part": len(chunk_states) + 1,
            "audio": "PENDING",
            "submit": "PENDING",
            "prediction_id": None,
            "poll_url": None,
            "download": "PENDING",
            "error": None,
        })
    save_state(state)

    # Script-level overrides take priority over global config
    voice_id = script_cfg.get("voice_id") or config["voice"]["id"]
    voice_settings = config["voice"].get("settings", {})
    resolution = config["pipeline"].get("resolution", "720p")
    image_path = script_cfg.get("image") or config["image"]
    enhance = script_cfg.get("enhance", True)  # False = disable ElevenLabs text normalization

    print(f"\n  Encoding image: {image_path}")
    image_data = file_to_data_uri(image_path)

    state_lock = threading.Lock()

    def save_locked():
        with state_lock:
            save_state(state)

    # ── Phase 1: Generate all audio in parallel ───────────────────────────────
    print(f"\n  Phase 1 — Generating {len(chunks)} audio file(s) in parallel...")

    def generate_audio_chunk(i):
        cs = chunk_states[i]
        part = i + 1
        if cs["audio"] == "DONE":
            print(f"  [Part {part}] audio already done, skipping")
            return
        audio_path = f"output/audio/{script_key}-part-{part}.mp3"
        print(f"  [Part {part}] generating audio...")
        try:
            generate_audio(chunks[i], voice_id, voice_settings, audio_path, enhance=enhance)
            duration = get_audio_duration(audio_path)
            if duration:
                flag = " ⚠ exceeds limit!" if duration > max_duration else ""
                print(f"  [Part {part}] audio ready: {duration:.1f}s{flag}")
            with state_lock:
                cs["audio"] = "DONE"
                save_state(state)
        except Exception as e:
            with state_lock:
                cs["audio"] = "FAILED"
                cs["error"] = str(e)
                save_state(state)
            print(f"  [Part {part}] audio ERROR: {e}")

    with ThreadPoolExecutor(max_workers=concurrent_limit) as ex:
        futures = [ex.submit(generate_audio_chunk, i) for i in range(len(chunks))]
        for f in as_completed(futures):
            f.result()  # surface exceptions

    audio_ok = [i for i in range(len(chunks)) if chunk_states[i]["audio"] == "DONE"]
    print(f"\n  Phase 1 done: {len(audio_ok)}/{len(chunks)} audio files ready")

    if audio_only:
        print("  [audio-only] Stopping after Phase 1.")
        return

    # ── Phase 2: Submit all to WaveSpeed in parallel ──────────────────────────
    print(f"\n  Phase 2 — Submitting {len(audio_ok)} job(s) to WaveSpeed in parallel...")

    def submit_chunk(i):
        cs = chunk_states[i]
        part = i + 1
        if cs["submit"] == "DONE":
            print(f"  [Part {part}] already submitted ({cs['prediction_id']})")
            return
        audio_path = f"output/audio/{script_key}-part-{part}.mp3"
        print(f"  [Part {part}] submitting to WaveSpeed...")
        try:
            audio_data = file_to_data_uri(audio_path)
            result = submit_infinitetalk(image_data, audio_data, resolution=resolution)
            with state_lock:
                cs["prediction_id"] = result.get("id")
                cs["poll_url"] = result.get("urls", {}).get("get")
                cs["submit"] = "DONE"
                save_state(state)
            print(f"  [Part {part}] submitted -> {cs['prediction_id']}")
        except Exception as e:
            with state_lock:
                cs["submit"] = "FAILED"
                cs["error"] = str(e)
                save_state(state)
            print(f"  [Part {part}] submit ERROR: {e}")

    with ThreadPoolExecutor(max_workers=concurrent_limit) as ex:
        futures = [ex.submit(submit_chunk, i) for i in audio_ok]
        for f in as_completed(futures):
            f.result()

    submit_ok = [i for i in audio_ok if chunk_states[i]["submit"] == "DONE"]
    print(f"\n  Phase 2 done: {len(submit_ok)}/{len(chunks)} jobs submitted")

    # ── Phase 3: Poll & download all in parallel ──────────────────────────────
    print(f"\n  Phase 3 — Polling & downloading {len(submit_ok)} video(s) in parallel...")
    print(f"  (720p render time varies by load — updates appear as each part finishes)\n")

    def poll_and_download_chunk(i):
        cs = chunk_states[i]
        part = i + 1
        if cs["download"] == "DONE":
            print(f"  [Part {part}] already downloaded")
            return
        video_path = f"output/videos/{script_key}-part-{part}.mp4"
        try:
            final = poll_status(
                cs["prediction_id"],
                get_url=cs.get("poll_url"),
                part=part,
            )
            outputs = final.get("outputs", [])
            if not outputs:
                raise RuntimeError("No output URL in completed response")
            print(f"  [Part {part}] downloading video...")
            download_video(outputs[0], video_path)
            with state_lock:
                cs["download"] = "DONE"
                save_state(state)
            print(f"  [Part {part}] saved: {video_path}")
        except Exception as e:
            with state_lock:
                cs["download"] = "FAILED"
                cs["error"] = str(e)
                save_state(state)
            print(f"  [Part {part}] download ERROR: {e}")

    with ThreadPoolExecutor(max_workers=concurrent_limit) as ex:
        futures = [ex.submit(poll_and_download_chunk, i) for i in submit_ok]
        for f in as_completed(futures):
            f.result()

    done = sum(1 for c in chunk_states[:len(chunks)] if c["download"] == "DONE")
    print(f"\n  All done: {done}/{len(chunks)} parts in output/videos/")


# ─── Status Display ───────────────────────────────────────────────────────────

def show_status(state, config):
    if not state["scripts"]:
        print("No runs yet. Execute without --status to start the pipeline.")
        return

    for key, script_state in state["scripts"].items():
        title = script_state.get("title", key)
        chunks = script_state.get("chunks", [])
        done = sum(1 for c in chunks if c["download"] == "DONE")
        print(f"\nScript {key}: {title}  ({done}/{len(chunks)} downloaded)")
        print(f"  {'Part':<6} {'Audio':<8} {'Submit':<8} {'Video':<8}  Error")
        print(f"  {'─'*60}")
        for c in chunks:
            err = (c.get("error") or "")[:45]
            print(f"  {c['part']:<6} {c['audio']:<8} {c['submit']:<8} {c['download']:<8}  {err}")


# ─── Entry Point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="InfiniteTalk Pipeline")
    parser.add_argument("--dry-run", action="store_true",
                        help="Split scripts only, no API calls")
    parser.add_argument("--script", type=str,
                        help="Process a specific script key (e.g. '1')")
    parser.add_argument("--max-parts", type=int,
                        help="Limit chunks per script (for testing)")
    parser.add_argument("--status", action="store_true",
                        help="Show pipeline progress")
    parser.add_argument("--audio-only", action="store_true",
                        help="Generate audio only, skip WaveSpeed")
    args = parser.parse_args()

    config = load_config()
    state = load_state()

    if args.status:
        show_status(state, config)
        return

    scripts_to_run = [args.script] if args.script else list(config["scripts"].keys())

    for script_key in scripts_to_run:
        process_script(
            script_key,
            config,
            state,
            dry_run=args.dry_run,
            max_parts=args.max_parts,
            audio_only=args.audio_only,
        )


if __name__ == "__main__":
    main()
