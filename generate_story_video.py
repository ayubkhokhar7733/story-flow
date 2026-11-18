#!/usr/bin/env python3
"""
generate_story_video.py - Master Pipeline Script for YouTube Storytelling Video Generation.
"""
import sys
import io

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import argparse
import os
import time

from core.script_engine import generate_story_script
from core.image_engine import generate_scene_images
from core.tts_engine import generate_story_audio
from core.video_composer import compose_story_video
import config

def build_story_video(topic: str, duration: int = 60, voice: str = "christopher", aspect: str = "9:16") -> str:
    start_total = time.time()
    preset = config.ASPECT_PRESETS.get(aspect, config.ASPECT_PRESETS["9:16"])
    vw, vh = preset["width"], preset["height"]

    print("=" * 65, flush=True)
    print(f">> AI STORYTELLING CHANNEL VIDEO GENERATOR", flush=True)
    print(f"Topic:       {topic}", flush=True)
    print(f"Duration:    ~{duration} seconds", flush=True)
    print(f"Format:      {aspect} ({vw}x{vh})", flush=True)
    print(f"Voice:       {voice}", flush=True)
    print("=" * 65, flush=True)

    # 1. Script Generation
    print("\n[Step 1/4] Writing scene-by-scene cartoon story script...", flush=True)
    story = generate_story_script(topic, target_seconds=duration)
    scenes = story.get("scenes", [])
    title = story.get("title", topic)

    print(f"Title: '{title}'", flush=True)
    print(f"Main Character: {story.get('character_anchor', 'Custom character')}", flush=True)
    print(f"Total Scenes: {len(scenes)}", flush=True)

    for sc in scenes:
        print(f"   Scene {sc['scene_id']}: \"{sc['narration'][:70]}...\"", flush=True)

    # 2. Scene-by-Scene Cartoon Image Generation (AI Horde)
    print(f"\n[Step 2/4] Generating cartoon artwork on AI Horde GPU cluster [{aspect}]...", flush=True)
    scenes = generate_scene_images(scenes, aspect=aspect)

    # 3. Audio Narration & Subtitle Generation (Edge-TTS)
    print("\n[Step 3/4] Synthesizing neural voiceover & synchronized subtitles...", flush=True)
    audio_path, srt_path, actual_duration, scenes = generate_story_audio(scenes, voice_name=voice)

    # 4. Final Video Assembly with Ken Burns & Music Ducking
    print(f"\n[Step 4/4] Assembling {aspect} video ({vw}x{vh}) with Ken Burns motion & subtitles...", flush=True)
    output_video_path = compose_story_video(
        scenes=scenes,
        audio_path=audio_path,
        srt_path=srt_path,
        title=title,
        aspect=aspect
    )

    elapsed = round(time.time() - start_total, 1)
    file_size_mb = os.path.getsize(output_video_path) / (1024 * 1024)

    print("\n" + "=" * 65, flush=True)
    print(f"SUCCESS: Story video generated in {elapsed}s!", flush=True)
    print(f"Output File: {output_video_path}", flush=True)
    print(f"Video Specs: {vw}x{vh} ({aspect}), {actual_duration:.1f}s, {file_size_mb:.2f} MB", flush=True)
    print("=" * 65, flush=True)

    return output_video_path


def main():
    parser = argparse.ArgumentParser(description="AI Storytelling Video Generator")
    parser.add_argument("--topic", "-t", type=str, default="The Mysterious Watch That Froze Raindrops", help="Story topic or prompt")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Target duration in seconds (default: 60 for 1-minute test)")
    parser.add_argument("--voice", "-v", type=str, default="christopher", choices=list(config.VALID_VOICES.keys()), help="Voice narrator")
    parser.add_argument("--aspect", "-a", type=str, default="9:16", choices=["9:16", "16:9"], help="Video aspect ratio: 9:16 (Shorts/Reels) or 16:9 (Landscape)")

    args = parser.parse_args()

    try:
        build_story_video(topic=args.topic, duration=args.duration, voice=args.voice, aspect=args.aspect)
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
