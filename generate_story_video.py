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
from core.character_engine import character_engine
import config

def build_story_video(
    topic: str,
    duration: int = 60,
    voice: str = "christopher",
    aspect: str = "9:16",
    character: str = None,
    upload_youtube: bool = False,
    privacy: str = "unlisted"
) -> str:
    start_total = time.time()
    preset = config.ASPECT_PRESETS.get(aspect, config.ASPECT_PRESETS["9:16"])
    vw, vh = preset["width"], preset["height"]

    char_data = character_engine.get_character(character) if character else None
    char_name = char_data.get("name", "Custom") if char_data else "None"

    # Automatically adapt voice to character if default voice was passed
    if character and voice == "christopher":
        vprofile = character_engine.get_voice_profile(character, language="en")
        char_vname = vprofile.get("voice", "").lower()
        if "guy" in char_vname:
            voice = "guy"
        elif "jenny" in char_vname:
            voice = "jenny"
        elif "eric" in char_vname:
            voice = "eric"
        elif "aria" in char_vname:
            voice = "aria"

    print("=" * 65, flush=True)
    print(f">> AI STORYTELLING CHANNEL VIDEO GENERATOR", flush=True)
    print(f"Topic:       {topic}", flush=True)
    print(f"Character:   {char_name} ({character or 'None'})", flush=True)
    print(f"Duration:    ~{duration} seconds", flush=True)
    print(f"Format:      {aspect} ({vw}x{vh})", flush=True)
    print(f"Voice:       {voice}", flush=True)
    print(f"YouTube:     {'Enabled (' + privacy + ')' if upload_youtube else 'Disabled'}", flush=True)
    print("=" * 65, flush=True)

    # 1. Script Generation
    print("\n[Step 1/4] Writing scene-by-scene cartoon story script...", flush=True)
    story = generate_story_script(topic, target_seconds=duration, character_id=character)
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

    # 5. Direct YouTube Upload (if requested)
    if upload_youtube:
        print("\n[Step 5/5] Uploading generated video to YouTube channel...", flush=True)
        try:
            from core.youtube_uploader import upload_video
            desc = f"{title}\n\nGenerated with StoryFlow AI.\nFeaturing: {char_name}\n"
            yt_res = upload_video(
                video_path=output_video_path,
                title=title,
                description=desc,
                tags=["StoryFlow", "Animation", "AIStory", char_name.replace(" ", "")],
                privacy_status=privacy
            )
            print(f"🎬 Watch Live on YouTube: {yt_res['video_url']}", flush=True)
        except Exception as yt_err:
            print(f"⚠️ YouTube upload warning: {yt_err}", flush=True)

    return output_video_path


def main():
    parser = argparse.ArgumentParser(description="AI Storytelling Video Generator")
    parser.add_argument("--topic", "-t", type=str, default="The Mysterious Watch That Froze Raindrops", help="Story topic or prompt")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Target duration in seconds (default: 60 for 1-minute test)")
    parser.add_argument("--voice", "-v", type=str, default="christopher", choices=list(config.VALID_VOICES.keys()), help="Voice narrator")
    parser.add_argument("--aspect", "-a", type=str, default="9:16", choices=["9:16", "16:9"], help="Video aspect ratio: 9:16 (Shorts/Reels) or 16:9 (Landscape)")
    parser.add_argument("--character", "-c", type=str, default=None, choices=["chacha_bashir", "zainab_explorer", "raja_veer", "baba_fazal"], help="Registered character anchor")
    parser.add_argument("--upload-youtube", action="store_true", help="Directly upload rendered video to YouTube channel")
    parser.add_argument("--privacy", type=str, default="unlisted", choices=["private", "unlisted", "public"], help="YouTube privacy setting")

    args = parser.parse_args()

    try:
        build_story_video(
            topic=args.topic,
            duration=args.duration,
            voice=args.voice,
            aspect=args.aspect,
            character=args.character,
            upload_youtube=args.upload_youtube,
            privacy=args.privacy
        )
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
