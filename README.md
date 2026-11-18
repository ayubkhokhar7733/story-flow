# AI Storytelling Channel Automation & AI Horde Studio

A complete, production-ready system for building an automated **YouTube Storytelling Channel** with scene-by-scene AI cartoon illustrations, neural voiceover, Ken Burns dynamic motion, synchronized subtitles, and background music—using crowdsourced GPUs completely for free via **AI Horde** and **Edge-TTS**.

---

## 🎬 YouTube Story Video Pipeline Overview

Instead of downloading random stock videos from stock sites, this pipeline generates **original, scene-by-scene cartoon art** tailored to the story narrative:

1. **Intelligent Script Engine (`core/script_engine.py`)**:
   - Generates high-retention hooks and storytelling structures without lazy AI clichés.
   - Enforces **character consistency**: defines a visual character anchor (e.g. *"A small boy with messy brown hair in a bright yellow raincoat with a glowing blue lantern"*) and injects it into every scene prompt.
   - Automatically breaks the story into 6–9 second visual scenes.
2. **AI Horde Cartoon Image Engine (`core/image_engine.py`)**:
   - Dispatches each scene prompt to top cartoon-style models (`Dreamshaper`, `Rev Animated`, `Deliberate`, `Anything v5`) across the free GPU cluster.
   - Automatically polls and downloads high-resolution illustration assets.
3. **Neural Voiceover & Subtitles (`core/tts_engine.py`)**:
   - Uses Microsoft Edge-TTS neural voices (`en-US-ChristopherNeural`, `en-US-GuyNeural`, `en-GB-RyanNeural`, etc.).
   - Measures exact audio durations for each scene and synchronizes them with the images.
   - Generates clean, broadcast-style 3–5 word phrase subtitles (`subtitles.srt`).
4. **Cinematic Video Composer (`core/video_composer.py`)**:
   - Renders 1080p Full HD (1920x1080, 16:9 widescreen) at 30fps.
   - Applies the **Ken Burns effect** (smooth camera zoom-in, zoom-out, pan-left, and pan-right) to each cartoon scene so static illustrations feel alive.
   - Burns in high-contrast lower-third subtitles.
   - Mixes and ducks background music (`assets/music/background.wav`) at -20dB under the voiceover.
   - Exports YouTube-ready `.mp4` into `output/`.

---

## 📁 Project Structure

```
story-flow/
├── generate_story_video.py    # Master Storytelling Video CLI runner
├── config.py                  # Global settings, voices, art styles & audio volume
├── core/
│   ├── script_engine.py       # Scene-by-scene script generator & prompt engineer
│   ├── image_engine.py        # Cartoon image generation via AI Horde
│   ├── tts_engine.py          # Edge-TTS narrator & phrase-level subtitles
│   └── video_composer.py      # FFmpeg Ken Burns compositor & audio ducking
├── assets/
│   ├── fonts/                 # Clean typography for subtitles
│   └── music/                 # Atmospheric background music (background.wav)
├── output/                    # Final rendered 1080p MP4 videos
├── temp/                      # Working folder for audio, images & chunks
├── src/
│   ├── ai-horde-client.js     # Reusable AI Horde SDK
│   ├── server.js              # Express API Server + SSE real-time stream
│   └── public/                # Web Studio Dashboard (Story Maker, Image, Text, Models)
├── .env                       # Environment configuration
└── package.json
```

---

## 🚀 How to Create Videos

### Option A: Via the Web Dashboard (Interactive)
1. Open **[http://localhost:3000](http://localhost:3000)** in your browser.
2. Click the **"🎬 Story Video Maker"** tab.
3. Enter a story topic (or click **"🎲 Story Ideas"**).
4. Select a duration (e.g. `30s (Test Short)`, `60s (Short)`, `3 mins`, or `10-20 mins`).
5. Choose your narrator voice (e.g. Christopher, Guy, Jenny, Ryan).
6. Click **"Generate Story Video (1080p)"**:
   - Watch the live execution log as scenes, cartoon art, and voiceover are generated.
   - Preview the finished video right inside the browser video player.
   - Click **"Download 1080p Video"** to save your file.

### Option B: Via Command Line (Automated / Headless)
```bash
# 1. Generate a quick 30-second test video
python generate_story_video.py --topic "The Boy and the Whispering Star" --duration 30

# 2. Generate a 60-second YouTube Short with British storytelling voice
python generate_story_video.py --topic "The Clockwork Dragon Who Guarded a Tiny Flower" --duration 60 --voice ryan

# 3. Scale up to longer stories (e.g. 300 seconds / 5 minutes)
python generate_story_video.py --topic "The Legendary Samurai and the Moonlight Deer" --duration 300 --voice christopher
```

---

## 📈 Scaling from Short Test Videos to 15–20 Minute Long-Form Videos

To produce 15 to 20 minute videos that hold viewer retention:
1. **Multi-Chapter Structure**: Long stories are split into 3–4 chapters (e.g. Act I: The Calling & The Mystery, Act II: The Perilous Journey & Trials, Act III: The Climax, Act IV: The Resolution & Wisdom).
2. **Batch Image Generation**: When generating 80–120 scenes for a 20-minute video, the pipeline automatically submits image jobs in batches to the crowdsourced cluster so you don't stall.
3. **Pacing**: Keeping scenes at 6–9 seconds each ensures viewer eyes never get bored, creating high average percentage viewed (APV) on YouTube.

---

## 🌟 Key Features

- **100% Free / Anonymous by Default**: Uses the official `0000000000` anonymous key without requiring payment or credit cards.
- **Account & Priority Ready**: Instantly override with your personal AI Horde API key via `AI_HORDE_API_KEY` for faster priority via Kudos.
- **Dynamic Model Discovery**: Queries `GET /status/models` to discover active workers and route requests to models with live GPUs.
- **Free-Tier Constraints**: Optimized defaults (`512x512`, `20-25 steps`, `sampler: k_euler_a`) to ensure zero-kudos requests are accepted and fulfilled promptly.
- **Robust Polling & Resilience**:
  - Automatic `HTTP 429` rate limit detection with exponential backoff & retry.
  - Live progress monitoring (`queue_position`, `wait_time`, `processing` state).
  - Configurable timeouts (3 minutes default) and abort controller support.
- **Dual Interface**:
  - **Reusable SDK (`src/ai-horde-client.js`)**: Importable into any Node.js/JavaScript workflow.
  - **Live Web Studio (`http://localhost:3000`)**: Interactive UI with live queue tracking, model explorer, and asset viewer.

---

## 📁 Project Structure

```
story-flow/
├── src/
│   ├── ai-horde-client.js     # Reusable AI Horde SDK & Service Module
│   ├── server.js              # Express API Server + SSE progress stream
│   └── public/
│       ├── index.html         # Web Studio Dashboard
│       ├── style.css          # Dark-mode UI styles
│       └── app.js             # Frontend client with live SSE tracking
├── examples/
│   ├── generate-image.js      # CLI Image generation script
│   ├── generate-text.js       # CLI Text (LLM) generation script
│   └── discover-models.js     # CLI Model discovery script
├── .env.example               # Environment template
├── .env                       # Active environment variables
└── package.json
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment (`.env`)
```ini
# Default 0000000000 for anonymous free usage; or paste your registered API key
AI_HORDE_API_KEY=0000000000

# Base URL for AI Horde v2 API
AI_HORDE_BASE_URL=https://aihorde.net/api/v2

# Required identifier to prevent aggressive rate limiting
AI_HORDE_CLIENT_AGENT=StoryFlow:1.0.0:dev@localhost

PORT=3000
```

### 3. Launch the Interactive Web Studio
```bash
npm start
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser to:
- Enter prompts and watch live queue positions (`#250` &rarr; `#15` &rarr; `#0`) and countdowns.
- Explore active cluster models and worker counts in real time.
- Download generated images directly as WebP or copy text completions.

---

## 💻 CLI Examples

### Discover Active Models
```bash
npm run example:models
```

### Generate an Image
```bash
node examples/generate-image.js "A cybernetic wolf with neon blue accents standing on a snow mountain peak, 8k"
```

### Generate Text (LLM)
```bash
node examples/generate-text.js "Explain why decentralized GPU computing is powerful in 2 sentences:"
```

---

## 🛠️ Programmatic Usage (SDK)

### Import and Initialize
```javascript
import { AiHordeClient } from './src/ai-horde-client.js';

const horde = new AiHordeClient({
  apiKey: process.env.AI_HORDE_API_KEY || '0000000000',
  clientAgent: 'MyApp:1.0.0:dev@localhost',
});
```

---

### Image Generation (`generateImage`)
```javascript
const result = await horde.generateImage(
  {
    prompt: 'A cyberpunk tea house floating in space, digital concept art',
    negativePrompt: 'blurry, low quality, deformed',
    models: ['stable_diffusion'],
    params: {
      width: 512,        // Free tier recommended: 512
      height: 512,       // Free tier recommended: 512
      steps: 20,         // Free tier recommended: 20-25
      sampler_name: 'k_euler_a',
      cfg_scale: 7.5,
    },
    r2: true,            // Direct Cloudflare R2 hosted URL
    nsfw: false,
    censor_nsfw: true,
  },
  // Real-time progress callback
  (progress) => {
    if (progress.step === 'polling') {
      console.log(`Queue: #${progress.queue_position} | Est. wait: ${progress.wait_time}s | GPU: ${progress.processing ? 'Rendering' : 'Queued'}`);
    }
  }
);

console.log('Image URL:', result.imageUrl);
console.log('Seed:', result.seed);
console.log('Worker:', result.workerName);
```

---

### Text Generation (`generateText`)
```javascript
const textResult = await horde.generateText(
  {
    prompt: 'Write 3 YouTube hook titles for a video about AI automation:',
    models: ['koboldcpp/Llama-3.2-3B-Instruct-Q4_K_M'], // Optional: omit to use any available
    params: {
      max_length: 200,
      temperature: 0.7,
    },
  },
  (progress) => {
    console.log(`Queue pos: #${progress.queue_position} | Est. wait: ${progress.wait_time}s`);
  }
);

console.log('Generated Output:\n', textResult.text);
console.log('Worker:', textResult.workerName);
```

---

### Dynamic Model Discovery (`getModels`)
```javascript
// Get top image models sorted by active GPU worker count
const imageModels = await horde.getActiveImageModels();
console.log('Top model:', imageModels[0].name, 'Workers:', imageModels[0].count);

// Get top text models sorted by active GPU worker count
const textModels = await horde.getActiveTextModels();
console.log('Top text model:', textModels[0].name, 'Workers:', textModels[0].count);
```

---

## 📡 API Endpoints (Express Server)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Heartbeat & client configuration status |
| `GET` | `/api/user` | Account info & Kudos balance |
| `POST` | `/api/config/key` | Set / validate custom Horde API Key |
| `GET` | `/api/models?type=image\|text` | Active models sorted by worker availability |
| `POST` | `/api/generate/image` | Dispatch async image generation job |
| `GET` | `/api/generate/image/:id/check` | Poll image queue position & wait time |
| `GET` | `/api/generate/image/:id/result` | Retrieve completed image asset |
| `GET` | `/api/generate/image/:id/stream` | Server-Sent Events (SSE) live progress stream |
| `POST` | `/api/generate/text` | Dispatch async text generation job |
| `GET` | `/api/generate/text/:id/status` | Poll text status / retrieve completed text |
| `GET` | `/api/generate/text/:id/stream` | Server-Sent Events (SSE) live progress stream |

---

## 🛡️ Best Practices for Zero-Kudos / Free Tier

1. **Keep Dimensions At 512x512**: Larger resolutions (e.g. 1024x1024) cost significantly more kudos and may be rejected or sit in the queue much longer on anonymous keys.
2. **Steps between 20 and 25**: Sufficient for high quality while keeping generation time under 15 seconds once picked up by a worker GPU.
3. **Always set `Client-Agent`**: Required by AI Horde to prevent automatic IP bans and aggressive 429 throttling.
4. **Use Multi-Model Lists or Dynamic Discovery**: Providing multiple compatible models (or auto-discovering ones with ETA &le; 10s) allows the coordinator to assign your request to whichever GPU becomes free first.

---

## ⚡ Cloud Video Generation via GitHub Actions

This repository includes a completely autonomous **GitHub Actions Workflow** (`.github/workflows/generate-story-video.yml`) that creates and renders Full HD videos on GitHub's cloud runners for free:

1. Go to your repository on GitHub.
2. Click the **Actions** tab.
3. Select **Generate AI Story Video** and click **Run workflow**.
4. Configure your parameters:
   - **Topic**: e.g. `The Lost City of Harappa` or `The Clockwork Guardian`
   - **Format**: `9:16` (Vertical Shorts/Reels) or `16:9` (Widescreen)
   - **Voice**: `asad` / `uzma` (Urdu), `christopher` / `guy` / `jenny` (English)
   - **Duration**: `60` seconds
5. Click **Run workflow**. In 3-4 minutes, your complete `.mp4` video will be generated and available under the **Artifacts** section!

