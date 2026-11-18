/**
 * AI Horde Studio - Frontend Client Logic
 */

// State
const state = {
  activeTab: 'tab-story',
  storyDuration: 60,
  storyAspect: '9:16',
  storyVoice: 'christopher',
  currentStoryEventSource: null,
  imageWidth: 512,
  imageHeight: 512,
  imageModels: [],
  textModels: [],
  currentImageEventSource: null,
  currentTextEventSource: null,
  imageTimerInterval: null,
  textTimerInterval: null,
};

const sampleStoryTopics = [
  'The Brave Little Fox Who Touched the Northern Lights',
  'The Clockwork Dragon Who Guarded a Tiny Wildflower',
  'The Girl Who Kept a Summer Raincloud in a Glass Jar',
  'The Ancient Samurai and the Celestial Moonlight Deer',
  'The Boy Who Built a Flying Ship Out of Forgotten Books'
];

// Sample Prompts
const sampleImagePrompts = [
  'A serene misty Japanese mountain sanctuary at dawn with cherry blossoms, cinematic lighting, 8k digital art',
  'A cyberpunk street market at night with neon holographic signs and steam rising from food stalls, unreal engine 5 render',
  'An ancient mystical library with floating illuminated spellbooks, warm atmospheric glow, hyperrealistic fantasy art',
  'A cozy retro-futuristic laboratory full of glowing vacuum tubes, brass instruments, and vintage monitors, detailed concept art',
  'Macro photography of an iridescent crystal butterfly resting on a bioluminescent jungle flower, studio lighting, sharp focus'
];

const sampleTextPrompts = [
  'Write an engaging 30-second YouTube video intro hook about the mysterious origins of deep-sea trenches:',
  'Write a clean, documented Python function that calculates exponential moving averages on a financial time-series dataframe:',
  'Brainstorm 5 high-converting, curiosity-driven YouTube video titles and thumbnail concepts for a tech automation channel:',
  'Write a short, atmospheric opening paragraph for a science fiction story about the first quantum warp jump:'
];

// Elements
const el = {
  // Tabs
  tabBtns: document.querySelectorAll('.tab-btn'),
  tabPanels: document.querySelectorAll('.tab-panel'),

  // Story Video Generator
  storyForm: document.getElementById('story-form'),
  storyTopic: document.getElementById('story-topic'),
  btnSampleStory: document.getElementById('btn-sample-story'),
  storyAspectChips: document.querySelectorAll('#story-aspect-selector .chip'),
  storyDurationChips: document.querySelectorAll('#story-duration-selector .chip'),
  storyVoice: document.getElementById('story-voice'),
  btnGenerateStory: document.getElementById('btn-generate-story'),
  storyStatusBadge: document.getElementById('story-status-badge'),
  storyLogBox: document.getElementById('story-log-box'),
  storyTerminalContent: document.getElementById('story-terminal-content'),
  storyEmptyState: document.getElementById('story-empty-state'),
  storyResultBox: document.getElementById('story-result-box'),
  storyVideoPlayer: document.getElementById('story-video-player'),
  storyVideoSource: document.getElementById('story-video-source'),
  storyResFilename: document.getElementById('story-res-filename'),
  btnDownloadStoryVideo: document.getElementById('btn-download-story-video'),
  recentVideosList: document.getElementById('recent-videos-list'),
  btnRefreshStoryVideos: document.getElementById('btn-refresh-story-videos'),

  // Header / Account
  hordeStatusText: document.getElementById('horde-status-text'),
  userName: document.getElementById('user-name'),
  userKudos: document.getElementById('user-kudos'),
  userKudosPill: document.getElementById('user-kudos-pill'),
  settingsBtn: document.getElementById('settings-btn'),
  settingsModal: document.getElementById('settings-modal'),
  btnCloseSettings: document.getElementById('btn-close-settings'),
  btnCancelSettings: document.getElementById('btn-cancel-settings'),
  btnSaveSettings: document.getElementById('btn-save-settings'),
  settingApiKey: document.getElementById('setting-apikey'),
  modalAccountName: document.getElementById('modal-account-name'),
  modalAccountKudos: document.getElementById('modal-account-kudos'),

  // Image Form
  imageForm: document.getElementById('image-form'),
  imgPrompt: document.getElementById('img-prompt'),
  imgNegPrompt: document.getElementById('img-neg-prompt'),
  imgModel: document.getElementById('img-model'),
  imgModelWorkers: document.getElementById('img-model-workers'),
  imgSteps: document.getElementById('img-steps'),
  imgStepsVal: document.getElementById('img-steps-val'),
  imgCfg: document.getElementById('img-cfg'),
  imgCfgVal: document.getElementById('img-cfg-val'),
  imgSampler: document.getElementById('img-sampler'),
  btnSampleImagePrompt: document.getElementById('btn-sample-image-prompt'),
  btnGenerateImage: document.getElementById('btn-generate-image'),
  resChips: document.querySelectorAll('#resolution-selector .chip'),

  // Image Status & Result
  imgStatusBadge: document.getElementById('img-status-badge'),
  imgProgressContainer: document.getElementById('img-progress-container'),
  imgProgressStep: document.getElementById('img-progress-step'),
  imgProgressTimer: document.getElementById('img-progress-timer'),
  imgProgressBar: document.getElementById('img-progress-bar'),
  imgQueuePos: document.getElementById('img-queue-pos'),
  imgWaitTime: document.getElementById('img-wait-time'),
  imgWorkerStatus: document.getElementById('img-worker-status'),
  imageEmptyState: document.getElementById('image-empty-state'),
  imageResultBox: document.getElementById('image-result-box'),
  imageOutput: document.getElementById('image-output'),
  imgResModel: document.getElementById('img-res-model'),
  imgResWorker: document.getElementById('img-res-worker'),
  imgResSeed: document.getElementById('img-res-seed'),
  btnDownloadImage: document.getElementById('btn-download-image'),
  btnCopyImageUrl: document.getElementById('btn-copy-image-url'),

  // Text Form
  textForm: document.getElementById('text-form'),
  textPrompt: document.getElementById('text-prompt'),
  textModel: document.getElementById('text-model'),
  textModelWorkers: document.getElementById('text-model-workers'),
  textMaxTokens: document.getElementById('text-max-tokens'),
  textMaxTokensVal: document.getElementById('text-max-tokens-val'),
  textTemp: document.getElementById('text-temp'),
  textTempVal: document.getElementById('text-temp-val'),
  btnSampleTextPrompt: document.getElementById('btn-sample-text-prompt'),
  btnGenerateText: document.getElementById('btn-generate-text'),

  // Text Status & Result
  textStatusBadge: document.getElementById('text-status-badge'),
  textProgressContainer: document.getElementById('text-progress-container'),
  textProgressStep: document.getElementById('text-progress-step'),
  textProgressTimer: document.getElementById('text-progress-timer'),
  textProgressBar: document.getElementById('text-progress-bar'),
  textQueuePos: document.getElementById('text-queue-pos'),
  textWaitTime: document.getElementById('text-wait-time'),
  textWorkerStatus: document.getElementById('text-worker-status'),
  textEmptyState: document.getElementById('text-empty-state'),
  textResultBox: document.getElementById('text-result-box'),
  textOutput: document.getElementById('text-output'),
  textResModel: document.getElementById('text-res-model'),
  textResWorker: document.getElementById('text-res-worker'),
  btnCopyText: document.getElementById('btn-copy-text'),

  // Models Table
  btnRefreshModels: document.getElementById('btn-refresh-models'),
  tableImageModels: document.getElementById('table-image-models').querySelector('tbody'),
  tableTextModels: document.getElementById('table-text-models').querySelector('tbody'),

  // Toast
  toast: document.getElementById('toast'),
};

// ==========================================
// Initialization
// ==========================================
async function init() {
  setupTabs();
  setupSliders();
  setupChips();
  setupSettingsModal();
  setupPromptButtons();
  setupStoryPipeline();

  await checkSystemStatus();
  await loadUserData();
  await loadModels();
  await loadRecentVideos();
}

// ==========================================
// System Status & User
// ==========================================
async function checkSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.status === 'ok') {
      el.hordeStatusText.textContent = 'Cluster Online';
    }
  } catch (err) {
    el.hordeStatusText.textContent = 'Offline';
    showToast('Failed to connect to backend server.', 'error');
  }
}

async function loadUserData() {
  try {
    const res = await fetch('/api/user');
    const data = await res.json();
    if (data.username) {
      el.userName.textContent = data.username.split('#')[0] || 'Anonymous';
      el.userKudos.textContent = `${Number(data.kudos || 0).toLocaleString()} Kudos`;
      el.modalAccountName.textContent = data.username;
      el.modalAccountKudos.textContent = Number(data.kudos || 0).toLocaleString();
    }
  } catch (err) {
    console.warn('Could not fetch user stats:', err);
  }
}

// ==========================================
// Dynamic Model Discovery
// ==========================================
async function loadModels() {
  try {
    el.imgModelWorkers.textContent = 'Discovering active workers...';
    el.textModelWorkers.textContent = 'Discovering active workers...';

    const [imgRes, textRes] = await Promise.all([
      fetch('/api/models?type=image'),
      fetch('/api/models?type=text')
    ]);

    state.imageModels = await imgRes.json();
    state.textModels = await textRes.json();

    // Populate Image Dropdown
    el.imgModel.innerHTML = '';
    state.imageModels.forEach((m, idx) => {
      const opt = document.createElement('option');
      opt.value = m.name;
      opt.textContent = `${m.name} (${m.count} workers | ETA: ${m.eta}s)`;
      if (m.name === 'stable_diffusion' || idx === 0) {
        opt.selected = true;
      }
      el.imgModel.appendChild(opt);
    });

    updateImageModelWorkerBadge();

    // Populate Text Dropdown
    el.textModel.innerHTML = '<option value="">Auto (Best Available Worker)</option>';
    state.textModels.forEach((m) => {
      const opt = document.createElement('option');
      opt.value = m.name;
      opt.textContent = `${m.name} (${m.count} workers | ETA: ${m.eta}s)`;
      el.textModel.appendChild(opt);
    });

    updateTextModelWorkerBadge();

    // Populate Models Tab Tables
    renderModelsTables();
  } catch (err) {
    console.error('Failed to load models:', err);
    showToast('Failed to discover active Horde models.', 'error');
  }
}

function updateImageModelWorkerBadge() {
  const selectedName = el.imgModel.value;
  const found = state.imageModels.find((m) => m.name === selectedName);
  if (found) {
    el.imgModelWorkers.textContent = `⚡ ${found.count} active GPUs (ETA: ${found.eta}s)`;
  } else {
    el.imgModelWorkers.textContent = '';
  }
}

function updateTextModelWorkerBadge() {
  const selectedName = el.textModel.value;
  if (!selectedName) {
    const totalWorkers = state.textModels.reduce((acc, m) => acc + m.count, 0);
    el.textModelWorkers.textContent = `⚡ ${totalWorkers} active text GPUs pooled`;
    return;
  }
  const found = state.textModels.find((m) => m.name === selectedName);
  if (found) {
    el.textModelWorkers.textContent = `⚡ ${found.count} active GPUs (ETA: ${found.eta}s)`;
  } else {
    el.textModelWorkers.textContent = '';
  }
}

el.imgModel.addEventListener('change', updateImageModelWorkerBadge);
el.textModel.addEventListener('change', updateTextModelWorkerBadge);

function renderModelsTables() {
  // Image Models Table
  el.tableImageModels.innerHTML = '';
  state.imageModels.slice(0, 20).forEach((m) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${escapeHtml(m.name)}</strong></td>
      <td><span class="worker-pill">${m.count} GPUs</span></td>
      <td>${m.jobs}</td>
      <td>${m.eta}s</td>
      <td><button class="btn btn-secondary btn-icon" style="font-size: 0.75rem; padding: 0.2rem 0.5rem;" onclick="selectModel('image', '${escapeHtml(m.name)}')">Select</button></td>
    `;
    el.tableImageModels.appendChild(tr);
  });

  // Text Models Table
  el.tableTextModels.innerHTML = '';
  state.textModels.slice(0, 20).forEach((m) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${escapeHtml(m.name)}</strong></td>
      <td><span class="worker-pill">${m.count} GPUs</span></td>
      <td>${m.jobs}</td>
      <td>${m.eta}s</td>
      <td><button class="btn btn-secondary btn-icon" style="font-size: 0.75rem; padding: 0.2rem 0.5rem;" onclick="selectModel('text', '${escapeHtml(m.name)}')">Select</button></td>
    `;
    el.tableTextModels.appendChild(tr);
  });
}

window.selectModel = (type, modelName) => {
  if (type === 'image') {
    el.imgModel.value = modelName;
    updateImageModelWorkerBadge();
    switchTab('tab-image');
    showToast(`Selected image model: ${modelName}`);
  } else {
    el.textModel.value = modelName;
    updateTextModelWorkerBadge();
    switchTab('tab-text');
    showToast(`Selected text model: ${modelName}`);
  }
};

el.btnRefreshModels.addEventListener('click', async () => {
  el.btnRefreshModels.disabled = true;
  el.btnRefreshModels.textContent = 'Refreshing...';
  await loadModels();
  el.btnRefreshModels.disabled = false;
  el.btnRefreshModels.textContent = '🔄 Refresh Models';
  showToast('Model status updated!');
});

// ==========================================
// Storytelling Video Pipeline
// ==========================================
function setupStoryPipeline() {
  // Aspect Ratio Chips
  el.storyAspectChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      el.storyAspectChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      state.storyAspect = chip.getAttribute('data-aspect');
    });
  });

  // Duration Chips
  el.storyDurationChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      el.storyDurationChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      state.storyDuration = Number(chip.getAttribute('data-dur'));
    });
  });

  // Random Story Prompt
  el.btnSampleStory.addEventListener('click', () => {
    const random = sampleStoryTopics[Math.floor(Math.random() * sampleStoryTopics.length)];
    el.storyTopic.value = random;
    showToast('Loaded story idea!');
  });

  // Refresh Videos List
  el.btnRefreshStoryVideos.addEventListener('click', () => {
    loadRecentVideos();
  });

  // Story Form Submit
  el.storyForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const topic = el.storyTopic.value.trim();
    if (!topic) return;

    const duration = state.storyDuration || 60;
    const voice = el.storyVoice.value || 'christopher';
    const aspect = state.storyAspect || '9:16';

    // UI state
    el.btnGenerateStory.disabled = true;
    el.btnGenerateStory.innerHTML = '<span class="btn-icon">⏳</span> Producing Story Video...';
    el.storyStatusBadge.className = 'badge badge-processing';
    el.storyStatusBadge.textContent = 'Processing';

    el.storyLogBox.classList.remove('hidden');
    el.storyTerminalContent.textContent = 'Connecting to Story Pipeline...\n';
    el.storyEmptyState.classList.add('hidden');
    el.storyResultBox.classList.add('hidden');

    if (state.currentStoryEventSource) {
      state.currentStoryEventSource.close();
    }

    const sseUrl = `/api/story/stream?topic=${encodeURIComponent(topic)}&duration=${duration}&voice=${encodeURIComponent(voice)}&aspect=${encodeURIComponent(aspect)}`;
    const eventSource = new EventSource(sseUrl);
    state.currentStoryEventSource = eventSource;

    eventSource.addEventListener('log', (event) => {
      const data = JSON.parse(event.data);
      const line = data.message;
      el.storyTerminalContent.textContent += line + '\n';
      el.storyTerminalContent.scrollTop = el.storyTerminalContent.scrollHeight;

      if (line.includes('[Step 1/4]')) {
        el.storyStatusBadge.textContent = '1/4 Writing Script';
      } else if (line.includes('[Step 2/4]')) {
        el.storyStatusBadge.textContent = '2/4 Generating Art';
      } else if (line.includes('[Step 3/4]')) {
        el.storyStatusBadge.textContent = '3/4 Voice & Subtitles';
      } else if (line.includes('[Step 4/4]')) {
        el.storyStatusBadge.textContent = '4/4 Rendering Video';
      }
    });

    eventSource.addEventListener('completed', (event) => {
      const data = JSON.parse(event.data);
      eventSource.close();

      el.btnGenerateStory.disabled = false;
      el.btnGenerateStory.innerHTML = '<span class="btn-icon">🎬</span> Generate Story Video (1080p)';
      el.storyStatusBadge.className = 'badge badge-done';
      el.storyStatusBadge.textContent = 'Ready';

      // Load Video into Player
      el.storyVideoSource.src = data.videoUrl;
      el.storyVideoPlayer.load();
      el.storyResFilename.textContent = data.filename;
      el.btnDownloadStoryVideo.href = data.videoUrl;
      el.btnDownloadStoryVideo.download = data.filename;

      el.storyResultBox.classList.remove('hidden');
      el.storyEmptyState.classList.add('hidden');

      showToast('🎉 Story video successfully generated!');
      loadRecentVideos();
    });

    eventSource.addEventListener('error', (event) => {
      eventSource.close();
      el.btnGenerateStory.disabled = false;
      el.btnGenerateStory.innerHTML = '<span class="btn-icon">🎬</span> Generate Story Video (1080p)';
      el.storyStatusBadge.className = 'badge badge-error';
      el.storyStatusBadge.textContent = 'Error';

      let msg = 'Story generation failed.';
      try {
        const parsed = JSON.parse(event.data);
        msg = parsed.message || msg;
      } catch (_) {}

      showToast(msg, 'error');
    });
  });
}

async function loadRecentVideos() {
  try {
    const res = await fetch('/api/story/videos');
    const videos = await res.json();

    if (!videos || videos.length === 0) {
      el.recentVideosList.innerHTML = '<div class="empty-list-note">No generated story videos yet. Create one above!</div>';
      return;
    }

    el.recentVideosList.innerHTML = '';
    videos.forEach((v) => {
      const item = document.createElement('div');
      item.className = 'recent-video-item';
      item.innerHTML = `
        <div class="recent-video-title" title="${escapeHtml(v.filename)}">🎞️ ${escapeHtml(v.filename)}</div>
        <div class="recent-video-actions">
          <span class="meta-val">${v.sizeMb} MB</span>
          <button class="btn btn-secondary btn-icon" style="font-size: 0.75rem; padding: 0.2rem 0.5rem;" onclick="playStoryVideo('${escapeHtml(v.url)}', '${escapeHtml(v.filename)}')">▶ Play</button>
          <a class="btn btn-secondary btn-icon" style="font-size: 0.75rem; padding: 0.2rem 0.5rem;" href="${escapeHtml(v.url)}" download="${escapeHtml(v.filename)}">📥</a>
        </div>
      `;
      el.recentVideosList.appendChild(item);
    });
  } catch (err) {
    console.warn('Failed to load recent story videos:', err);
  }
}

window.playStoryVideo = (url, filename) => {
  el.storyVideoSource.src = url;
  el.storyVideoPlayer.load();
  el.storyVideoPlayer.play();
  el.storyResFilename.textContent = filename;
  el.btnDownloadStoryVideo.href = url;
  el.btnDownloadStoryVideo.download = filename;

  el.storyResultBox.classList.remove('hidden');
  el.storyEmptyState.classList.add('hidden');
  switchTab('tab-story');
  showToast(`Loaded ${filename}`);
};

// ==========================================
// Image Generation Flow
// ==========================================
el.imageForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = el.imgPrompt.value.trim();
  if (!prompt) return;

  const negativePrompt = el.imgNegPrompt.value.trim();
  const model = el.imgModel.value || 'stable_diffusion';
  const steps = Number(el.imgSteps.value);
  const cfgScale = Number(el.imgCfg.value);
  const sampler = el.imgSampler.value;

  // UI Setup for Active Generation
  el.btnGenerateImage.disabled = true;
  el.btnGenerateImage.innerHTML = '<span class="btn-icon">⏳</span> Queued on Horde...';
  el.imgStatusBadge.className = 'badge badge-queued';
  el.imgStatusBadge.textContent = 'Queued';

  el.imgProgressContainer.classList.remove('hidden');
  el.imageEmptyState.classList.add('hidden');
  el.imageResultBox.classList.add('hidden');

  el.imgProgressStep.textContent = 'Dispatching to AI Horde coordinator...';
  el.imgProgressBar.style.width = '10%';
  el.imgQueuePos.textContent = '--';
  el.imgWaitTime.textContent = '--';
  el.imgWorkerStatus.textContent = 'Submitting';

  let elapsedSeconds = 0;
  clearInterval(state.imageTimerInterval);
  state.imageTimerInterval = setInterval(() => {
    elapsedSeconds++;
    el.imgProgressTimer.textContent = `${elapsedSeconds}s elapsed`;
  }, 1000);

  if (state.currentImageEventSource) {
    state.currentImageEventSource.close();
  }

  try {
    // 1. Submit Request
    const submitRes = await fetch('/api/generate/image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        negativePrompt,
        models: [model],
        params: {
          width: state.imageWidth,
          height: state.imageHeight,
          steps,
          cfg_scale: cfgScale,
          sampler_name: sampler,
        },
      }),
    });

    const submitData = await submitRes.json();
    if (!submitRes.ok) {
      throw new Error(submitData.error || 'Failed to submit image job.');
    }

    const jobId = submitData.id;
    el.imgProgressStep.textContent = `Job #${jobId.slice(0, 8)} in queue...`;

    // 2. Subscribe to Real-Time SSE Stream
    const eventSource = new EventSource(`/api/generate/image/${jobId}/stream`);
    state.currentImageEventSource = eventSource;

    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);

      el.imgQueuePos.textContent = data.queue_position !== undefined ? `#${data.queue_position}` : '--';
      el.imgWaitTime.textContent = data.wait_time ? `${data.wait_time}s` : '< 10s';

      if (data.processing > 0) {
        el.imgWorkerStatus.textContent = '⚡ Rendering on GPU';
        el.imgStatusBadge.className = 'badge badge-processing';
        el.imgStatusBadge.textContent = 'Processing';
        el.imgProgressStep.textContent = 'Volunteer worker rendering your image...';
        el.imgProgressBar.style.width = '80%';
      } else {
        el.imgWorkerStatus.textContent = 'Waiting in queue';
        el.imgStatusBadge.className = 'badge badge-queued';
        el.imgStatusBadge.textContent = 'Queued';
        el.imgProgressBar.style.width = '35%';
      }
    });

    eventSource.addEventListener('completed', (event) => {
      const data = JSON.parse(event.data);
      eventSource.close();
      clearInterval(state.imageTimerInterval);

      el.btnGenerateImage.disabled = false;
      el.btnGenerateImage.innerHTML = '<span class="btn-icon">⚡</span> Generate Image (Free)';
      el.imgStatusBadge.className = 'badge badge-done';
      el.imgStatusBadge.textContent = 'Completed';
      el.imgProgressBar.style.width = '100%';
      el.imgProgressStep.textContent = 'Render completed!';

      renderImageResult(data.result);
      showToast('Image generated successfully!');
    });

    eventSource.addEventListener('error', (event) => {
      eventSource.close();
      clearInterval(state.imageTimerInterval);
      el.btnGenerateImage.disabled = false;
      el.btnGenerateImage.innerHTML = '<span class="btn-icon">⚡</span> Generate Image (Free)';
      el.imgStatusBadge.className = 'badge badge-error';
      el.imgStatusBadge.textContent = 'Error';

      let msg = 'Image generation failed.';
      try {
        const parsed = JSON.parse(event.data);
        msg = parsed.message || msg;
      } catch (_) {}

      showToast(msg, 'error');
    });

  } catch (err) {
    clearInterval(state.imageTimerInterval);
    el.btnGenerateImage.disabled = false;
    el.btnGenerateImage.innerHTML = '<span class="btn-icon">⚡</span> Generate Image (Free)';
    el.imgStatusBadge.className = 'badge badge-error';
    el.imgStatusBadge.textContent = 'Failed';
    showToast(err.message, 'error');
  }
});

function renderImageResult(result) {
  const gen = result.generations?.[0];
  if (!gen) return;

  const imgData = gen.img;
  const isUrl = typeof imgData === 'string' && imgData.startsWith('http');

  const src = isUrl ? imgData : `data:image/webp;base64,${imgData}`;
  el.imageOutput.src = src;

  el.imgResModel.textContent = gen.model || 'Unknown';
  el.imgResWorker.textContent = gen.worker_name || 'Volunteer Worker';
  el.imgResSeed.textContent = gen.seed || 'Random';

  el.btnDownloadImage.href = src;
  el.btnDownloadImage.download = `aihorde_${gen.seed || 'result'}.webp`;

  el.btnCopyImageUrl.onclick = () => {
    navigator.clipboard.writeText(src);
    showToast('Asset URL copied to clipboard!');
  };

  el.imageResultBox.classList.remove('hidden');
}

// ==========================================
// Text Generation Flow (LLM)
// ==========================================
el.textForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = el.textPrompt.value.trim();
  if (!prompt) return;

  const model = el.textModel.value ? [el.textModel.value] : undefined;
  const maxTokens = Number(el.textMaxTokens.value);
  const temp = Number(el.textTemp.value);

  // UI Setup
  el.btnGenerateText.disabled = true;
  el.btnGenerateText.innerHTML = '<span class="btn-icon">⏳</span> Queued on Horde...';
  el.textStatusBadge.className = 'badge badge-queued';
  el.textStatusBadge.textContent = 'Queued';

  el.textProgressContainer.classList.remove('hidden');
  el.textEmptyState.classList.add('hidden');
  el.textResultBox.classList.add('hidden');

  el.textProgressStep.textContent = 'Dispatching to text cluster...';
  el.textProgressBar.style.width = '10%';
  el.textQueuePos.textContent = '--';
  el.textWaitTime.textContent = '--';
  el.textWorkerStatus.textContent = 'Submitting';

  let elapsedSeconds = 0;
  clearInterval(state.textTimerInterval);
  state.textTimerInterval = setInterval(() => {
    elapsedSeconds++;
    el.textProgressTimer.textContent = `${elapsedSeconds}s elapsed`;
  }, 1000);

  if (state.currentTextEventSource) {
    state.currentTextEventSource.close();
  }

  try {
    // 1. Submit
    const submitRes = await fetch('/api/generate/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        models: model,
        params: {
          max_length: maxTokens,
          temperature: temp,
        },
      }),
    });

    const submitData = await submitRes.json();
    if (!submitRes.ok) {
      throw new Error(submitData.error || 'Failed to submit text job.');
    }

    const jobId = submitData.id;
    el.textProgressStep.textContent = `Job #${jobId.slice(0, 8)} in queue...`;

    // 2. Subscribe to SSE
    const eventSource = new EventSource(`/api/generate/text/${jobId}/stream`);
    state.currentTextEventSource = eventSource;

    eventSource.addEventListener('progress', (event) => {
      const data = JSON.parse(event.data);

      el.textQueuePos.textContent = data.queue_position !== undefined ? `#${data.queue_position}` : '--';
      el.textWaitTime.textContent = data.wait_time ? `${data.wait_time}s` : '< 10s';

      if (data.processing > 0) {
        el.textWorkerStatus.textContent = '⚡ Streaming / Generating';
        el.textStatusBadge.className = 'badge badge-processing';
        el.textStatusBadge.textContent = 'Generating';
        el.textProgressStep.textContent = 'LLM worker generating response...';
        el.textProgressBar.style.width = '85%';
      } else {
        el.textWorkerStatus.textContent = 'Waiting in queue';
        el.textStatusBadge.className = 'badge badge-queued';
        el.textStatusBadge.textContent = 'Queued';
        el.textProgressBar.style.width = '40%';
      }
    });

    eventSource.addEventListener('completed', (event) => {
      const data = JSON.parse(event.data);
      eventSource.close();
      clearInterval(state.textTimerInterval);

      el.btnGenerateText.disabled = false;
      el.btnGenerateText.innerHTML = '<span class="btn-icon">✍️</span> Generate Text (Free)';
      el.textStatusBadge.className = 'badge badge-done';
      el.textStatusBadge.textContent = 'Completed';
      el.textProgressBar.style.width = '100%';
      el.textProgressStep.textContent = 'Text generation complete!';

      renderTextResult(data.result);
      showToast('Text response generated!');
    });

    eventSource.addEventListener('error', (event) => {
      eventSource.close();
      clearInterval(state.textTimerInterval);
      el.btnGenerateText.disabled = false;
      el.btnGenerateText.innerHTML = '<span class="btn-icon">✍️</span> Generate Text (Free)';
      el.textStatusBadge.className = 'badge badge-error';
      el.textStatusBadge.textContent = 'Error';

      let msg = 'Text generation failed.';
      try {
        const parsed = JSON.parse(event.data);
        msg = parsed.message || msg;
      } catch (_) {}

      showToast(msg, 'error');
    });

  } catch (err) {
    clearInterval(state.textTimerInterval);
    el.btnGenerateText.disabled = false;
    el.btnGenerateText.innerHTML = '<span class="btn-icon">✍️</span> Generate Text (Free)';
    el.textStatusBadge.className = 'badge badge-error';
    el.textStatusBadge.textContent = 'Failed';
    showToast(err.message, 'error');
  }
});

function renderTextResult(result) {
  const gen = result.generations?.[0];
  if (!gen) return;

  el.textOutput.textContent = gen.text.trim();
  el.textResModel.textContent = gen.model || 'Unknown';
  el.textResWorker.textContent = gen.worker_name || 'Volunteer Worker';

  el.btnCopyText.onclick = () => {
    navigator.clipboard.writeText(gen.text.trim());
    showToast('Text copied to clipboard!');
  };

  el.textResultBox.classList.remove('hidden');
}

// ==========================================
// Settings Modal & API Key Configuration
// ==========================================
function setupSettingsModal() {
  const open = () => el.settingsModal.classList.remove('hidden');
  const close = () => el.settingsModal.classList.add('hidden');

  el.settingsBtn.addEventListener('click', open);
  el.userKudosPill.addEventListener('click', open);
  el.btnCloseSettings.addEventListener('click', close);
  el.btnCancelSettings.addEventListener('click', close);

  el.settingsModal.addEventListener('click', (e) => {
    if (e.target === el.settingsModal) close();
  });

  el.btnSaveSettings.addEventListener('click', async () => {
    const apiKey = el.settingApiKey.value.trim() || '0000000000';
    el.btnSaveSettings.disabled = true;
    el.btnSaveSettings.textContent = 'Validating key...';

    try {
      const res = await fetch('/api/config/key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiKey }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'Failed to update key.');
      }

      el.userName.textContent = data.username.split('#')[0] || 'Anonymous';
      el.userKudos.textContent = `${Number(data.kudos || 0).toLocaleString()} Kudos`;
      el.modalAccountName.textContent = data.username;
      el.modalAccountKudos.textContent = Number(data.kudos || 0).toLocaleString();

      showToast(data.isAnonymous ? 'Saved as Anonymous (0000000000)' : `Connected as ${data.username}!`);
      close();
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      el.btnSaveSettings.disabled = false;
      el.btnSaveSettings.textContent = 'Save & Validate Key';
    }
  });
}

// ==========================================
// UI Helpers & Tab Switching
// ==========================================
function setupTabs() {
  el.tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  el.tabBtns.forEach((b) => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  el.tabPanels.forEach((p) => {
    p.classList.toggle('active', p.id === tabId);
  });
  state.activeTab = tabId;
}

function setupSliders() {
  el.imgSteps.addEventListener('input', (e) => {
    el.imgStepsVal.textContent = e.target.value;
  });
  el.imgCfg.addEventListener('input', (e) => {
    el.imgCfgVal.textContent = e.target.value;
  });
  el.textMaxTokens.addEventListener('input', (e) => {
    el.textMaxTokensVal.textContent = e.target.value;
  });
  el.textTemp.addEventListener('input', (e) => {
    el.textTempVal.textContent = e.target.value;
  });
}

function setupChips() {
  el.resChips.forEach((chip) => {
    chip.addEventListener('click', () => {
      el.resChips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      state.imageWidth = Number(chip.getAttribute('data-w'));
      state.imageHeight = Number(chip.getAttribute('data-h'));
    });
  });
}

function setupPromptButtons() {
  el.btnSampleImagePrompt.addEventListener('click', () => {
    const random = sampleImagePrompts[Math.floor(Math.random() * sampleImagePrompts.length)];
    el.imgPrompt.value = random;
    showToast('Loaded sample image prompt!');
  });

  el.btnSampleTextPrompt.addEventListener('click', () => {
    const random = sampleTextPrompts[Math.floor(Math.random() * sampleTextPrompts.length)];
    el.textPrompt.value = random;
    showToast('Loaded sample text prompt!');
  });
}

function showToast(message, type = 'info') {
  el.toast.textContent = message;
  el.toast.className = `toast ${type === 'error' ? 'toast-error' : ''}`;
  el.toast.classList.remove('hidden');

  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => {
    el.toast.classList.add('hidden');
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Start
document.addEventListener('DOMContentLoaded', init);
