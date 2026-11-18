"""
image_engine.py - Sequential Image-to-Image Generation for coherent scene-by-scene storytelling via AI Horde.
"""
import os
import time
import base64
import io
import requests
from PIL import Image
import config

def generate_scene_images(scenes: list, aspect: str = "9:16", progress_callback=None) -> list:
    """
    Generates cartoon illustrations for each scene using sequential image-to-image (img2img)
    chaining and locked checkpoint models to guarantee visual character & style consistency.
    Supports 9:16 (vertical Shorts) and 16:9 (horizontal widescreen).
    """
    total = len(scenes)
    locked_model = None
    base_seed = None
    master_anchor_path = None
    prev_scene_path = None

    preset = config.ASPECT_PRESETS.get(aspect, config.ASPECT_PRESETS["9:16"])
    target_w = preset["image_width"]
    target_h = preset["image_height"]

    for idx, scene in enumerate(scenes, 1):
        scene_id = scene.get("scene_id", idx)
        prompt = scene.get("full_image_prompt", scene.get("visual_prompt", ""))
        output_filename = f"scene_{scene_id}_{int(time.time())}.png"
        output_path = os.path.join(config.TEMP_DIR, output_filename)

        is_sequential = (idx > 1 and prev_scene_path and os.path.exists(prev_scene_path))
        seq_label = " [img2img linked]" if is_sequential else " [Master Keyframe]"

        if progress_callback:
            progress_callback(idx, total, f"Generating Scene {idx}/{total}{seq_label} on AI Horde...")
        else:
            print(f"[image_engine] Scene {idx}/{total}{seq_label}: {prompt[:65]}...", flush=True)

        # Decide reference image: Scene 2 uses Scene 1; Scene 3+ uses prev scene or master anchor
        ref_image_path = None
        denoising = 0.58
        if is_sequential:
            ref_image_path = prev_scene_path
            denoising = 0.58

        success = False
        for attempt in range(3):
            try:
                # Clamp Horde request to <= 512x512 to prevent KudosUpfront rejection on free tier
                horde_w = min(target_w, 512)
                horde_h = min(target_h, 512)

                img_url, used_model, used_seed = _request_horde_image(
                    prompt=prompt,
                    width=horde_w,
                    height=horde_h,
                    ref_image_path=ref_image_path if attempt == 0 else None, # fallback to txt2img on retry
                    target_model=locked_model,
                    denoising_strength=denoising,
                    seed=str(base_seed + idx * 23) if base_seed else None
                )

                if img_url:
                    _download_and_save_image(img_url, output_path)
                    scene["image_path"] = output_path
                    success = True

                    # Lock the model and seed from Scene 1 for all subsequent scenes
                    if idx == 1 or not locked_model:
                        locked_model = used_model
                        try:
                            base_seed = int(used_seed)
                        except (TypeError, ValueError):
                            base_seed = 42
                        master_anchor_path = output_path
                        print(f"[image_engine] Style Locked -> Model: '{locked_model}', Base Seed: {base_seed} ({target_w}x{target_h})", flush=True)

                    prev_scene_path = output_path
                    break
            except Exception as e:
                print(f"[image_engine] Scene {scene_id} attempt {attempt + 1} failed: {e}", flush=True)
                time.sleep(2)

        if not success:
            print(f"[image_engine] Warning: Generating character fallback for Scene {scene_id}", flush=True)
            _create_fallback_image(scene_id, prompt, output_path, target_w, target_h, character_id=scene.get("character_id"))
            scene["image_path"] = output_path
            prev_scene_path = output_path

    return scenes


def _request_horde_image(prompt: str, width: int = 512, height: int = 768, ref_image_path: str = None, target_model: str = None, denoising_strength: float = 0.58, seed: str = None):
    """
    Submits generation to AI Horde. If ref_image_path is provided, uses img2img sequence.
    Returns (image_url, model_name, seed).
    """
    headers = {
        "Client-Agent": config.AI_HORDE_CLIENT_AGENT,
        "apikey": config.AI_HORDE_API_KEY,
        "Content-Type": "application/json"
    }

    models_to_use = [target_model] if target_model else config.CARTOON_IMAGE_MODELS

    payload = {
        "prompt": f"{prompt} ### {config.CARTOON_NEGATIVE_PROMPT}",
        "params": {
            "width": width,
            "height": height,
            "steps": 22,
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.5,
        },
        "models": models_to_use,
        "nsfw": False,
        "censor_nsfw": True,
        "r2": True
    }

    if seed:
        payload["params"]["seed"] = str(seed)

    # Attach img2img reference image if available
    if ref_image_path and os.path.exists(ref_image_path):
        b64_img = _encode_image_b64(ref_image_path, width, height)
        if b64_img:
            payload["source_image"] = b64_img
            payload["source_processing"] = "img2img"
            payload["params"]["denoising_strength"] = float(denoising_strength)

    res = requests.post(f"{config.AI_HORDE_BASE_URL}/generate/async", json=payload, headers=headers, timeout=20)
    data = res.json()
    job_id = data.get("id")
    if not job_id:
        raise RuntimeError(f"Horde returned no job ID: {data}")

    # Poll status
    start_time = time.time()
    while time.time() - start_time < 35:
        time.sleep(3)
        chk = requests.get(f"{config.AI_HORDE_BASE_URL}/generate/check/{job_id}", headers=headers, timeout=15).json()

        if chk.get("faulted"):
            raise RuntimeError(f"Horde job {job_id} faulted on worker.")

        if chk.get("done"):
            status_res = requests.get(f"{config.AI_HORDE_BASE_URL}/generate/status/{job_id}", headers=headers, timeout=15).json()
            gens = status_res.get("generations", [])
            if gens and gens[0].get("img"):
                gen = gens[0]
                return gen["img"], gen.get("model", "stable_diffusion"), gen.get("seed", "0")
            raise RuntimeError("Horde completed but returned no image.")

    raise TimeoutError(f"Horde generation timed out for job {job_id}")


def _encode_image_b64(image_path: str, max_w: int = 512, max_h: int = 768) -> str:
    """Encodes and optimizes image as base64 JPEG for img2img transmission."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"[image_engine] Failed to encode ref image {image_path}: {e}")
        return None


def _download_and_save_image(img_data: str, target_path: str):
    """Download R2 hosted image or decode base64, ensure standard RGB PNG."""
    if img_data.startswith("http"):
        resp = requests.get(img_data, timeout=30)
        img = Image.open(io.BytesIO(resp.content))
    else:
        raw_bytes = base64.b64decode(img_data)
        img = Image.open(io.BytesIO(raw_bytes))

    img = img.convert("RGB")
    img.save(target_path, "PNG")


def _create_fallback_image(scene_id: int, prompt: str, target_path: str, width: int = 512, height: int = 768, character_id: str = None):
    """Uses character visual keyframe or stylized gradient backdrop if worker fails."""
    # Check for character visual asset in assets/characters/
    char_asset = None
    characters_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "characters")
    if character_id:
        p = os.path.join(characters_dir, f"{character_id}.png")
        if os.path.exists(p):
            char_asset = p
    if not char_asset:
        default_p = os.path.join(characters_dir, "chacha_bashir.png")
        if os.path.exists(default_p):
            char_asset = default_p

    if char_asset and os.path.exists(char_asset):
        try:
            from PIL import ImageOps
            with Image.open(char_asset) as base:
                fitted = ImageOps.fit(base, (width, height), method=Image.Resampling.LANCZOS)
                fitted.save(target_path, "PNG")
                return
        except Exception as e:
            print(f"[image_engine] Character fallback composite error: {e}")

    from PIL import ImageDraw
    img = Image.new("RGB", (width, height), color=(30, 40, 60))
    draw = ImageDraw.Draw(img)

    margin = 30
    draw.rectangle([(margin, margin), (width - margin, height - margin)], fill=(45, 60, 90), outline=(100, 150, 240), width=4)
    draw.text((width // 2, height // 2 - 40), f"Scene {scene_id}", fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, height // 2 + 30), prompt[:60] + "...", fill=(200, 220, 255), anchor="mm")
    img.save(target_path, "PNG")
