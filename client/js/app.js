/**
 * AuraStream Fire TV Application Orchestrator.
 * Connects Video Player, Media Shelf, Spatial Navigation, Aura HUD, and Backend MCP Services.
 * Features:
 * - Dynamic Viewport Scaling preserving 1080p geometry at any screen resolution
 * - Non-blocking Glassmorphic Ambient Toast Notifications (zero alert() calls)
 * - Coordinated stream switching with canonical streamData.js
 */

// Viewport Scaling Engine for 10-foot TV UI
function setupTVViewportScaling() {
  const root = document.getElementById('tv-app-root');
  if (!root) return;

  function applyScale() {
    const targetW = 1920;
    const targetH = 1080;
    const availW = window.innerWidth;
    const availH = window.innerHeight;

    const scale = Math.min(availW / targetW, availH / targetH);
    const offsetX = (availW - targetW * scale) / 2;
    const offsetY = (availH - targetH * scale) / 2;

    root.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
    root.style.transformOrigin = 'top left';
  }

  window.addEventListener('resize', applyScale);
  applyScale();
}

// Glassmorphic Non-Blocking Toast Notification System
function showToast(title, message, durationMs = 4000) {
  const toastEl = document.getElementById('aura-toast');
  const titleEl = document.getElementById('toast-title');
  const msgEl = document.getElementById('toast-message');

  if (!toastEl) return;
  if (titleEl) titleEl.innerText = title;
  if (msgEl) msgEl.innerText = message;

  toastEl.style.display = 'flex';
  // Trigger CSS animation on next tick
  requestAnimationFrame(() => {
    toastEl.classList.add('visible');
  });

  clearTimeout(window._toastTimer);
  window._toastTimer = setTimeout(() => {
    toastEl.classList.remove('visible');
    setTimeout(() => {
      toastEl.style.display = 'none';
    }, 400);
  }, durationMs);
}
window.showToast = showToast;

document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing AuraStream Prime Video X-Ray Experience...');

  // Initialize Viewport Scaling First
  setupTVViewportScaling();

  // Initialize Video Engine with real HTML5 Video
  const player = new window.VideoPlayer('hero-video', 'hero-video-canvas');
  window.PlayerInstance = player;

  // Register Focus Groups for Spatial Navigation
  const pills = document.querySelectorAll('.tv-pill');
  const shelfTiles = document.querySelectorAll('.shelf-tile');
  const controls = document.querySelectorAll('#video-controls');

  if (window.SpatialNav) {
    window.SpatialNav.registerGroup('pills', pills);
    window.SpatialNav.registerGroup('shelf', shelfTiles);
    window.SpatialNav.registerGroup('controls', controls);
    window.SpatialNav.setFocus('pills', 0);
  }

  // Wire Media Shelf Tiles (Click / Enter switches stream)
  shelfTiles.forEach((tile) => {
    tile.addEventListener('click', () => {
      const streamId = tile.getAttribute('data-stream');
      const title = tile.getAttribute('data-title');
      console.log(`Switching to title: ${title} (${streamId})`);

      player.switchStream(streamId);

      // Visual focus update
      shelfTiles.forEach((t) => t.classList.remove('focused'));
      tile.classList.add('focused');
    });
  });

  // Wire Quick Action Pills
  pills.forEach((pill) => {
    pill.addEventListener('click', async () => {
      const action = pill.getAttribute('data-action');
      console.log(`Action selected: ${action}`);

      // Visual pill active state
      pills.forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');

      const frameBase64 = player.captureFrameBase64();

      if (action === 'who') {
        const res = await window.AuraStreamAPI.sendMultimodalQuery(
          player.activeStreamId,
          player.currentTime,
          'Who is on screen?',
          frameBase64
        );
        window.AuraOverlay.showCards(res.trivia_cards);
      } else if (action === 'tactics') {
        if (player.activeStreamId !== 'stream_sports') {
          player.switchStream('stream_sports');
        }
        const res = await window.AuraStreamAPI.sendMultimodalQuery(
          player.activeStreamId,
          player.currentTime,
          'Explain this tactical soccer play',
          frameBase64
        );
        window.AuraOverlay.showCards(res.trivia_cards);
      } else if (action === 'music') {
        const res = await window.AuraStreamAPI.sendMultimodalQuery(
          player.activeStreamId,
          player.currentTime,
          'What soundtrack is playing right now?',
          frameBase64
        );
        window.AuraOverlay.showCards(res.trivia_cards);
      } else if (action === 'recap') {
        const res = await window.AuraStreamAPI.sendMultimodalQuery(
          player.activeStreamId,
          player.currentTime,
          'Catch me up (Spoiler-Free)',
          frameBase64
        );
        window.AuraOverlay.showCards(res.trivia_cards);
      } else if (action === 'ambient') {
        const res = await window.AuraStreamAPI.adaptAmbient('family', 'medium', 'PG-13');
        const nextState = !subtitlesEnabled;
        setSubtitles(nextState, false);
        window.showToast(
          'Aura Living Room Ambient Mode Active',
          `Dialogue Boost: +4.5dB • Subtitles: Adaptive ${nextState ? 'ON' : 'OFF'} • Rating Cap: PG-13`
        );
      } else if (action === 'switch-stream') {
        const nextStream =
          player.activeStreamId === 'stream_sintel'
            ? 'stream_oceans'
            : player.activeStreamId === 'stream_oceans'
            ? 'stream_sailing'
            : player.activeStreamId === 'stream_sailing'
            ? 'stream_sports'
            : 'stream_sintel';
        player.switchStream(nextStream);
        updateSubtitleCue(player.activeStreamId, 0);
      }
    });
  });

  // Subtitle Synchronization Engine (BUG-14)
  let subtitlesEnabled = false;

  function setSubtitles(enabled, isLarge = false) {
    subtitlesEnabled = enabled;
    const subEl = document.getElementById('vtt-subtitle-display');
    if (!subEl) return;
    if (subtitlesEnabled) {
      if (isLarge) subEl.classList.add('large');
      else subEl.classList.remove('large');
      updateSubtitleCue(player.activeStreamId, player.currentTime);
    } else {
      subEl.style.display = 'none';
    }
  }

  function updateSubtitleCue(streamId, currentTime) {
    if (!subtitlesEnabled) return;
    const subEl = document.getElementById('vtt-subtitle-display');
    if (!subEl) return;
    const cue = window.AuraOverlay.getActiveSubtitle(streamId, currentTime);
    if (cue) {
      subEl.innerText = cue;
      subEl.style.display = 'block';
    } else {
      subEl.style.display = 'none';
    }
  }

  // Keyboard shortcut C for Closed Captions toggle
  window.addEventListener('keydown', (e) => {
    if (e.key === 'c' || e.key === 'C') {
      const nextState = !subtitlesEnabled;
      setSubtitles(nextState, false);
      window.showToast(
        nextState ? 'Subtitles ON' : 'Subtitles OFF',
        nextState ? 'Adaptive living room subtitles enabled' : 'Subtitles disabled'
      );
    }
  });

  // Sync HUD telemetry on timeupdate
  let lastFetchedSecond = -1;
  window.addEventListener('tv:timeupdate', async (e) => {
    const { currentTime, streamId } = e.detail;
    const currentInt = Math.floor(currentTime);

    // Update subtitles in real-time
    updateSubtitleCue(streamId, currentTime);

    if (currentInt % 4 === 0 && currentInt !== lastFetchedSecond) {
      lastFetchedSecond = currentInt;
      const telem = await window.AuraStreamAPI.getTelemetry(streamId, currentTime);
      window.AuraOverlay.updateHUD(telem);
    }
  });

  // Handle Alexa Voice Trigger
  window.addEventListener('tv:execute-query', async (e) => {
    const query = e.detail.query;
    console.log(`Executing voice query: "${query}"`);
    const frameBase64 = player.captureFrameBase64();
    const res = await window.AuraStreamAPI.sendMultimodalQuery(
      player.activeStreamId,
      player.currentTime,
      query,
      frameBase64
    );
    window.AuraOverlay.showCards(res.trivia_cards);
  });

  console.log('AuraStream Prime Video X-Ray Ready.');
});
