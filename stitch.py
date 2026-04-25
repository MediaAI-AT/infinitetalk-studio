#!/usr/bin/env python3
"""
Stitch downloaded InfiniteTalk parts into a single MP4 using Remotion.
Uses MP3 audio durations (from ElevenLabs) to calculate frame counts.

Usage:
  python stitch.py --script 1     # stitch script "1"
  python stitch.py                # stitch all completed scripts
"""

import os
import sys
import json
import math
import shutil
import struct
import subprocess
import argparse
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

try:
    from mutagen.mp3 import MP3
except ImportError:
    print("[ERROR] mutagen not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

STATE_FILE = "state.json"
REMOTION_DIR = Path("remotion")
REMOTION_PUBLIC = REMOTION_DIR / "public"
OUTPUT_FINAL = Path("output/final")
FPS = 30


def load_state():
    if not Path(STATE_FILE).exists():
        print("[ERROR] state.json not found. Run generate.py first.")
        sys.exit(1)
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_audio_duration_frames(script_key, part_num):
    """Read MP3 duration and convert to frames at 30fps."""
    audio_path = Path(f"output/audio/{script_key}-part-{part_num}.mp3")
    if not audio_path.exists():
        return None
    try:
        duration = MP3(audio_path).info.length
        return math.ceil(duration * FPS)
    except Exception:
        return None


def get_image_dimensions(image_path):
    """Read JPEG/PNG dimensions without Pillow."""
    path = Path(image_path)
    if not path.exists():
        return None, None
    data = path.read_bytes()
    # JPEG
    if data[:2] == b'\xff\xd8':
        pos = 2
        while pos < len(data) - 9:
            if data[pos] == 0xff and data[pos+1] in (0xc0, 0xc1, 0xc2):
                h = struct.unpack('>H', data[pos+5:pos+7])[0]
                w = struct.unpack('>H', data[pos+7:pos+9])[0]
                return w, h
            pos += 1
    # PNG
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        w = struct.unpack('>I', data[16:20])[0]
        h = struct.unpack('>I', data[20:24])[0]
        return w, h
    return None, None


def get_remotion_dimensions(config, script_key):
    """Return (width, height) for Remotion based on image aspect ratio."""
    script_cfg = config.get("scripts", {}).get(str(script_key), {})
    image_path = script_cfg.get("image") or config.get("image", "")
    w, h = get_image_dimensions(image_path)
    if w and h and h > w:
        # Portrait (9:16 or similar) -> 720x1280
        return 720, 1280
    # Landscape default
    return 1280, 720


def stitch_script(script_key, state, config=None):
    script_state = state["scripts"].get(str(script_key))
    if not script_state:
        print(f"[ERROR] Script '{script_key}' not found in state.json")
        return

    chunks = script_state.get("chunks", [])
    done_parts = sorted(
        [c for c in chunks if c["download"] == "DONE"],
        key=lambda c: c["part"]
    )

    if not done_parts:
        print(f"Script {script_key}: No downloaded parts yet.")
        return

    title = script_state.get("title", script_key)
    print(f"\n=== Stitching Script {script_key}: {title} ===")
    print(f"  {len(done_parts)} part(s)")

    # Collect video paths and durations
    video_files = []
    durations_in_frames = []

    for c in done_parts:
        part_num = c["part"]
        video_path = Path(f"output/videos/{script_key}-part-{part_num}.mp4")
        if not video_path.exists():
            print(f"  [WARN] Missing: {video_path} — skipping")
            continue

        frames = get_audio_duration_frames(script_key, part_num)
        if frames is None:
            print(f"  [WARN] No audio for part {part_num}, estimating 90 frames")
            frames = 90

        video_files.append(video_path)
        durations_in_frames.append(frames)
        print(f"  Part {part_num}: {video_path.name} ({frames/FPS:.1f}s -> {frames} frames)")

    if not video_files:
        print("  No valid video files found.")
        return

    if len(video_files) == 1:
        OUTPUT_FINAL.mkdir(parents=True, exist_ok=True)
        out = OUTPUT_FINAL / f"{script_key}-final.mp4"
        shutil.copy(video_files[0], out)
        print(f"  Only 1 part — copied to {out}")
        return

    # Copy videos to remotion/public/
    REMOTION_PUBLIC.mkdir(parents=True, exist_ok=True)
    public_names = []
    for vf in video_files:
        dest = REMOTION_PUBLIC / vf.name
        shutil.copy(vf, dest)
        public_names.append(vf.name)

    # Build output path (absolute)
    OUTPUT_FINAL.mkdir(parents=True, exist_ok=True)
    output_path = (OUTPUT_FINAL / f"{script_key}-final.mp4").resolve()

    # Detect dimensions from image
    width, height = get_remotion_dimensions(config or {}, script_key)
    print(f"  Format: {width}x{height} ({'portrait' if height > width else 'landscape'})")

    # Build props for Remotion
    props = json.dumps({
        "parts": public_names,
        "partDurationsInFrames": durations_in_frames,
        "width": width,
        "height": height,
    })

    print(f"\n  Rendering with Remotion -> {output_path}")
    print(f"  Total: ~{sum(durations_in_frames)/FPS:.1f}s")

    npx = "npx.cmd" if os.name == "nt" else "npx"
    result = subprocess.run(
        [
            npx, "remotion", "render",
            "src/index.ts",
            "Stitcher",
            "--props", props,
            "--output", str(output_path),
        ],
        cwd=str(REMOTION_DIR.resolve()),
    )

    if result.returncode == 0:
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"\n  Done: {output_path} ({size_mb:.1f} MB)")
    else:
        print(f"\n  [ERROR] Remotion render failed (exit code {result.returncode})")


def main():
    parser = argparse.ArgumentParser(description="Stitch InfiniteTalk parts with Remotion")
    parser.add_argument("--script", type=str, help="Script key to stitch (e.g. '1')")
    args = parser.parse_args()

    state = load_state()
    config = json.loads(Path("config.json").read_text(encoding="utf-8")) if Path("config.json").exists() else {}
    scripts = [args.script] if args.script else list(state["scripts"].keys())

    for script_key in scripts:
        stitch_script(script_key, state, config=config)


if __name__ == "__main__":
    main()
