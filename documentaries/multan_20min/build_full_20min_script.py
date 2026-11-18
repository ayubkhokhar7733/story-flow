import json
import os

def build_full_20min_manifest():
    with open("documentaries/multan_20min/script.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters = data["chapters"]

    extra_c3 = [
        {
            "scene_id": 25.1,
            "narration": "Greek physician Critodemus of Cos cut open Alexander's ribcage with a scalpel while his officers held the screaming king down, extracting the three-inch barbed arrowhead in a pool of blood.",
            "visual_prompt": "intense historical scene inside the royal tent, physician Critodemus operating on Alexander the Great by torchlight, generals holding the wounded king, raw ancient medical drama",
            "duration_sec": 10.5,
            "motion": "zoom_in"
        },
        {
            "scene_id": 25.2,
            "narration": "To quell rumors among the army that Alexander had perished, the commanders carried him on a shield onto the deck of his royal flagship, where he raised his hand to thunderous weeping and cheering.",
            "visual_prompt": "Alexander the Great lying on his shield aboard a royal galley on the Chenab river, weakly raising his arm to thousands of Macedonian soldiers lining the riverbanks shouting with joy",
            "duration_sec": 10.5,
            "motion": "pan_right"
        }
    ]

    extra_c4 = [
        {
            "scene_id": 37.1,
            "narration": "Famous 10th-century geographer Ibn Hawqal recorded that Multan was half the size of Baghdad, defended by ten massive iron gates and a moat fed directly from the river.",
            "visual_prompt": "medieval Arab traveler Ibn Hawqal sketching the fortifications of Multan on parchment, overlooking the deep moat and colossal spiked iron gate towers, historical cartography aesthetics",
            "duration_sec": 10.0,
            "motion": "zoom_out"
        },
        {
            "scene_id": 37.2,
            "narration": "Specialized caravans carrying raw silk, emeralds, and Persian perfume departed weekly from Multan's gates, traveling through the Bolan and Gomal passes toward Central Asia.",
            "visual_prompt": "long merchant caravan leaving the arched portal of Multan at dawn, pack mules and camels laden with silk bolts and brass lanterns, departing into the golden desert morning",
            "duration_sec": 9.5,
            "motion": "pan_left"
        }
    ]

    extra_c6 = [
        {
            "scene_id": 59.1,
            "narration": "Legend tells that when the wandering mystic Shams Tabrizi was refused food in the city, he prayed to the sun, calling it down closer to Multan to roast his meal—an enduring folk tale explaining the city's legendary summer heat.",
            "visual_prompt": "mythological folklore painting, saint Shams Tabrizi in ragged robes looking up at a blazing golden sun hovering close above the ancient brick roofs of Multan, ethereal heat mirage shimmering",
            "duration_sec": 10.5,
            "motion": "zoom_in"
        },
        {
            "scene_id": 59.2,
            "narration": "Multani artisans passed the secrets of Kashigari from father to son across twenty generations, grinding cobalt oxide and quartz into glazes that never lose their brilliance under the harsh desert sun.",
            "visual_prompt": "artisan workshop in old Multan, master potter spinning a kick-wheel, apprentice grinding cobalt blue minerals with mortar and pestle, shelves filled with glazed turquoise vases and tiles",
            "duration_sec": 10.0,
            "motion": "pan_right"
        }
    ]

    extra_c7 = [
        {
            "scene_id": 63.1,
            "narration": "In May 1758, in one of the most astonishing expansions in Indian history, the Maratha Empire marched three thousand miles from Pune, driving out the Afghan garrison and raising the saffron flag of the Maratha Confederacy over the citadel of Multan.",
            "visual_prompt": "Maratha cavalry in saffron turbans and steel breastplates riding victoriously along the battlements of Multan citadel, unfurling the swallow-tailed Bhagwa Dhwaj flag over the ramparts, historic conquest",
            "duration_sec": 11.0,
            "motion": "pan_left"
        },
        {
            "scene_id": 63.2,
            "narration": "Under Maratha general Tukoji Rao Holkar, Multan became the northernmost outpost of Hindu Maratha rule, stretching the empire from the Arabian Sea to the gates of Central Asia.",
            "visual_prompt": "Maratha general Tukoji Holkar receiving the keys of the Multan fortress from local dignitaries in a grand brick pavilion, historic alliance, panoramic historical painting",
            "duration_sec": 10.0,
            "motion": "zoom_in"
        }
    ]

    extra_c8 = [
        {
            "scene_id": 78.1,
            "narration": "Beneath the battlefield, a silent war of shadows took place. British sappers and Punjabi miners dug underground tunnels toward the ramparts, engaging in deadly hand-to-hand combat inside pitch-black tunnels.",
            "visual_prompt": "underground siege warfare, sappers digging through earth by lantern light with picks and shovels, subterranean clash between soldiers inside a collapsed wooden tunnel",
            "duration_sec": 10.0,
            "motion": "zoom_in"
        },
        {
            "scene_id": 83.1,
            "narration": "British Lieutenant Edwardes wrote in his diary: 'Never have I witnessed men fight with such dogged, sullen heroism as the garrison of Multan amidst the smoking ruins of their sanctuary.'",
            "visual_prompt": "British officer Lieutenant Edwardes writing in his leather journal inside a siege trench tent by candlelight, through the canvas flap showing the smoking silhouette of Multan under bombardment",
            "duration_sec": 10.5,
            "motion": "zoom_out"
        }
    ]

    chapters[2]["scenes"].extend(extra_c3)
    chapters[3]["scenes"].extend(extra_c4)
    chapters[5]["scenes"].extend(extra_c6)
    chapters[6]["scenes"].extend(extra_c7)
    chapters[7]["scenes"].extend(extra_c8)

    global_id = 1
    for ch in chapters:
        for sc in ch["scenes"]:
            sc["scene_id"] = global_id
            global_id += 1

    total_scenes = sum(len(c["scenes"]) for c in chapters)
    total_duration = sum(sum(s["duration_sec"] for s in c["scenes"]) for c in chapters)
    word_count = sum(sum(len(s["narration"].split()) for s in c["scenes"]) for c in chapters)

    master_run_time_sec = total_duration + (len(chapters) * 8.0) + 35.0

    manifest = {
        "title": "The City of Gold and Blood: 5,000 Years of Multan",
        "subtitle": "The World's Most Besieged Fortress Documentary",
        "aspect_ratio": "16:9",
        "total_chapters": len(chapters),
        "total_scenes": total_scenes,
        "narration_duration_sec": total_duration,
        "master_runtime_min": round(master_run_time_sec / 60, 2),
        "master_runtime_sec": master_run_time_sec,
        "total_words": word_count,
        "chapters": chapters
    }

    out_path = "documentaries/multan_20min/script.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"============================================================")
    print(f"FULL 20-MINUTE MASTER DOCUMENTARY SCRIPT GENERATED:")
    print(f"  Title:             {manifest['title']}")
    print(f"  Total Chapters:    {len(chapters)}")
    print(f"  Total Scenes:      {total_scenes}")
    print(f"  Total Words:       {word_count} words")
    print(f"  Narration Time:    {total_duration/60:.2f} mins ({total_duration:.1f}s)")
    print(f"  Master Run Time:   {manifest['master_runtime_min']} minutes ({master_run_time_sec:.1f}s)")
    print(f"  Output Path:       {out_path}")
    print(f"============================================================")

if __name__ == "__main__":
    build_full_20min_manifest()
