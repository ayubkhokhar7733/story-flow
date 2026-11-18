import json
import os

chapters = [
    {
        "chapter_id": 1,
        "title": "Prologue: The City Empires Bled For",
        "scenes": [
            {
                "scene_id": 1,
                "narration": "Before Rome was ruled by emperors, before the great walls of Babylon crumbled into dust, there stood a golden citadel in the fertile heart of the Punjab.",
                "visual_prompt": "cinematic historical establishing shot, ancient walled citadel of Multan rising atop a colossal earth mound, golden sunrise casting deep shadows across ancient baked brick bastions, atmospheric morning mist, birds soaring, epic cinematic matte painting, 8k resolution",
                "duration_sec": 9.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 2,
                "narration": "For more than five thousand unbroken years, the city of Multan has stood at the crossroads of human conquest, culture, and trade.",
                "visual_prompt": "aerial wide angle panoramic view of ancient Multan, sprawling bazaar streets, high fortress walls, convergence of Chenab and Ravi rivers on the distant horizon, ancient trade caravans approaching the grand gate, photorealistic historical painting",
                "duration_sec": 8.5,
                "motion": "pan_right"
            },
            {
                "scene_id": 3,
                "narration": "It was assaulted by Alexander the Great, conquered by the Umayyads, stormed by Mahmud of Ghazni, besieged by the Mongols, and claimed by the Mughals, Sikhs, and the British Empire.",
                "visual_prompt": "dramatic montage of ancient conquerors, silhouettes of Greek phalanxes, Arab cavalry banners, Mongol horse archers, and British redcoats outside towering stone and brick fortress walls, fiery cinematic lighting, epic battle atmosphere",
                "duration_sec": 10.0,
                "motion": "zoom_out"
            },
            {
                "scene_id": 4,
                "narration": "No single city on the Indian subcontinent has witnessed more blood spilled outside its ramparts—or guarded more legendary wealth beneath its soil.",
                "visual_prompt": "underground ancient vaulted treasury, stone arches lit by flickering torches, overflowing chests of golden coins, jeweled chalices, and sacred artifacts of ancient Punjab, dark moody cinematic lighting, mystery, high detail",
                "duration_sec": 9.0,
                "motion": "pan_left"
            },
            {
                "scene_id": 5,
                "narration": "This is the epic chronicle of Multan: The City of Gold, the City of Saints, and the most besieged fortress in Asian history.",
                "visual_prompt": "dramatic title card frame, ancient illuminated bronze and lapis lazuli emblem of Multan, golden calligraphy filigree, dramatic embers drifting in the wind, cinematic dark backdrop, 8k",
                "duration_sec": 8.0,
                "motion": "zoom_in"
            }
        ]
    },
    {
        "chapter_id": 2,
        "title": "Act I: Mulasthana & The Sun Temple",
        "scenes": [
            {
                "scene_id": 6,
                "narration": "The earliest memories of Multan are lost in the mists of antiquity, known in ancient Sanskrit scriptures as Mulasthana—the original seat.",
                "visual_prompt": "mythological ancient Indian kingdom, Vedic settlement along the Chenab riverbank, priests in saffron robes performing rituals near ancient brick altars, sacred fires burning at dawn, lush river reeds, soft ethereal lighting",
                "duration_sec": 9.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 7,
                "narration": "According to legend, the city was founded by Samba, the son of Lord Krishna, who built a colossal sanctuary dedicated to Aditya, the Sun God.",
                "visual_prompt": "magnificent architectural rendering of the ancient Sun Temple of Multan, monumental carved sandstone towers, grand flight of stone stairs, golden sun disc glowing at the temple pinnacle, worshippers gathered in awe",
                "duration_sec": 9.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 8,
                "narration": "At the temple's inner sanctum sat a life-sized idol of the Sun God cast entirely in pure gold, with eyes fashioned from radiant red rubies that illuminated the sanctuary.",
                "visual_prompt": "interior of the ancient Sun Temple, colossal idol of Surya cast from solid gleaming gold, hypnotic glowing ruby eyes reflecting torchlight, incense smoke swirling around intricate stone pillars, breathtaking golden glow",
                "duration_sec": 10.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 9,
                "narration": "Pilgrims journeyed thousands of miles from Persia, Tibet, and across the subcontinent to offer vast treasures at its altar, transforming Multan into an empire of divine wealth.",
                "visual_prompt": "ancient pilgrims and merchants in diverse historical attire marching along a dust trail toward the towering temple complex, carrying offerings of silks, incense, and gold, panoramic desert landscape, majestic",
                "duration_sec": 9.5,
                "motion": "pan_right"
            },
            {
                "scene_id": 10,
                "narration": "Positioned where five major rivers converge into the Indus, Multan became the unrivaled gateway between Central Asia and the Gangetic plains.",
                "visual_prompt": "ancient map cartography table, illuminated parchment map showing the five rivers of Punjab converging, trade routes drawn in glowing gold connecting Khorasan, Multan, and Delhi, historical cartographer's compass and dividers",
                "duration_sec": 9.0,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "chapter_id": 3,
        "title": "Act II: Alexander the Great & The Mallian Massacre (326 BCE)",
        "scenes": [
            {
                "scene_id": 11,
                "narration": "In the year 326 BCE, the undefeated Macedonian conqueror Alexander the Great turned his army south along the Chenab and Ravi rivers.",
                "visual_prompt": "Alexander the Great on horseback overlooking the vast plains of Punjab, Macedonian bronze phalanx marching in disciplined formation with towering 18-foot sarissa pikes, banners fluttering in the hot desert wind, cinematic epic scale",
                "duration_sec": 9.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 12,
                "narration": "Standing directly in his path were the Malli—a fierce, fiercely independent tribe known as some of the bravest warriors in ancient India.",
                "visual_prompt": "ancient Mallian warriors standing resolute atop massive earthen ramparts, holding bronze curved swords, bows, and wicker shields, intense battle-hardened expressions, dust swirling around the battlements",
                "duration_sec": 8.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 13,
                "narration": "Frustrated by the slow pace of the siege, Alexander took a siege ladder, climbed the citadel walls himself, and leaped alone into the enemy stronghold.",
                "visual_prompt": "dramatic historical action scene, Alexander the Great in royal gilded armor leaping from the top of the citadel wall down into the fortified courtyard among enemy warriors, sword raised, dramatic sunset lighting, frozen motion",
                "duration_sec": 10.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 14,
                "narration": "Surrounded by hostile defenders with only two bodyguards, a heavy three-foot Mallian wooden arrow pierced straight through Alexander's breastplate and punctured his lung.",
                "visual_prompt": "dramatic battlefield moment, Alexander collapsing against a sacred tree inside the citadel, clutching an arrow wound to his chest, loyal bodyguard Peucestas raising the sacred shield of Athena to protect him from raining blows",
                "duration_sec": 10.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 15,
                "narration": "Believing their king had fallen, the enraged Macedonian army broke down the gates in fury, unleashing a merciless assault that leveled the fortress.",
                "visual_prompt": "Macedonian soldiers battering down the wooden gates of the citadel with a bronze battering ram, soldiers surging through the breach with shields and torches, smoke rising against the fiery evening sky, chaos and devastation",
                "duration_sec": 10.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 16,
                "narration": "Alexander miraculously survived the surgery to remove the barbed arrow, but Multan had proven that it would never surrender its freedom without catastrophic bloodshed.",
                "visual_prompt": "ancient army camp on the riverbank at night, tents illuminated by campfires, Alexander the Great resting on a couch surrounded by his top generals, looking out toward the dark silhouette of Multan's ruined walls",
                "duration_sec": 10.0,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "chapter_id": 4,
        "title": "Act III: The House of Gold & The Islamic Era",
        "scenes": [
            {
                "scene_id": 17,
                "narration": "A millennium after Alexander, in 712 CE, a seventeen-year-old Arab general named Muhammad bin Qasim led an Umayyad army into the Indus valley.",
                "visual_prompt": "Muhammad bin Qasim riding an Arabian steed at the head of a desert cavalry, emerald and white Umayyad banners waving, armored horsemen advancing across the sand dunes of Sindh towards the walls of Multan",
                "duration_sec": 9.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 18,
                "narration": "After a grueling two-month siege, the Arab forces diverted the city's water canal, forcing the garrison to negotiate terms of capitulation.",
                "visual_prompt": "historical Arab siege camp, engineers diverting a stone-lined irrigation canal, dry moat beneath the colossal battlements, defenders on the towers watching in despair, high historical realism",
                "duration_sec": 9.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 19,
                "narration": "Inside the citadel, the conquerors uncovered an astonishing secret: a subterranean vault filled with so many tons of pure gold that Qasim named the city 'Faraj Bayt al-Dhahab'—The Frontier House of Gold.",
                "visual_prompt": "Arab soldiers and scholars holding oil lamps entering a subterranean stone vault beneath the citadel, massive clay jars and chests overflowing with gold ingots, ancient coins, and jewelry glittering in the torchlight",
                "duration_sec": 10.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 20,
                "narration": "For the next three centuries, Multan flourished as an independent Islamic emirate, issuing its own coinage and maintaining diplomacy with Baghdad, Cairo, and China.",
                "visual_prompt": "bustling medieval Islamic bazaar in Multan, merchants in turbans and silks trading spices, engraved gold dinar coins resting on a scales balance, arched porticos with blue ceramic tilework, vibrant medieval civilization",
                "duration_sec": 9.5,
                "motion": "pan_right"
            },
            {
                "scene_id": 21,
                "narration": "By the late 10th century, the city came under the rule of the Ismaili Qarmatians, creating a unique syncretic haven of intellectual dialogue and international commerce.",
                "visual_prompt": "medieval scholars and astronomers gathered in an open courtyard in Multan, studying celestial astrolabes and Arabic manuscripts under the starry night sky, serene Islamic architecture, reflecting pools",
                "duration_sec": 9.0,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "chapter_id": 5,
        "title": "Act IV: The Invasions of Fire & The Mongol Shield",
        "scenes": [
            {
                "scene_id": 22,
                "narration": "Peace was shattered in 1005 CE when Sultan Mahmud of Ghazni swept down from the Afghan mountains with cold military precision.",
                "visual_prompt": "Mahmud of Ghazni's ferocious army advancing across snow-dusted mountain passes toward the Punjab plains, armored cavalry with curved scimitars and war drums, dark storm clouds gathering, ominous cinematic lighting",
                "duration_sec": 9.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 23,
                "narration": "Mahmud besieged Multan twice, dismantling its Ismaili ruler and absorbing the city into the sprawling Ghaznavid empire as a royal military garrison.",
                "visual_prompt": "Ghaznavid siege engines, catapults hurling flaming boulders against the thick brick bastions of Multan's citadel, smoke billows rising above the battlements, intense siege warfare",
                "duration_sec": 9.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 24,
                "narration": "Two centuries later, a far deadlier menace emerged from the steppes of Central Asia: the unstoppable armies of Genghis Khan and his successors.",
                "visual_prompt": "terrifying Mongol cavalry horde galloping across the arid steppe, fur-trimmed armor, composite bows drawn, banners with horse-tail totems, dust clouds blocking out the sun, apocalyptic historical scale",
                "duration_sec": 9.5,
                "motion": "pan_right"
            },
            {
                "scene_id": 25,
                "narration": "Multan was chosen by the Delhi Sultanate as the northern bastion of South Asia—the fortress that had to hold, or the entire subcontinent would burn.",
                "visual_prompt": "Sultan Balban and his generals planning military strategy over a relief map of Multan's fortifications, armored guards standing at attention with shields, heavy iron gates reinforced with spikes",
                "duration_sec": 9.0,
                "motion": "zoom_out"
            },
            {
                "scene_id": 26,
                "narration": "In 1285, Prince Muhammad Sultan, the beloved heir to Delhi's throne, gave his life on the battlefields outside Multan repelling a massive Mongol horde.",
                "visual_prompt": "heroic last stand on the battlefield of Multan, Prince Muhammad Sultan fighting bravely amidst a storm of arrows, fallen warriors, sunset sky soaked in crimson, tragic and epic historical painting",
                "duration_sec": 10.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 27,
                "narration": "Though the prince fell, the fortress of Multan held firm, saving northern India from the complete annihilation that had devastated Baghdad and Persia.",
                "visual_prompt": "Multan citadel battlements standing intact and defiant at twilight, smoke clearing over the battle plains below, guards patrolling the high walls, solemn resilience, cinematic mastery",
                "duration_sec": 9.5,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "chapter_id": 6,
        "title": "Act V: The City of Saints & Kashigari Blue",
        "scenes": [
            {
                "scene_id": 28,
                "narration": "Exhausted by centuries of invasion and bloodshed, the soul of Multan underwent an extraordinary spiritual renaissance.",
                "visual_prompt": "peaceful sunrise illuminating the skyline of Multan, morning mist rising over brick domes and terracotta minarets, a flock of white doves gliding across the sky, tranquil spiritual mood",
                "duration_sec": 8.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 29,
                "narration": "Sufi masters and mystics arrived from Baghdad, Central Asia, and Persia, preaching universal love, tolerance, and inner harmony.",
                "visual_prompt": "venerable Sufi saint seated under the shade of an ancient banyan tree in Multan, surrounded by diverse disciples listening in quiet contemplation, gentle golden sunlight filtering through leaves",
                "duration_sec": 9.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 30,
                "narration": "Foremost among them was Sheikh Bahauddin Zakariya, who founded one of the greatest educational and spiritual centers in the Islamic world.",
                "visual_prompt": "historic Islamic madrasah courtyard of Bahauddin Zakariya in Multan, students seated on carpets studying manuscripts, arched colonnades, calm reflecting fountain, intricate terracotta brickwork",
                "duration_sec": 9.5,
                "motion": "pan_right"
            },
            {
                "scene_id": 31,
                "narration": "Beside him rose the towering tomb of his grandson, Shah Rukn-e-Alam—a masterwork of medieval architecture that remains the crown jewel of Multan.",
                "visual_prompt": "majestic high angle view of the Tomb of Shah Rukn-e-Alam, colossal octagonal sloping three-tier terracotta mausoleum, crowning white hemispherical dome, glowing at golden hour, architectural grandeur",
                "duration_sec": 10.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 32,
                "narration": "The shrine was decorated with Kashigari—intricate handcrafted glazed tiles in brilliant cobalt blue, turquoise, and white, making Multan world-famous as the Blue City.",
                "visual_prompt": "extreme close-up of traditional Multani Kashigari artisans hand-painting floral geometric motifs on glazed blue tiles, vibrant turquoise and cobalt pigments, delicate calligraphy, master craftsmanship",
                "duration_sec": 9.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 33,
                "narration": "Constructed with ingenious wood-and-brick interlocking joints, the monument has survived devastating earthquakes for over seven hundred years without a single crack.",
                "visual_prompt": "architectural cross-section illustration showing the interlocking shisham wood beams embedded inside the thick terracotta brick walls of Shah Rukn-e-Alam, engineering genius of medieval artisans",
                "duration_sec": 9.5,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "chapter_id": 7,
        "title": "Act VI: Empires Clash: Mughals, Afghans & Ranjit Singh",
        "scenes": [
            {
                "scene_id": 34,
                "narration": "Under the Mughal Empire in the 16th and 17th centuries, Multan enjoyed unprecedented tranquility and wealth as one of the empire's wealthiest provinces.",
                "visual_prompt": "Mughal era royal court in Multan, Emperor Akbar's governor seated under an embroidered canopy, courtiers in elaborate silk robes presenting tax revenues and trade goods, opulent Mughal court aesthetics",
                "duration_sec": 9.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 35,
                "narration": "The tragic philosopher-prince Dara Shikoh served as its governor, translating ancient sacred texts into Persian and celebrating Multan's culture of tolerance.",
                "visual_prompt": "Prince Dara Shikoh in exquisite Mughal attire seated in a riverside pavilion library overlooking the Chenab, studying Sanskrit and Persian manuscripts together with Hindu and Muslim scholars",
                "duration_sec": 10.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 36,
                "narration": "As the Mughal Empire waned, Multan was seized by the Afghan conqueror Ahmad Shah Durrani, returning the city to turbulent frontline warfare.",
                "visual_prompt": "Afghan Durrani cavalry riding through the arched gates of Multan, turbans with long tail feathers, matchlock rifles, rugged mountain warriors taking command of the fortress battlements",
                "duration_sec": 9.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 37,
                "narration": "By the early 19th century, the rising power of Maharaja Ranjit Singh's Sikh Empire set its sights on the legendary fortress.",
                "visual_prompt": "Maharaja Ranjit Singh, the Lion of Punjab, inspecting his royal Sikh army, golden armored cavalry, Nihang warriors with blue garments and tall turbans carrying steel chakrams, formidable military review",
                "duration_sec": 9.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 38,
                "narration": "Ranjit Singh launched no fewer than six separate sieges, each repelled by the resolute Afghan governor Nawab Muzaffar Khan.",
                "visual_prompt": "dramatic siege battle outside Multan, Sikh artillery battery firing volleys against the high stone walls, smoke obscuring the bastions, Nawab Muzaffar Khan leading defenders from the ramparts with drawn sword",
                "duration_sec": 10.0,
                "motion": "pan_left"
            },
            {
                "scene_id": 39,
                "narration": "In the decisive seventh siege of 1818, Ranjit Singh brought up the monstrous bronze cannon 'Zamzama'—also known as Kim's Gun.",
                "visual_prompt": "the colossal historic bronze cannon Zamzama, deeply engraved barrel, being positioned by Sikh artillerymen on wooden ramparts aiming directly at the fortified walls of Multan, immense historical weight",
                "duration_sec": 9.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 40,
                "narration": "After firing massive eighty-pound iron balls that finally shattered the citadel gates, Nawab Muzaffar Khan died sword in hand alongside his sons, and Multan fell to the Sikh Empire.",
                "visual_prompt": "heroic final stand at the breached gate of Multan, Nawab Muzaffar Khan and his sons fighting valiantly against overwhelming odds amidst shattered timber and cannon smoke, tragic cinematic lighting",
                "duration_sec": 10.5,
                "motion": "zoom_out"
            }
        ]
    },
    {
        "chapter_id": 8,
        "title": "Act VII: The Gunpowder Cataclysm & The British Empire",
        "scenes": [
            {
                "scene_id": 41,
                "narration": "Three decades later, in 1848, the British East India Company demanded the submission of Multan's governor, Dewan Mulraj.",
                "visual_prompt": "British officers in red uniforms with brass buttons negotiating with Dewan Mulraj and his Sikh and Punjabi ministers inside the grand audience hall of the Multan citadel, tense political standoff",
                "duration_sec": 9.5,
                "motion": "pan_left"
            },
            {
                "scene_id": 42,
                "narration": "When two British emissaries were killed outside the fortress, Dewan Mulraj raised the standard of open rebellion, sparking the Second Anglo-Sikh War.",
                "visual_prompt": "Dewan Mulraj hoisting his battle flag atop the citadel tower, thousands of Punjabi soldiers and citizens raising swords in defiant revolt against colonial rule, dramatic dust storm rising",
                "duration_sec": 9.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 43,
                "narration": "A massive British and allied army surrounded the city with heavy siege howitzers, bombarding the citadel day and night with relentless explosive shells.",
                "visual_prompt": "British artillery batteries arrayed in siege trenches outside Multan, heavy siege mortars firing explosive shells into the sky, night illuminated by arcs of tracer fire and bursting detonations over the city",
                "duration_sec": 10.0,
                "motion": "pan_right"
            },
            {
                "scene_id": 44,
                "narration": "On December 30th, 1848, a British mortar shell scored a direct hit on the citadel's central magazine—housing over five hundred thousand pounds of stored gunpowder.",
                "visual_prompt": "cinematic climax, a lone mortar shell arcing across the sky and dropping through the roof of the central citadel dome, interior spark igniting massive stacked barrels of black gunpowder",
                "duration_sec": 10.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 45,
                "narration": "The resulting explosion was so catastrophic it shook the earth for thirty miles, hurling thousands of tons of stone, brick, and dust thousands of feet into the sky.",
                "visual_prompt": "colossal apocalyptic explosion mushroom cloud rising over the citadel of Multan, massive shockwave tearing through ancient masonry, smoke blocking out the sun, debris raining across the plains",
                "duration_sec": 10.5,
                "motion": "zoom_out"
            },
            {
                "scene_id": 46,
                "narration": "In January 1849, Dewan Mulraj surrendered the shattered fortress, and Multan was formally annexed into the British Raj.",
                "visual_prompt": "Dewan Mulraj surrendering his sword to British General Whish amidst the rubble and ruins of the breached citadel, Union Jack raised over the smoldering ramparts, historic Victorian photography aesthetic",
                "duration_sec": 9.5,
                "motion": "pan_left"
            }
        ]
    },
    {
        "chapter_id": 9,
        "title": "Epilogue: Where History Still Breathes",
        "scenes": [
            {
                "scene_id": 47,
                "narration": "The British rebuilt the city, constructing the iconic clock tower of Ghanta Ghar upon the ancient foundations of the fortress mound.",
                "visual_prompt": "Victorian Indo-Saracenic Ghanta Ghar clock tower of Multan standing proud in the golden afternoon light, horse carriages and early 20th century street scene, bustling cultural crossroads",
                "duration_sec": 9.0,
                "motion": "zoom_in"
            },
            {
                "scene_id": 48,
                "narration": "Today, Multan stands as an eternal monument to human resilience. Thirty sieges could not break it. Ten empires could not erase it.",
                "visual_prompt": "stunning modern aerial twilight drone view of Multan, ancient illuminated shrines of Shah Rukn-e-Alam and Bahauddin Zakariya glowing like beacons above the vibrant modern city lights, awe-inspiring",
                "duration_sec": 9.5,
                "motion": "pan_right"
            },
            {
                "scene_id": 49,
                "narration": "In its winding alleys, fragrant spice markets, and celestial blue tilework, the heart of five thousand years of history still beats unbroken.",
                "visual_prompt": "cinematic slow tracking shot through an ancient Multan street at dusk, warm lanterns glowing, artisans crafting blue pottery, children laughing, timeless poetry and eternal soul of the city",
                "duration_sec": 9.5,
                "motion": "zoom_in"
            },
            {
                "scene_id": 50,
                "narration": "For as long as the rivers of Punjab flow to the sea, Multan will remain what it has always been: the unconquerable City of Gold and Saints.",
                "visual_prompt": "breathtaking closing cinematic shot, wide sunset panorama of the ancient citadel mound against an indigo and gold sky, the Chenab river glistening in the foreground, epic documentary finale",
                "duration_sec": 10.0,
                "motion": "zoom_out"
            }
        ]
    }
]

total_scenes = sum(len(c["scenes"]) for c in chapters)
total_duration = sum(sum(s["duration_sec"] for s in c["scenes"]) for c in chapters)
word_count = sum(sum(len(s["narration"].split()) for s in c["scenes"]) for c in chapters)

manifest = {
    "title": "The City of Gold and Blood: 5,000 Years of Multan",
    "subtitle": "The World's Most Besieged Fortress Documentary",
    "aspect_ratio": "16:9",
    "total_chapters": len(chapters),
    "total_scenes": total_scenes,
    "estimated_duration_sec": total_duration,
    "word_count": word_count,
    "chapters": chapters
}

out_path = "documentaries/multan_20min/script.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Generated master documentary script:")
print(f"  Title: {manifest['title']}")
print(f"  Total Chapters: {len(chapters)}")
print(f"  Total Scenes: {total_scenes}")
print(f"  Total Duration: {total_duration/60:.2f} minutes ({total_duration:.1f}s)")
print(f"  Total Words: {word_count}")
print(f"  Saved to: {out_path}")
