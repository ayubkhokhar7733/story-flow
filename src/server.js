import 'dotenv/config';
import express from 'express';
import path from 'node:path';
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { AiHordeClient } from './ai-horde-client.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.join(__dirname, '..');

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use('/videos', express.static(path.join(projectRoot, 'output')));

// Initialize AI Horde Client
let hordeClient = new AiHordeClient();

// In-memory active SSE connections or abort signals if needed
const activeJobs = new Map();

// ==========================================
// API Routes
// ==========================================

/**
 * Service heartbeat & client configuration status
 */
app.get('/api/status', async (req, res) => {
  try {
    const heartbeat = await hordeClient.getHordeStatus().catch(() => ({ msg: 'Horde reachable' }));
    res.json({
      status: 'ok',
      clientAgent: hordeClient.clientAgent,
      baseUrl: hordeClient.baseUrl,
      isAnonymous: hordeClient.apiKey === '0000000000',
      heartbeat,
    });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

/**
 * Current user / Kudos balance
 */
app.get('/api/user', async (req, res) => {
  try {
    const user = await hordeClient.getUserInfo();
    res.json({
      username: user.username,
      kudos: user.kudos,
      workerCount: user.worker_count,
      records: user.records,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/**
 * Configure API Key dynamically
 */
app.post('/api/config/key', async (req, res) => {
  const { apiKey } = req.body;
  const newKey = (apiKey && apiKey.trim()) ? apiKey.trim() : '0000000000';

  try {
    // Validate key with Horde
    const user = await hordeClient.getUserInfo(newKey);
    hordeClient = new AiHordeClient({
      apiKey: newKey,
      baseUrl: hordeClient.baseUrl,
      clientAgent: hordeClient.clientAgent,
    });

    res.json({
      success: true,
      username: user.username,
      kudos: user.kudos,
      isAnonymous: newKey === '0000000000',
    });
  } catch (err) {
    res.status(400).json({ success: false, error: `Invalid key or Horde error: ${err.message}` });
  }
});

/**
 * Fetch active models (sorted by worker count)
 */
app.get('/api/models', async (req, res) => {
  try {
    const type = req.query.type === 'text' ? 'text' : 'image';
    const models = await hordeClient.getModels({ type, onlyActive: true });
    res.json(models);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ------------------------------------------
// Image Generation Endpoints
// ------------------------------------------

/**
 * Dispatch image generation job
 */
app.post('/api/generate/image', async (req, res) => {
  try {
    const { prompt, negativePrompt, models, params, nsfw } = req.body;
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required.' });
    }

    const submitResult = await hordeClient.submitImageGeneration({
      prompt,
      negativePrompt,
      models: models && models.length > 0 ? models : ['stable_diffusion'],
      params: {
        width: Number(params?.width || 512),
        height: Number(params?.height || 512),
        steps: Number(params?.steps || 20),
        sampler_name: params?.sampler_name || 'k_euler_a',
        cfg_scale: Number(params?.cfg_scale || 7.5),
        seed: params?.seed || undefined,
      },
      nsfw: Boolean(nsfw ?? false),
      censor_nsfw: !Boolean(nsfw),
      r2: true,
    });

    res.json(submitResult);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
});

/**
 * Check image generation poll status
 */
app.get('/api/generate/image/:id/check', async (req, res) => {
  try {
    const check = await hordeClient.checkImageStatus(req.params.id);
    res.json(check);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
});

/**
 * Fetch finished image asset
 */
app.get('/api/generate/image/:id/result', async (req, res) => {
  try {
    const result = await hordeClient.getImageResult(req.params.id);
    res.json(result);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
});

/**
 * Server-Sent Events (SSE) stream for real-time image progress
 */
app.get('/api/generate/image/:id/stream', async (req, res) => {
  const jobId = req.params.id;

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const sendEvent = (event, data) => {
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };

  sendEvent('connected', { jobId, message: 'Subscribed to job updates' });

  let isClosed = false;
  req.on('close', () => {
    isClosed = true;
  });

  const startTime = Date.now();
  const timeoutMs = 180000; // 3 minutes

  while (!isClosed) {
    try {
      if (Date.now() - startTime > timeoutMs) {
        sendEvent('error', { message: 'Image generation timed out after 3 minutes.' });
        res.end();
        break;
      }

      const check = await hordeClient.checkImageStatus(jobId);
      const elapsed = Math.round((Date.now() - startTime) / 1000);

      sendEvent('progress', {
        jobId,
        done: check.done,
        faulted: check.faulted,
        wait_time: check.wait_time ?? 0,
        queue_position: check.queue_position ?? 0,
        processing: check.processing ?? 0,
        finished: check.finished ?? 0,
        waiting: check.waiting ?? 0,
        is_possible: check.is_possible ?? true,
        elapsed,
      });

      if (check.faulted) {
        sendEvent('error', { message: 'Image job faulted on worker.' });
        res.end();
        break;
      }

      if (check.done) {
        const finalAsset = await hordeClient.getImageResult(jobId);
        sendEvent('completed', {
          jobId,
          result: finalAsset,
          elapsed,
        });
        res.end();
        break;
      }

      await new Promise((resolve) => setTimeout(resolve, 3000));
    } catch (err) {
      if (!isClosed) {
        sendEvent('error', { message: err.message });
        res.end();
      }
      break;
    }
  }
});

// ------------------------------------------
// Text Generation Endpoints
// ------------------------------------------

/**
 * Dispatch text generation job
 */
app.post('/api/generate/text', async (req, res) => {
  try {
    const { prompt, models, params } = req.body;
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required.' });
    }

    const submitResult = await hordeClient.submitTextGeneration({
      prompt,
      models: models && models.length > 0 ? models : undefined,
      params: {
        max_length: Number(params?.max_length || 250),
        max_context_length: Number(params?.max_context_length || 2048),
        temperature: Number(params?.temperature || 0.7),
        top_p: Number(params?.top_p || 0.9),
      },
    });

    res.json(submitResult);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
});

/**
 * Check text generation poll status
 */
app.get('/api/generate/text/:id/status', async (req, res) => {
  try {
    const status = await hordeClient.checkTextStatus(req.params.id);
    res.json(status);
  } catch (err) {
    res.status(err.statusCode || 500).json({ error: err.message });
  }
});

/**
 * Server-Sent Events (SSE) stream for real-time text progress
 */
app.get('/api/generate/text/:id/stream', async (req, res) => {
  const jobId = req.params.id;

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const sendEvent = (event, data) => {
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };

  sendEvent('connected', { jobId, message: 'Subscribed to text job updates' });

  let isClosed = false;
  req.on('close', () => {
    isClosed = true;
  });

  const startTime = Date.now();
  const timeoutMs = 180000;

  while (!isClosed) {
    try {
      if (Date.now() - startTime > timeoutMs) {
        sendEvent('error', { message: 'Text generation timed out after 3 minutes.' });
        res.end();
        break;
      }

      const status = await hordeClient.checkTextStatus(jobId);
      const elapsed = Math.round((Date.now() - startTime) / 1000);

      sendEvent('progress', {
        jobId,
        done: status.done,
        faulted: status.faulted,
        wait_time: status.wait_time ?? 0,
        queue_position: status.queue_position ?? 0,
        processing: status.processing ?? 0,
        finished: status.finished ?? 0,
        waiting: status.waiting ?? 0,
        elapsed,
      });

      if (status.faulted) {
        sendEvent('error', { message: 'Text job faulted on worker.' });
        res.end();
        break;
      }

      if (status.done) {
        sendEvent('completed', {
          jobId,
          result: status,
          elapsed,
        });
        res.end();
        break;
      }

      await new Promise((resolve) => setTimeout(resolve, 3000));
    } catch (err) {
      if (!isClosed) {
        sendEvent('error', { message: err.message });
        res.end();
      }
      break;
    }
  }
});

// ------------------------------------------
// Storytelling Video Channel Endpoints
// ------------------------------------------

/**
 * List generated story videos
 */
app.get('/api/story/videos', (req, res) => {
  const outputDir = path.join(projectRoot, 'output');
  if (!fs.existsSync(outputDir)) {
    return res.json([]);
  }

  const files = fs.readdirSync(outputDir)
    .filter((f) => f.endsWith('.mp4'))
    .map((filename) => {
      const filePath = path.join(outputDir, filename);
      const stat = fs.statSync(filePath);
      return {
        filename,
        url: `/videos/${encodeURIComponent(filename)}`,
        sizeMb: (stat.size / (1024 * 1024)).toFixed(2),
        createdAt: stat.birthtime,
      };
    })
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  res.json(files);
});

/**
 * Real-time SSE Story Video Generation Pipeline
 */
app.get('/api/story/stream', (req, res) => {
  const topic = req.query.topic || 'The Boy and the Whispering Star';
  const duration = parseInt(req.query.duration || '60', 10);
  const voice = req.query.voice || 'christopher';
  const aspect = req.query.aspect || '9:16';

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const sendEvent = (event, data) => {
    res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
  };

  sendEvent('log', { message: `🎬 Initializing Storytelling Pipeline for "${topic}" (~${duration}s, format: ${aspect})...` });

  const pyScript = path.join(projectRoot, 'generate_story_video.py');
  const pyProcess = spawn('python', ['-u', pyScript, '--topic', topic, '--duration', String(duration), '--voice', voice, '--aspect', aspect], {
    cwd: projectRoot,
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
  });

  let videoPath = null;

  pyProcess.stdout.on('data', (data) => {
    const text = data.toString('utf-8');
    const lines = text.split('\n').filter((l) => l.trim().length > 0);
    for (const line of lines) {
      sendEvent('log', { message: line.trim() });
      if (line.includes('Output File:')) {
        videoPath = line.split('Output File:')[1].trim();
      }
    }
  });

  pyProcess.stderr.on('data', (data) => {
    sendEvent('log', { message: `[stderr] ${data.toString('utf-8').trim()}` });
  });

  pyProcess.on('close', (code) => {
    if (code === 0 && videoPath) {
      const filename = path.basename(videoPath);
      sendEvent('completed', {
        filename,
        videoUrl: `/videos/${encodeURIComponent(filename)}`,
        message: 'Story video successfully rendered!',
      });
    } else {
      sendEvent('error', { message: `Process exited with code ${code}` });
    }
    res.end();
  });

  req.on('close', () => {
    pyProcess.kill();
  });
});

// Start Express server on 0.0.0.0 for universal IPv4/IPv6 dual-stack access
app.listen(port, '0.0.0.0', () => {
  console.log(`\n🚀 AI Horde & Story-Flow Server listening at http://localhost:${port} and http://127.0.0.1:${port}`);
  console.log(`🌐 Base URL:      ${hordeClient.baseUrl}`);
  console.log(`🔑 API Key:       ${hordeClient.apiKey === '0000000000' ? '0000000000 (Anonymous Free Tier)' : hordeClient.apiKey.slice(0, 6) + '...'}`);
  console.log(`🏷️  Client-Agent:  ${hordeClient.clientAgent}\n`);
});
