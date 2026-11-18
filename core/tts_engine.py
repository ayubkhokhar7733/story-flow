"""
tts_engine.py - Voiceover generation with Edge-TTS and phrase-level SRT subtitles.
"""
import asyncio
import os
import time
from moviepy import AudioFileClip
import config

def generate_story_audio(scenes: list, voice_name: str = None) -> tuple:
    """
    Synthesizes narration for each scene, measures exact durations,
    generates word-synchronized SRT subtitles, and returns:
        (full_audio_path, srt_path, total_duration, updated_scenes)
    """
    voice = voice_name or config.DEFAULT_VOICE
    if voice in config.VALID_VOICES:
        voice = config.VALID_VOICES[voice]

    full_audio_path = os.path.join(config.TEMP_DIR, "story_voiceover.mp3")
    srt_path = os.path.join(config.TEMP_DIR, "story_subtitles.srt")

    # Combine narrations while tracking sentence offsets
    full_text = " ".join(s.get("narration", "").strip() for s in scenes).strip()
    if not full_text:
        raise ValueError("No narration text found in scenes.")

    print(f"[tts_engine] Synthesizing speech with voice '{voice}'...")
    _run_edge_tts(full_text, voice, full_audio_path, srt_path)

    # Measure total audio duration
    total_duration = _measure_duration(full_audio_path)
    print(f"[tts_engine] Voiceover synthesized successfully! Total duration: {total_duration:.2f}s")

    # Distribute scene durations proportionately based on narration word count
    total_words = sum(len(s.get("narration", "").split()) for s in scenes)
    if total_words == 0:
        total_words = len(scenes)

    current_offset = 0.0
    accumulated = 0.0
    for idx, scene in enumerate(scenes):
        w_count = len(scene.get("narration", "").split())
        if idx == len(scenes) - 1:
            # Last scene absorbs remainder so visual duration matches voiceover to the millisecond
            scene_dur = max(2.5, round(total_duration - accumulated, 2))
        else:
            ratio = w_count / total_words if total_words > 0 else (1.0 / len(scenes))
            scene_dur = max(2.5, round(total_duration * ratio, 2))
            accumulated += scene_dur

        scene["duration_sec"] = scene_dur
        scene["start_sec"] = current_offset
        current_offset += scene_dur

    return full_audio_path, srt_path, total_duration, scenes


def _measure_duration(path: str) -> float:
    try:
        clip = AudioFileClip(path)
        d = float(clip.duration)
        clip.close()
        return d
    except Exception:
        return 30.0


def _run_edge_tts(text: str, voice: str, audio_path: str, srt_path: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_async_edge_tts(text, voice, audio_path, srt_path))
    finally:
        loop.close()


async def _async_edge_tts(text: str, voice: str, audio_path: str, srt_path: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=config.VOICE_RATE, boundary="WordBoundary")
    word_events = []

    with open(audio_path, "wb") as f_audio:
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                f_audio.write(chunk.get("data", b""))
            elif chunk.get("type") == "WordBoundary" and chunk.get("text"):
                offset_s = float(chunk.get("offset", 0)) / 10_000_000.0
                dur_s = float(chunk.get("duration", 0)) / 10_000_000.0
                word_events.append({
                    "text": str(chunk.get("text", "")).strip(),
                    "start": offset_s,
                    "end": offset_s + max(0.08, dur_s),
                })

    # Group single words into 3-5 word readable broadcast subtitle phrases
    if word_events:
        srt_lines = []
        cue_idx = 1
        phrase = []
        p_start = 0.0
        p_end = 0.0

        def format_ts(sec: float) -> str:
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            ms = int(round((sec - int(sec)) * 1000))
            return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

        for ev in word_events:
            if not phrase:
                p_start = ev["start"]
            phrase.append(ev["text"])
            p_end = ev["end"]

            # Break every 4 words or on punctuation
            if len(phrase) >= 4 or any(ev["text"].endswith(p) for p in [".", ",", "!", "?", ";", ":"]):
                srt_lines.append(f"{cue_idx}\n{format_ts(p_start)} --> {format_ts(p_end)}\n{' '.join(phrase)}\n")
                cue_idx += 1
                phrase = []

        if phrase:
            srt_lines.append(f"{cue_idx}\n{format_ts(p_start)} --> {format_ts(p_end)}\n{' '.join(phrase)}\n")

        with open(srt_path, "w", encoding="utf-8") as f_srt:
            f_srt.write("\n".join(srt_lines))
