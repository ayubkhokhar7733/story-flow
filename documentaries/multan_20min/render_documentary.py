import os
import sys
import json
import argparse
import subprocess
import time
import requests

ffmpeg = r'C:\Users\Microsoft\AppData\Local\Programs\Python\Python311\Scripts\ffmpeg.exe'
if not os.path.exists(ffmpeg):
    ffmpeg = 'ffmpeg'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(ROOT_DIR)

import config

from PIL import Image, ImageDraw, ImageFont
import textwrap

def get_or_create_placeholder_image(prompt: str, out_path: str, title: str, subtitle: str, w: int = 1920, h: int = 1080):
    """
    Creates a resilient, elegant 1080p archival documentary frame using Pillow.
    Guaranteed to work cross-platform without FFmpeg filter escaping or fontconfig errors.
    """
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return out_path

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img = Image.new('RGB', (w, h), color=(8, 18, 30))
    draw = ImageDraw.Draw(img)

    # Gold decorative border
    border_margin = 60 if w >= 1920 else 30
    draw.rectangle([border_margin, border_margin, w - border_margin, h - border_margin], outline=(212, 175, 55), width=3)
    draw.rectangle([border_margin + 10, border_margin + 10, w - border_margin - 10, h - border_margin - 10], outline=(100, 85, 30), width=1)

    # Fonts
    font_path = os.path.join(ROOT_DIR, "assets", "fonts", "font.ttf")
    font_bold_path = os.path.join(ROOT_DIR, "assets", "fonts", "font_bold.ttf")
    try:
        font_header = ImageFont.truetype(font_path, int(26 * (w / 1920)))
        font_title = ImageFont.truetype(font_bold_path, int(42 * (w / 1920)))
        font_body = ImageFont.truetype(font_path, int(26 * (w / 1920)))
    except Exception:
        font_header = font_title = font_body = ImageFont.load_default()

    header_y = int(130 * (h / 1080))
    title_y = int(h // 2 - (50 * (h / 1080)))
    body_y = int(h // 2 + (70 * (h / 1080)))

    draw.text((w // 2, header_y), "MULTAN: 5,000 YEARS OF LIVING HISTORY", fill=(212, 175, 55), font=font_header, anchor="mm")
    draw.text((w // 2, title_y), title[:65], fill=(245, 235, 214), font=font_title, anchor="mm")

    wrap_width = 65 if w >= 1920 else 35
    wrapped = textwrap.fill(subtitle, width=wrap_width)
    draw.text((w // 2, body_y), wrapped, fill=(200, 215, 225), font=font_body, anchor="mm", align="center")

    img.save(out_path, format="PNG")
    return out_path

def render_scene_clip(image_path: str, audio_path: str, duration: float, motion: str, out_path: str, w: int = 1920, h: int = 1080, fps: int = 30):
    total_frames = max(30, int(duration * fps))

    if motion == "zoom_out":
        z_expr = "max(1.15-0.001*on,1.0)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion == "pan_left":
        z_expr = "1.12"
        x_expr = "if(lte(on,1),(iw-iw/zoom)/2,max(x-1.0,0))"
        y_expr = "ih/2-(ih/zoom/2)"
    elif motion == "pan_right":
        z_expr = "1.12"
        x_expr = "if(lte(on,1),0,min(x+1.0,(iw-iw/zoom)))"
        y_expr = "ih/2-(ih/zoom/2)"
    else: # zoom_in
        z_expr = "min(zoom+0.001,1.15)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},"
        f"zoompan=z='{z_expr}':d={total_frames}:x='{x_expr}':y='{y_expr}':s={w}x{h}:fps={fps}"
    )

    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-t", f"{duration:.3f}",
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        err = res.stderr.decode('utf-8', errors='ignore')
        print(f"[FFmpeg ERROR] Scene render failed: {err[-400:]}")
        raise RuntimeError(f"FFmpeg failed with code {res.returncode}")

def render_chapter(chapter_data: dict, out_chapter_mp4: str, w: int = 1920, h: int = 1080):
    cid = chapter_data["chapter_id"]
    ctitle = chapter_data["title"]
    scenes = chapter_data["scenes"]
    print(f"\n=======================================================")
    print(f">> Rendering Chapter {cid}: {ctitle} ({len(scenes)} scenes)")
    print(f"=======================================================")

    temp_chunks = []
    chunk_dir = os.path.join(BASE_DIR, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)

    for idx, sc in enumerate(scenes, 1):
        sid = sc["scene_id"]
        narration = sc["narration"]
        prompt = sc["visual_prompt"]
        dur = sc.get("actual_duration_sec", sc.get("duration_sec", 9.5))
        motion = sc.get("motion", "zoom_in")

        aud_path = os.path.join(BASE_DIR, "audio", f"scene_{sid:03d}.mp3")
        img_path = os.path.join(BASE_DIR, "images", f"scene_{sid:03d}.png")
        if not os.path.exists(img_path):
            img_path = os.path.join(BASE_DIR, "images", f"scene_{sid:03d}.webp")

        if not os.path.exists(img_path):
            img_path = get_or_create_placeholder_image(
                prompt=prompt,
                out_path=os.path.join(BASE_DIR, "images", f"scene_{sid:03d}.png"),
                title=ctitle,
                subtitle=narration,
                w=w, h=h
            )

        chunk_path = os.path.join(chunk_dir, f"chunk_{sid:03d}.mp4")
        print(f"  [{idx}/{len(scenes)}] Scene {sid:03d} ({dur:.1f}s, {motion}) -> {chunk_path}")
        render_scene_clip(img_path, aud_path, dur, motion, chunk_path, w=w, h=h)
        temp_chunks.append(chunk_path)

    # Concat chapter chunks
    concat_list = os.path.join(chunk_dir, f"concat_ch_{cid}.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for cp in temp_chunks:
            esc = os.path.abspath(cp).replace("\\", "/")
            f.write(f"file '{esc}'\n")

    subprocess.run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        out_chapter_mp4
    ], check=True, stdout=subprocess.DEVNULL)

    print(f"[SUCCESS] Chapter {cid} exported: {out_chapter_mp4}")
    return out_chapter_mp4

def main():
    parser = argparse.ArgumentParser(description="20-Minute Multan Documentary Renderer")
    parser.add_argument("--chapter", "-c", type=int, default=0, help="Render specific chapter (1-9) or 0 for all")
    parser.add_argument("--aspect", "-a", type=str, default="16:9", choices=["16:9", "9:16"], help="Aspect ratio")
    args = parser.parse_args()

    manifest_file = os.path.join(BASE_DIR, "script.json")
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    w, h = (1920, 1080) if args.aspect == "16:9" else (1080, 1920)
    os.makedirs(os.path.join(ROOT_DIR, "output"), exist_ok=True)
    chapter_dir = os.path.join(BASE_DIR, "chapters_rendered")
    os.makedirs(chapter_dir, exist_ok=True)

    chapters = manifest["chapters"]
    rendered_chapters = []

    if args.chapter > 0:
        target_ch = next((c for c in chapters if c["chapter_id"] == args.chapter), None)
        if not target_ch:
            print(f"Error: Chapter {args.chapter} not found!")
            sys.exit(1)
        out_ch = os.path.join(chapter_dir, f"chapter_{args.chapter:02d}.mp4")
        render_chapter(target_ch, out_ch, w=w, h=h)
        return

    # Render all chapters
    for ch in chapters:
        cid = ch["chapter_id"]
        out_ch = os.path.join(chapter_dir, f"chapter_{cid:02d}.mp4")
        render_chapter(ch, out_ch, w=w, h=h)
        rendered_chapters.append(out_ch)

    # Master Concat
    master_concat_list = os.path.join(chapter_dir, "master_concat.txt")
    with open(master_concat_list, "w", encoding="utf-8") as f:
        for rc in rendered_chapters:
            esc = os.path.abspath(rc).replace("\\", "/")
            f.write(f"file '{esc}'\n")

    final_master_mp4 = os.path.join(ROOT_DIR, "output", "Multan_5000_Years_Full_Documentary_20Min.mp4")
    print(f"\n>> Merging all {len(rendered_chapters)} chapters into master 20-minute documentary...")
    subprocess.run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", master_concat_list,
        "-c", "copy",
        "-movflags", "+faststart",
        final_master_mp4
    ], check=True, stdout=subprocess.DEVNULL)

    size_mb = os.path.getsize(final_master_mp4) / (1024 * 1024)
    print(f"\n============================================================")
    print(f"MASTER 20-MINUTE DOCUMENTARY COMPLETE!")
    print(f"File: {final_master_mp4}")
    print(f"Size: {size_mb:.2f} MB")
    print(f"============================================================")

if __name__ == "__main__":
    main()
