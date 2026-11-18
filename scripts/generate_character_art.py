#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_character_art.py — Synthesizes high-fidelity stylized 3D character artwork,
turnarounds, and keyframes using state-of-the-art Flux AI models.
"""

import os
import sys
import time
import urllib.parse
import requests
from PIL import Image
import io

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "characters")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHARACTERS_TO_GENERATE = [
    {
        "id": "chacha_bashir",
        "name": "Chacha Bashir",
        "filename": "chacha_bashir.png",
        "avatar_filename": "chacha_bashir_avatar.png",
        "prompt": (
            "Stylized 3D low poly video game character, Pakistani auto rickshaw driver, "
            "cheerful 50 year old man with twirled handlebar mustache and aviator sunglasses, "
            "wearing vibrant emerald green waistcoat with colorful truck art embroidery and white shalwar kameez, "
            "driving a decorated Pakistani green and yellow auto rickshaw with 'Lahore Lahore Aye' art, "
            "driving through a vibrant Lahore street with shop signboards 'Data Biryani' 'Punjab Tailors' and overhead wires, "
            "warm golden hour sunset lighting, Unreal Engine 5 stylized cartoon game art style, 8k render, masterpiece"
        ),
        "avatar_prompt": (
            "Stylized 3D low poly character portrait, Chacha Bashir, cheerful Pakistani uncle with twirled handlebar mustache, "
            "cool sunglasses, green embroidered truck-art waistcoat, friendly smile, studio lighting, colorful gradient background, "
            "Pixar and stylized video game aesthetic, 3D character bust, high quality"
        )
    },
    {
        "id": "zainab_explorer",
        "name": "Zainab the Explorer",
        "filename": "zainab_explorer.png",
        "avatar_filename": "zainab_avatar.png",
        "prompt": (
            "Stylized 3D adventure game character, 24 year old Pakistani female archaeologist and explorer named Zainab, "
            "wearing khaki explorer utility vest with brass buckles over royal blue kurta, leather satchel bag, brass explorer goggles rested on forehead, "
            "holding an ancient Indus Valley terracotta artifact, standing before ancient fortress gates of Multan and Lahore Fort, "
            "cinematic adventure game lighting, stylized 3D Pixar character art, rich textures, Unreal Engine 5 aesthetic, 8k"
        ),
        "avatar_prompt": (
            "Stylized 3D character portrait bust of Zainab, young adventurous Pakistani woman archaeologist, "
            "wearing brass explorer goggles on forehead, confident warm smile, dark hair tied back, leather satchel strap, "
            "vibrant lapis lazuli and gold background, stylized cartoon game character, 8k render"
        )
    },
    {
        "id": "raja_veer",
        "name": "Raja Veer - Ancient Citadel Guardian",
        "filename": "raja_veer.png",
        "avatar_filename": "raja_veer_avatar.png",
        "prompt": (
            "Stylized 3D epic warrior prince character, Raja Veer of the ancient Mallians in 326 BC, "
            "ornate embossed brass armor chestplate, saffron silk turban with emerald jewel and peacock feather, "
            "holding an ancient engraved curved steel talwar sword, standing on the sunlit battlements of the ancient Citadel of Multan, "
            "dramatic cinematic lighting, stylized Clash of Clans and Prince of Persia mythic hero game art style, 8k"
        ),
        "avatar_prompt": (
            "Stylized 3D hero portrait bust, Raja Veer ancient Indian Punjabi prince warrior, "
            "regal turban with jewel, golden armor collar, noble fierce gaze, stylized 3D game art, warm sunset glow, 8k"
        )
    },
    {
        "id": "baba_fazal",
        "name": "Baba Fazal - The Walled City Storyteller",
        "filename": "baba_fazal.png",
        "avatar_filename": "baba_fazal_avatar.png",
        "prompt": (
            "Stylized 3D storybook character, Baba Fazal, wise elderly Pakistani tea stall master and storyteller, "
            "long flowing silver beard, maroon wool pashmina shawl over gray kurta, pouring steaming spiced chai from a glowing brass samovar into clay cups, "
            "sitting outside in an atmospheric old Lahore bazaar with glowing lanterns at dusk, "
            "whimsical stylized 3D animation style, warm cozy glowing light, detailed volumetric steam, 8k"
        ),
        "avatar_prompt": (
            "Stylized 3D character portrait, Baba Fazal the wise storyteller elder, "
            "warm gentle smile, twinkling eyes, neat white beard, cozy maroon shawl, warm lantern glow background, stylized 3D art"
        )
    }
]


def download_pollinations_image(prompt: str, output_path: str, width: int = 1024, height: int = 1024) -> bool:
    """Fetches high quality image from Pollinations Flux with retry."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true&seed=42"
    print(f"🎨 Generating: {os.path.basename(output_path)}...")
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 1000:
                img = Image.open(io.BytesIO(resp.content))
                img.save(output_path, "PNG")
                print(f"✅ Saved ({img.size[0]}x{img.size[1]}): {output_path}")
                return True
            else:
                print(f"⚠️ Attempt {attempt}: HTTP {resp.status_code}, length {len(resp.content)}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
        time.sleep(2)
    return False


def main():
    print(f"🚀 Generating 3D Stylized Character Art into: {OUTPUT_DIR}\n")
    success_count = 0
    total = len(CHARACTERS_TO_GENERATE) * 2

    for char in CHARACTERS_TO_GENERATE:
        main_img_path = os.path.join(OUTPUT_DIR, char["filename"])
        avatar_img_path = os.path.join(OUTPUT_DIR, char["avatar_filename"])

        if download_pollinations_image(char["prompt"], main_img_path, width=1280, height=720):
            success_count += 1
        time.sleep(1)

        if download_pollinations_image(char["avatar_prompt"], avatar_img_path, width=512, height=512):
            success_count += 1
        time.sleep(1)

    print(f"\n🎉 Done! Generated {success_count}/{total} character visual assets.")


if __name__ == "__main__":
    main()
