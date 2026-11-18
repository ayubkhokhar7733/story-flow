"""
video_composer.py - High-performance FFmpeg video composer with Ken Burns motions, audio ducking, and subtitle burn-in.
Supports both 9:16 Vertical (Shorts/Reels) and 16:9 Landscape.
"""
import os
import re
import subprocess
import time
import config

def compose_story_video(scenes: list, audio_path: str, srt_path: str, title: str = "story_video", aspect: str = "9:16", output_filename: str = None) -> str:
    """
    Renders the complete storytelling video from scene images, voiceover, and subtitles.
    Supports aspect="9:16" (1080x1920) and aspect="16:9" (1920x1080).
    Returns the absolute path of the generated MP4.
    """
    preset = config.ASPECT_PRESETS.get(aspect, config.ASPECT_PRESETS["9:16"])
    target_w = preset["width"]
    target_h = preset["height"]
    font_size = preset["subtitle_font_size"]
    margin_v = preset["subtitle_margin_v"]

    print(f"\n[video_composer] Starting video composition for '{title}' [{aspect} -> {target_w}x{target_h}]...")
    total_scenes = len(scenes)

    # 1. Generate visual chunks for each scene with Ken Burns motion
    chunk_paths = []
    motions = ["zoom_in", "pan_left", "zoom_out", "pan_right"]

    for idx, scene in enumerate(scenes, 1):
        img_path = scene.get("image_path")
        if not img_path or not os.path.exists(img_path):
            raise FileNotFoundError(f"Missing image for scene {idx}: {img_path}")

        duration = scene.get("duration_sec", 6.0)
        motion = scene.get("camera_motion") or motions[(idx - 1) % len(motions)]
        chunk_file = os.path.join(config.TEMP_DIR, f"chunk_{idx}_{int(time.time())}.mp4")

        print(f"[video_composer] Rendering Scene {idx}/{total_scenes} ({duration:.1f}s, {motion})...")
        _render_ken_burns_chunk(img_path, duration, motion, chunk_file, target_w, target_h)
        chunk_paths.append(chunk_file)

    # 2. Concatenate all scene video chunks into a single visual track
    concat_list_path = os.path.join(config.TEMP_DIR, f"concat_list_{int(time.time())}.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for cp in chunk_paths:
            esc_path = os.path.abspath(cp).replace("\\", "/")
            f.write(f"file '{esc_path}'\n")

    visual_track_path = os.path.join(config.TEMP_DIR, "visual_track.mp4")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        visual_track_path
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    # 3. Prepare Audio & Subtitle Overlays for Final Render
    clean_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
    aspect_tag = "shorts_9x16" if aspect == "9:16" else "video_16x9"
    final_filename = output_filename or f"{clean_title[:25]}_{aspect_tag}_{int(time.time())}.mp4"
    final_output_path = os.path.join(config.OUTPUT_DIR, final_filename)

    music_path = os.path.join(config.MUSIC_DIR, "background.wav")
    has_music = os.path.exists(music_path)

    # Relative path for srt to avoid Windows drive colon escaping issues
    rel_srt = os.path.relpath(srt_path).replace("\\", "/")
    has_srt = os.path.exists(srt_path) and os.path.getsize(srt_path) > 10

    # Build FFmpeg command for final mix
    cmd = ["ffmpeg", "-y", "-i", visual_track_path, "-i", audio_path]

    filter_complex = []
    audio_map = "1:a"

    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", music_path])
        music_vol = config.MUSIC_VOLUME
        filter_complex.append(f"[2:a]volume={music_vol},afade=t=out:st=1000:d=2[bgm]")
        filter_complex.append(f"[1:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]")
        audio_map = "[aout]"

    # Video subtitle filter
    vf_filters = []
    if has_srt:
        sub_style = (
            f"FontName=Arial,FontSize={font_size},Bold=1,"
            "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
            f"BorderStyle=1,Outline=2.5,Shadow=1,Alignment=2,MarginV={margin_v}"
        )
        vf_filters.append(f"subtitles={rel_srt}:force_style='{sub_style}'")

    if vf_filters:
        cmd.extend(["-vf", ",".join(vf_filters)])

    if filter_complex:
        cmd.extend(["-filter_complex", ";".join(filter_complex)])

    cmd.extend([
        "-map", "0:v",
        "-map", audio_map,
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        final_output_path
    ])

    print("[video_composer] Encoding final high-definition MP4...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[video_composer] FFmpeg error: {res.stderr}")
        raise RuntimeError("FFmpeg final render failed.")

    # 4. Clean up temporary chunks
    _safe_delete(concat_list_path)
    _safe_delete(visual_track_path)
    for cp in chunk_paths:
        _safe_delete(cp)

    print(f"\n[SUCCESS] Video successfully exported to:\n{final_output_path}")
    return final_output_path


def _render_ken_burns_chunk(img_path: str, duration: float, motion: str, output_path: str, w: int = 1080, h: int = 1920):
    """
    Renders an image into a video clip with smooth Ken Burns motion scaled to w x h.
    """
    total_frames = max(30, int(duration * config.FPS))

    if motion == "zoom_out":
        z_expr = "max(1.15-0.0012*on,1.0)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        z_expr = "1.12"
        x_expr = "if(lte(on,1),(iw-iw/zoom)/2,max(x-1.5,0))"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        z_expr = "1.12"
        x_expr = "if(lte(on,1),0,min(x+1.5,(iw-iw/zoom)))"
        y_expr = "ih/2-(ih/zoom/2)"
    else:
        # Default: zoom_in
        z_expr = "min(zoom+0.0012,1.15)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},"
        f"zoompan=z='{z_expr}':d={total_frames}:x='{x_expr}':y='{y_expr}':s={w}x{h}:fps={config.FPS}"
    )

    cmd = [
        "ffmpeg", "-y", "-loop", "1",
        "-i", img_path,
        "-t", f"{duration:.3f}",
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg chunk render failed: {res.stderr.decode('utf-8', errors='ignore')}")


def _safe_delete(filepath: str):
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass
