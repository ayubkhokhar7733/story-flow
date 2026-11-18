#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
character_engine.py — Manages stylized character personas, visual consistency tokens,
avatar keyframes, and character-driven voiceover styling for StoryFlow.
"""

import os
import json
from typing import Dict, Any, List, Optional

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "characters", "registry.json")


class CharacterEngine:
    def __init__(self, registry_path: str = REGISTRY_PATH):
        self.registry_path = registry_path
        self._registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if not os.path.exists(self.registry_path):
            return {"default_character": "chacha_bashir", "characters": {}}
        try:
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[character_engine] Warning: Failed to read registry: {e}")
            return {"default_character": "chacha_bashir", "characters": {}}

    def list_characters(self) -> List[Dict[str, Any]]:
        """Returns a list of all registered character profiles."""
        chars = self._registry.get("characters", {})
        return [
            {
                "id": cid,
                "name": data.get("name"),
                "title": data.get("title"),
                "catchphrase": data.get("personality", {}).get("english_catchphrase"),
                "avatar": data.get("assets", {}).get("avatar"),
                "art_style": data.get("appearance", {}).get("art_style")
            }
            for cid, data in chars.items()
        ]

    def get_character(self, character_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetches character data by ID, or fallback to default."""
        chars = self._registry.get("characters", {})
        if not character_id or character_id not in chars:
            default_id = self._registry.get("default_character", "chacha_bashir")
            return chars.get(default_id, {})
        return chars[character_id]

    def get_visual_tokens(self, character_id: Optional[str] = None) -> str:
        """Returns visual prompt modifiers to lock character design in image generation."""
        char = self.get_character(character_id)
        return char.get("visual_tokens", "")

    def get_voice_profile(self, character_id: Optional[str] = None, language: str = "en") -> Dict[str, str]:
        """Returns Edge-TTS voice configuration matching character persona."""
        char = self.get_character(character_id)
        voice_info = char.get("voice", {})
        if language == "ur":
            return {
                "voice": voice_info.get("voice_name", "ur-PK-AsadNeural"),
                "rate": voice_info.get("rate", "+0%"),
                "pitch": voice_info.get("pitch", "+0Hz")
            }
        return {
            "voice": voice_info.get("english_voice_name", "en-US-GuyNeural"),
            "rate": voice_info.get("rate", "+0%"),
            "pitch": voice_info.get("pitch", "+0Hz")
        }

    def enhance_prompt_with_character(self, prompt: str, character_id: Optional[str] = None) -> str:
        """Prefaces an image generation prompt with character visual tokens."""
        char = self.get_character(character_id)
        tokens = char.get("visual_tokens", "")
        if not tokens:
            return prompt
        char_name = char.get("name", "Character")
        return f"{tokens}, featuring {char_name}: {prompt}"

    def get_system_prompt_addition(self, character_id: Optional[str] = None) -> str:
        """Returns script instruction to have LLM write narration in the character's voice."""
        char = self.get_character(character_id)
        if not char:
            return ""
        name = char.get("name")
        persona_prompt = char.get("system_prompt", "")
        catchphrase = char.get("personality", {}).get("english_catchphrase", "")
        return (
            f"\nNARRATIVE CHARACTER ANCHOR:\n"
            f"The narrator and visual protagonist is '{name}'.\n"
            f"Persona & Tone: {persona_prompt}\n"
            f"Signature Catchphrase to include organically: \"{catchphrase}\"\n"
            f"Ensure every scene's visual prompt describes {name}'s actions and expressions.\n"
        )


# Singleton instance
character_engine = CharacterEngine()
