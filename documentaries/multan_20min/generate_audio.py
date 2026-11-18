import asyncio
import os
import json
import edge_tts
import subprocess
import re

ffmpeg = r'C:\Users\Microsoft\AppData\Local\Programs\Python\Python311\Scripts\ffmpeg.exe'
if not os.path.exists(ffmpeg):
    ffmpeg = 'ffmpeg'

async def synthesize_scenes(manifest_path="documentaries/multan_20min/script.json", voice="en-US-ChristopherNeural", out_dir="documentaries/multan_20min/audio"):
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    all_scenes = []
    for ch in data["chapters"]:
        for sc in ch["scenes"]:
            sc["chapter_id"] = ch["chapter_id"]
            sc["chapter_title"] = ch["title"]
            all_scenes.append(sc)

    total = len(all_scenes)
    print(f">> Synthesizing {total} scenes using Edge-TTS ({voice})...")

    durations = {}
    for idx, sc in enumerate(all_scenes, 1):
        sid = sc["scene_id"]
        narration = sc["narration"]
        target_mp3 = os.path.join(out_dir, f"scene_{sid:03d}.mp3")

        if not os.path.exists(target_mp3) or os.path.getsize(target_mp3) < 1000:
            for attempt in range(3):
                try:
                    comm = edge_tts.Communicate(narration, voice, rate="-2%")
                    await comm.save(target_mp3)
                    break
                except Exception as e:
                    print(f"  Retry scene {sid} ({attempt+1}/3): {e}")
                    await asyncio.sleep(1.5)

        # Measure duration with ffmpeg
        res = subprocess.run([ffmpeg, "-i", target_mp3], stderr=subprocess.PIPE, text=True)
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', res.stderr)
        dur = float(m.group(1))*3600 + float(m.group(2))*60 + float(m.group(3)) if m else sc["duration_sec"]
        durations[sid] = round(dur, 2)
        sc["actual_duration_sec"] = round(dur, 2)

        if idx % 10 == 0 or idx == total:
            print(f"  Progress: {idx}/{total} scenes synthesized ({dur:.2f}s)")

    # Update manifest with actual durations
    data["actual_narration_sec"] = sum(durations.values())
    data["actual_narration_min"] = round(data["actual_narration_sec"] / 60, 2)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] All {total} audio scenes ready!")
    print(f"Total narration duration: {data['actual_narration_min']} minutes ({data['actual_narration_sec']}s)")

if __name__ == "__main__":
    asyncio.run(synthesize_scenes())
