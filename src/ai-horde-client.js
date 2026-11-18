/**
 * AI Horde Client / Service Module
 *
 * Provides a robust, asynchronous client for the AI Horde API (v2),
 * enabling completely free image and text generation on crowdsourced GPU workers.
 *
 * Features:
 * - Anonymous (0000000000) or authenticated API key support
 * - Automatic HTTP 429 rate-limit backoff & retry
 * - Dynamic model discovery (sorted by worker availability)
 * - Safe free-tier constraints (512x512, 20-25 steps)
 * - Progress callbacks with live queue_position and wait_time
 * - Full timeout handling (default 3 minutes)
 * - AbortController support for cancelling in-flight polls
 */

export class AiHordeError extends Error {
  constructor(message, statusCode = null, rawData = null) {
    super(message);
    this.name = 'AiHordeError';
    this.statusCode = statusCode;
    this.rawData = rawData;
  }
}

export class AiHordeClient {
  /**
   * @param {Object} [config]
   * @param {string} [config.baseUrl] - Base API URL (defaults to https://aihorde.net/api/v2)
   * @param {string} [config.apiKey] - Horde API Key (defaults to 0000000000 anonymous)
   * @param {string} [config.clientAgent] - Client-Agent header (defaults to StoryFlow:1.0.0:dev@localhost)
   * @param {number} [config.pollIntervalMs] - Polling interval in ms (default: 3000)
   * @param {number} [config.defaultTimeoutMs] - Polling timeout in ms (default: 180000 = 3 mins)
   * @param {number} [config.maxRetries] - Max retries for rate-limiting (default: 3)
   */
  constructor(config = {}) {
    this.baseUrl = (config.baseUrl || process.env.AI_HORDE_BASE_URL || 'https://aihorde.net/api/v2').replace(/\/+$/, '');
    this.apiKey = config.apiKey || process.env.AI_HORDE_API_KEY || '0000000000';
    this.clientAgent = config.clientAgent || process.env.AI_HORDE_CLIENT_AGENT || 'StoryFlow:1.0.0:dev@localhost';
    this.pollIntervalMs = config.pollIntervalMs || 3000;
    this.defaultTimeoutMs = config.defaultTimeoutMs || 180000;
    this.maxRetries = config.maxRetries ?? 3;
  }

  /**
   * Internal HTTP request helper with automatic 429 retry logic.
   * @private
   */
  async #request(endpoint, { method = 'GET', body = null, apiKey = null, signal = null, retryCount = 0 } = {}) {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    const headers = {
      'Client-Agent': this.clientAgent,
      'apikey': apiKey || this.apiKey,
    };

    if (body) {
      headers['Content-Type'] = 'application/json';
    }

    const options = {
      method,
      headers,
      signal,
    };

    if (body) {
      options.body = typeof body === 'string' ? body : JSON.stringify(body);
    }

    let response;
    try {
      response = await fetch(url, options);
    } catch (err) {
      if (err.name === 'AbortError') {
        throw err;
      }
      throw new AiHordeError(`Network request failed: ${err.message}`, null, err);
    }

    // Handle Rate Limiting (HTTP 429)
    if (response.status === 429) {
      if (retryCount < this.maxRetries) {
        const retryAfterHeader = response.headers.get('retry-after');
        const delaySeconds = retryAfterHeader ? parseInt(retryAfterHeader, 10) : Math.pow(2, retryCount + 1);
        const delayMs = Math.max(1000, delaySeconds * 1000);

        console.warn(`[AI Horde] Rate limited (429). Retrying after ${delayMs}ms (attempt ${retryCount + 1}/${this.maxRetries})...`);
        await new Promise((res) => setTimeout(res, delayMs));

        return this.#request(endpoint, {
          method,
          body,
          apiKey,
          signal,
          retryCount: retryCount + 1,
        });
      }
      throw new AiHordeError('AI Horde rate limit exceeded after maximum retries.', 429);
    }

    let data = null;
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      try {
        data = await response.json();
      } catch (parseErr) {
        throw new AiHordeError(`Failed to parse JSON response from ${endpoint}: ${parseErr.message}`, response.status);
      }
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMsg = data?.message || data?.error || (typeof data === 'string' ? data : response.statusText);
      throw new AiHordeError(`AI Horde API Error [${response.status}]: ${errorMsg}`, response.status, data);
    }

    return data;
  }

  // ==========================================
  // Dynamic Model Discovery
  // ==========================================

  /**
   * Fetch active models with their live worker counts.
   * @param {Object} [options]
   * @param {'image' | 'text'} [options.type='image']
   * @param {boolean} [options.onlyActive=true] - Only return models with count > 0
   * @returns {Promise<Array<{name: string, count: number, eta: number, queued: number, type: string}>>}
   */
  async getModels({ type = 'image', onlyActive = true } = {}) {
    const data = await this.#request(`/status/models?type=${type}`);
    if (!Array.isArray(data)) return [];

    let filtered = data;
    if (onlyActive) {
      filtered = filtered.filter((m) => m.count > 0);
    }

    // Sort by active worker count descending
    return filtered.sort((a, b) => b.count - a.count);
  }

  /**
   * Helper to fetch active image models sorted by worker count.
   */
  async getActiveImageModels() {
    return this.getModels({ type: 'image', onlyActive: true });
  }

  /**
   * Helper to fetch active text models sorted by worker count.
   */
  async getActiveTextModels() {
    return this.getModels({ type: 'text', onlyActive: true });
  }

  /**
   * Get the top active model name for a given type, or fallback.
   * @param {'image' | 'text'} type
   * @param {string} fallback
   */
  async getBestModel(type = 'image', fallback = 'stable_diffusion') {
    try {
      const models = await this.getModels({ type, onlyActive: true });
      if (models.length > 0 && models[0].count > 0) {
        return models[0].name;
      }
    } catch (err) {
      console.warn(`[AI Horde] Failed to fetch best ${type} model, using fallback '${fallback}':`, err.message);
    }
    return fallback;
  }

  // ==========================================
  // Image Generation Flow
  // ==========================================

  /**
   * Submit an asynchronous image generation job.
   * Constrains default parameters within free-tier friendly limits.
   *
   * @param {Object} options
   * @param {string} options.prompt - Prompt text
   * @param {string} [options.negativePrompt] - Negative prompt text
   * @param {Array<string>} [options.models] - Target models (e.g. ['stable_diffusion'])
   * @param {Object} [options.params] - Generation parameters
   * @param {number} [options.params.steps=20] - Sampling steps (20-25 recommended for free tier)
   * @param {number} [options.params.width=512] - Image width (512 recommended for free tier)
   * @param {number} [options.params.height=512] - Image height (512 recommended for free tier)
   * @param {number} [options.params.cfg_scale=7.5] - CFG Scale
   * @param {string} [options.params.sampler_name='k_euler_a'] - Sampler name
   * @param {boolean} [options.nsfw=false]
   * @param {boolean} [options.censor_nsfw=true]
   * @param {boolean} [options.r2=true] - Return Cloudflare R2 hosted URLs instead of base64
   * @returns {Promise<{id: string, kudos: number, message?: string}>}
   */
  async submitImageGeneration(options = {}) {
    if (!options.prompt || !options.prompt.trim()) {
      throw new Error('Image generation prompt is required.');
    }

    let fullPrompt = options.prompt.trim();
    if (options.negativePrompt && options.negativePrompt.trim()) {
      // AI Horde convention for negative prompts
      fullPrompt = `${fullPrompt} ### ${options.negativePrompt.trim()}`;
    }

    const payload = {
      prompt: fullPrompt,
      params: {
        sampler_name: options.params?.sampler_name || 'k_euler_a',
        cfg_scale: Number(options.params?.cfg_scale ?? 7.5),
        steps: Math.min(Math.max(Number(options.params?.steps ?? 20), 10), 50),
        width: Number(options.params?.width ?? 512),
        height: Number(options.params?.height ?? 512),
        ...(options.params?.denoising_strength !== undefined ? { denoising_strength: Number(options.params.denoising_strength) } : {}),
        ...(options.params?.seed ? { seed: String(options.params.seed) } : {}),
      },
      nsfw: Boolean(options.nsfw ?? false),
      censor_nsfw: Boolean(options.censor_nsfw ?? true),
      models: options.models && options.models.length > 0 ? options.models : ['stable_diffusion'],
      r2: Boolean(options.r2 ?? true),
      ...(options.source_image ? {
        source_image: options.source_image,
        source_processing: options.source_processing || 'img2img',
      } : {}),
    };

    return this.#request('/generate/async', {
      method: 'POST',
      body: payload,
    });
  }

  /**
   * Poll check status of an image generation job.
   * Returns queue position, wait time, and completion flags.
   *
   * @param {string} jobId
   * @returns {Promise<{finished: number, processing: number, waiting: number, done: boolean, faulted: boolean, wait_time: number, queue_position: number, is_possible: boolean}>}
   */
  async checkImageStatus(jobId) {
    if (!jobId) throw new Error('Job ID is required to check status.');
    return this.#request(`/generate/check/${jobId}`);
  }

  /**
   * Retrieve the final image asset status and generation payloads.
   *
   * @param {string} jobId
   * @returns {Promise<{generations: Array<{img: string, seed: string, worker_name: string, model: string}>, done: boolean, faulted: boolean}>}
   */
  async getImageResult(jobId) {
    if (!jobId) throw new Error('Job ID is required to fetch result.');
    return this.#request(`/generate/status/${jobId}`);
  }

  /**
   * Complete End-to-End Image Generation Workflow:
   * 1. Dispatches image job via POST /generate/async
   * 2. Polls GET /generate/check/{id} every 3s
   * 3. Calls onProgress with live updates (queue_position, wait_time, etc.)
   * 4. Once done, calls GET /generate/status/{id}
   * 5. Returns final image URL / base64 and generation metadata
   *
   * @param {Object} options - See submitImageGeneration
   * @param {Function} [onProgress] - Callback (progressInfo) => void
   * @param {Object} [control]
   * @param {AbortSignal} [control.signal] - Optional abort signal
   * @param {number} [control.timeoutMs] - Custom timeout in ms (default: 180000)
   * @param {number} [control.pollIntervalMs] - Custom poll interval in ms (default: 3000)
   * @returns {Promise<{id: string, imageUrl: string, isUrl: boolean, seed: string, workerName: string, model: string, generations: Array}>}
   */
  async generateImage(options, onProgress = null, control = {}) {
    const timeoutMs = control.timeoutMs || this.defaultTimeoutMs;
    const pollInterval = control.pollIntervalMs || this.pollIntervalMs;
    const signal = control.signal || null;

    const startTime = Date.now();

    // 1. Submit
    const submitResult = await this.submitImageGeneration(options);
    const jobId = submitResult.id;

    if (!jobId) {
      throw new AiHordeError('No job ID returned by AI Horde for image generation.', null, submitResult);
    }

    if (onProgress) {
      onProgress({
        step: 'submitted',
        jobId,
        kudos: submitResult.kudos,
        elapsedSeconds: 0,
        wait_time: null,
        queue_position: null,
      });
    }

    // 2. Poll
    while (true) {
      if (signal?.aborted) {
        throw new Error('Image generation was cancelled by the user.');
      }

      if (Date.now() - startTime > timeoutMs) {
        throw new AiHordeError(`Image generation timed out after ${Math.round(timeoutMs / 1000)} seconds. Job ID: ${jobId}`);
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval));

      const check = await this.checkImageStatus(jobId);
      const elapsedSeconds = Math.round((Date.now() - startTime) / 1000);

      if (onProgress) {
        onProgress({
          step: check.done ? 'finishing' : 'polling',
          jobId,
          done: check.done,
          faulted: check.faulted,
          wait_time: check.wait_time ?? 0,
          queue_position: check.queue_position ?? 0,
          processing: check.processing ?? 0,
          finished: check.finished ?? 0,
          waiting: check.waiting ?? 0,
          is_possible: check.is_possible ?? true,
          elapsedSeconds,
        });
      }

      if (check.faulted) {
        throw new AiHordeError(`Image generation job ${jobId} faulted on worker.`, null, check);
      }

      if (check.is_possible === false) {
        console.warn(`[AI Horde] Warning: Job ${jobId} is currently marked as impossible (no active workers for model).`);
      }

      if (check.done) {
        break;
      }
    }

    // 3. Fetch final asset
    const finalResult = await this.getImageResult(jobId);

    if (!finalResult.generations || finalResult.generations.length === 0) {
      throw new AiHordeError(`Image job ${jobId} finished but returned no generations.`, null, finalResult);
    }

    const firstGen = finalResult.generations[0];
    const imgData = firstGen.img;
    const isUrl = typeof imgData === 'string' && imgData.startsWith('http');

    const result = {
      id: jobId,
      imageUrl: imgData,
      isUrl,
      seed: firstGen.seed,
      workerName: firstGen.worker_name,
      model: firstGen.model,
      generations: finalResult.generations,
    };

    if (onProgress) {
      onProgress({
        step: 'completed',
        jobId,
        result,
        elapsedSeconds: Math.round((Date.now() - startTime) / 1000),
      });
    }

    return result;
  }

  // ==========================================
  // Text Generation Flow (KoboldAI LLMs)
  // ==========================================

  /**
   * Submit an asynchronous text generation request.
   *
   * @param {Object} options
   * @param {string} options.prompt - Prompt text
   * @param {Array<string>} [options.models] - Target text models
   * @param {Object} [options.params] - Generation parameters
   * @param {number} [options.params.max_length=250] - Maximum generation tokens (default: 250)
   * @param {number} [options.params.max_context_length=2048] - Max context tokens (default: 2048)
   * @param {number} [options.params.temperature=0.7] - Temperature
   * @param {number} [options.params.top_p=0.9] - Top P
   * @returns {Promise<{id: string, kudos: number}>}
   */
  async submitTextGeneration(options = {}) {
    if (!options.prompt || !options.prompt.trim()) {
      throw new Error('Text generation prompt is required.');
    }

    const payload = {
      prompt: options.prompt.trim(),
      params: {
        max_length: Number(options.params?.max_length ?? 250),
        max_context_length: Number(options.params?.max_context_length ?? 2048),
        temperature: Number(options.params?.temperature ?? 0.7),
        top_p: Number(options.params?.top_p ?? 0.9),
        ...(options.params?.rep_pen ? { rep_pen: Number(options.params.rep_pen) } : {}),
      },
      ...(options.models && options.models.length > 0 ? { models: options.models } : {}),
    };

    return this.#request('/generate/text/async', {
      method: 'POST',
      body: payload,
    });
  }

  /**
   * Check status and retrieve generations for a text job.
   * Note: On AI Horde, text status endpoint returns both polling progress AND final generations.
   *
   * @param {string} jobId
   * @returns {Promise<{done: boolean, faulted: boolean, wait_time: number, queue_position: number, finished: number, processing: number, generations: Array<{text: string, worker_name: string, model: string}>}>}
   */
  async checkTextStatus(jobId) {
    if (!jobId) throw new Error('Job ID is required to check text status.');
    return this.#request(`/generate/text/status/${jobId}`);
  }

  /**
   * Complete End-to-End Text Generation Workflow:
   * 1. Dispatches text job via POST /generate/text/async
   * 2. Polls GET /generate/text/status/{id} every 3s
   * 3. Calls onProgress with queue_position and wait_time
   * 4. Returns completed text output and worker metadata
   *
   * @param {Object} options - See submitTextGeneration
   * @param {Function} [onProgress] - Callback (progressInfo) => void
   * @param {Object} [control]
   * @param {AbortSignal} [control.signal]
   * @param {number} [control.timeoutMs]
   * @param {number} [control.pollIntervalMs]
   * @returns {Promise<{id: string, text: string, workerName: string, model: string, generations: Array}>}
   */
  async generateText(options, onProgress = null, control = {}) {
    const timeoutMs = control.timeoutMs || this.defaultTimeoutMs;
    const pollInterval = control.pollIntervalMs || this.pollIntervalMs;
    const signal = control.signal || null;

    const startTime = Date.now();

    // 1. Submit
    const submitResult = await this.submitTextGeneration(options);
    const jobId = submitResult.id;

    if (!jobId) {
      throw new AiHordeError('No job ID returned by AI Horde for text generation.', null, submitResult);
    }

    if (onProgress) {
      onProgress({
        step: 'submitted',
        jobId,
        kudos: submitResult.kudos,
        elapsedSeconds: 0,
        wait_time: null,
        queue_position: null,
      });
    }

    // 2. Poll
    while (true) {
      if (signal?.aborted) {
        throw new Error('Text generation was cancelled by the user.');
      }

      if (Date.now() - startTime > timeoutMs) {
        throw new AiHordeError(`Text generation timed out after ${Math.round(timeoutMs / 1000)} seconds. Job ID: ${jobId}`);
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval));

      const status = await this.checkTextStatus(jobId);
      const elapsedSeconds = Math.round((Date.now() - startTime) / 1000);

      if (onProgress) {
        onProgress({
          step: status.done ? 'finishing' : 'polling',
          jobId,
          done: status.done,
          faulted: status.faulted,
          wait_time: status.wait_time ?? 0,
          queue_position: status.queue_position ?? 0,
          processing: status.processing ?? 0,
          finished: status.finished ?? 0,
          waiting: status.waiting ?? 0,
          elapsedSeconds,
        });
      }

      if (status.faulted) {
        throw new AiHordeError(`Text generation job ${jobId} faulted on worker.`, null, status);
      }

      if (status.done) {
        if (!status.generations || status.generations.length === 0) {
          throw new AiHordeError(`Text job ${jobId} marked done but returned no generations.`, null, status);
        }

        const firstGen = status.generations[0];
        const result = {
          id: jobId,
          text: firstGen.text,
          workerName: firstGen.worker_name,
          model: firstGen.model,
          generations: status.generations,
        };

        if (onProgress) {
          onProgress({
            step: 'completed',
            jobId,
            result,
            elapsedSeconds,
          });
        }

        return result;
      }
    }
  }

  // ==========================================
  // Account & Heartbeat Info
  // ==========================================

  /**
   * Fetch user account info (kudos balance, username, worker count)
   * @param {string} [apiKey] - Defaults to client's configured key
   */
  async getUserInfo(apiKey = null) {
    return this.#request('/find_user', { apiKey: apiKey || this.apiKey });
  }

  /**
   * Check Horde service operational status
   */
  async getHordeStatus() {
    return this.#request('/status/heartbeat');
  }
}

export default AiHordeClient;
