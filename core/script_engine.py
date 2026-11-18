"""
script_engine.py - Generates scene-by-scene storytelling scripts with tailored cartoon visual prompts.
"""
import json
import os
import re
import requests
import config

SYSTEM_PROMPT = """You are a master storyteller for a viral, high-retention cartoon & illustrated story YouTube channel.
Your goal is to write captivating, emotional, and visually imaginative stories where each scene is paired with a vivid, literal cartoon image prompt that precisely illustrates what the narrator speaks.

RULES FOR VIRAL RETENTION:
1. THE HOOK: Never start with generic intros like "Once upon a time" or "Did you know". Start immediately with high intrigue, unusual action, or an immediate mystery.
2. PACING: Break the story into short, distinct visual scenes (around 5-7 seconds each, 1-2 spoken sentences, ~15-20 words per scene).
3. EXACT VISUAL-NARRATIVE MATCH:
   Every single scene's visual prompt MUST directly depict the literal physical action, specific props, character emotion, and environment described in that scene's narration sentence.
   The image must visually prove what the voiceover is narrating so the viewer's eyes track the story seamlessly.
4. CHARACTER CONSISTENCY: Give the main character distinct, recognizable traits (clothing, color, signature accessory) and keep them consistent.
5. FORMAT: You MUST return strictly valid JSON matching the exact schema specified, with no markdown or extraneous text.
"""

def generate_story_script(topic: str, target_seconds: int = 60) -> dict:
    """
    Generate a complete storytelling script structured into scenes.
    For target_seconds=60: ~8-10 micro-scenes.
    """
    # Calculate scene count: ~6.5 seconds per scene for fast engaging cuts
    scene_count = max(4, round(target_seconds / 6.5))
    target_words = round(target_seconds * 2.4)  # ~144 words for 60 seconds

    user_prompt = f"""Write an engaging illustrated cartoon story about: "{topic}".

SPECIFICATIONS:
- Target Duration: ~{target_seconds} seconds
- Total Scenes: Exactly {scene_count} scenes
- Total Word Count: Approximately {target_words} words across all {scene_count} scenes combined (~15-18 words per scene)

CRITICAL INSTRUCTION FOR VISUAL PROMPTS:
Each scene's visual prompt MUST be a literal, specific illustration of what is spoken in that scene's narration. The viewer MUST see what they hear.

OUTPUT FORMAT (Must be valid JSON only):
{{
  "title": "Captivating Story Title",
  "character_anchor": "Brief consistent visual description of main character (e.g. an elderly clockmaker Silas with silver spectacles and an apron)",
  "scenes": [
    {{
      "scene_id": 1,
      "narration": "Spoken sentence for scene 1 (15-20 words).",
      "visual_prompt": "Specific visual description of what we see happening in this exact sentence",
      "camera_motion": "zoom_in"
    }}
  ]
}}

Valid camera_motion values: "zoom_in", "zoom_out", "pan_left", "pan_right".
Generate all {scene_count} scenes now:"""

    # 1. Try Groq API
    if config.GROQ_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500,
                "response_format": {"type": "json_object"}
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=25)
            if res.status_code == 200:
                raw_content = res.json()["choices"][0]["message"].get("content", "").strip()
                parsed = _parse_json_safely(raw_content)
                if parsed and "scenes" in parsed and len(parsed["scenes"]) > 0:
                    _enrich_visual_prompts(parsed)
                    return parsed
        except Exception as e:
            print(f"[script_engine] Groq attempt failed: {e}. Trying fallback...")

    # 2. Try AI Horde Text API (Free Crowdsourced LLM)
    try:
        horde_script = _generate_with_ai_horde(topic, scene_count, target_words)
        if horde_script:
            _enrich_visual_prompts(horde_script)
            return horde_script
    except Exception as e:
        print(f"[script_engine] AI Horde LLM attempt failed: {e}. Using built-in generator...")

    # 3. Built-in High-Quality Story Template Generator (Always reliable offline)
    fallback = _generate_template_story(topic, scene_count)
    _enrich_visual_prompts(fallback)
    return fallback


def _enrich_visual_prompts(story_data: dict):
    """Enriches each scene's visual prompt with the character anchor and cartoon styling."""
    char_anchor = story_data.get("character_anchor", "").strip()
    for scene in story_data.get("scenes", []):
        base_prompt = scene.get("visual_prompt", "")
        if char_anchor and char_anchor.lower() not in base_prompt.lower():
            combined = f"{char_anchor}, {base_prompt}, {config.CARTOON_STYLE_PREFIX}"
        else:
            combined = f"{base_prompt}, {config.CARTOON_STYLE_PREFIX}"
        scene["full_image_prompt"] = combined


def _generate_with_ai_horde(topic: str, scene_count: int, target_words: int) -> dict:
    """Generate script via AI Horde free LLM cluster."""
    headers = {
        "Client-Agent": config.AI_HORDE_CLIENT_AGENT,
        "apikey": config.AI_HORDE_API_KEY,
        "Content-Type": "application/json"
    }
    prompt = f"""Write a {scene_count}-scene cartoon story about "{topic}".
Output as JSON:
{{"title": "Title", "character_anchor": "visual description of character", "scenes": [{{"scene_id": 1, "narration": "sentence", "visual_prompt": "description", "camera_motion": "zoom_in"}}]}}"""

    payload = {
        "prompt": prompt,
        "params": {"max_length": 600, "temperature": 0.7}
    }
    post_res = requests.post(f"{config.AI_HORDE_BASE_URL}/generate/text/async", json=payload, headers=headers).json()
    job_id = post_res.get("id")
    if not job_id:
        return None

    import time
    for _ in range(15):
        time.sleep(3)
        chk = requests.get(f"{config.AI_HORDE_BASE_URL}/generate/text/status/{job_id}", headers=headers).json()
        if chk.get("done"):
            text = chk["generations"][0]["text"]
            return _parse_json_safely(text)
    return None


def _generate_template_story(topic: str, scene_count: int) -> dict:
    """High quality procedural fallback if external LLMs are unavailable."""
    clean_topic = topic.strip()
    return {
        "title": f"The Tale of {clean_topic.title()}",
        "character_anchor": "a brave little orange fox named Leo wearing a soft starry blue scarf",
        "scenes": [
            {
                "scene_id": 1,
                "narration": f"Deep within the ancient Whispering Woods, young Leo the fox discovered a mysterious glowing secret about {clean_topic}.",
                "visual_prompt": "little orange fox in starry blue scarf discovering a glowing magical ancient relic half-buried under glowing bioluminescent moss",
                "camera_motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "With every step across the forgotten stone bridge, glowing stardust rose from the river below, lighting a path no creature had walked in centuries.",
                "visual_prompt": "little fox cautiously stepping across a cobblestone mossy bridge over a river of sparkling starlight and floating lanterns",
                "camera_motion": "pan_left"
            },
            {
                "scene_id": 3,
                "narration": "Suddenly, a friendly clockwork owl perched on an elder branch, opening a gilded door that revealed the wondrous world beyond.",
                "visual_prompt": "magnificent steampunk clockwork owl with brass wings perched on a mystical silver oak opening a small glowing golden doorway",
                "camera_motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "Taking a deep breath and leaping forward, Leo realized that true courage isn't having no fear—it is discovering the magic waiting on the other side.",
                "visual_prompt": "joyful little fox leaping into a breathtaking vibrant sunrise realm of floating cloud islands and friendly whimsical creatures",
                "camera_motion": "pan_right"
            }
        ]
    }


def _parse_json_safely(text: str) -> dict:
    """Attempts to clean and parse JSON from LLM output."""
    if not text:
        return None
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except Exception:
        # Search for first { and last }
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
    return None
