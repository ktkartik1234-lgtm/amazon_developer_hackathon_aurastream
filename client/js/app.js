/**
 * AuraStream Fire TV Application Orchestrator.
 * Connects Video Player, Prime Video X-Ray Drawer, Spatial Navigation, Alexa Voice Bar, and Backend Services.
 * Features:
 * - Dynamic Viewport Scaling preserving 1080p geometry at any screen resolution
 * - Inactivity Auto-Hide Engine (4.0s fade into 100% full-bleed cinema video)
 * - Coordinated stream switching with canonical streamData.js
 * - Real-time telemetry and subtitle synchronization
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
function showToast(title, message, durationMs = 3500) {
  const toastEl = document.getElementById('aura-toast');
  const titleEl = document.getElementById('toast-title');
  const msgEl = document.getElementById('toast-message');

  if (!toastEl) return;
  if (titleEl) titleEl.innerText = title;
  if (msgEl) msgEl.innerText = message;

  toastEl.style.display = 'flex';
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

  // 1. Initialize Viewport Scaling
  setupTVViewportScaling();

  // 2. Initialize Video Engine with HTML5 Video
  const player = new window.VideoPlayer('hero-video', 'hero-video-canvas');
  window.PlayerInstance = player;

  // 3. Register Focus Groups with Spatial Navigation
  const tabs = document.querySelectorAll('.xray-tab');
  const activeCastCards = document.querySelectorAll('#tray-cast .cast-card');
  const shelfTiles = document.querySelectorAll('.shelf-tile');

  if (window.SpatialNav) {
    window.SpatialNav.registerGroup('tabs', tabs);
    window.SpatialNav.registerGroup('tray', activeCastCards);
    window.SpatialNav.setFocus('tabs', 0);
  }

  // 4. Wire Catalog Shelf Tiles (Click / Enter switches stream)
  shelfTiles.forEach((tile) => {
    tile.addEventListener('click', () => {
      const streamId = tile.getAttribute('data-stream');
      const title = tile.getAttribute('data-title');
      console.log(`Switching to title: ${title} (${streamId})`);

      player.switchStream(streamId);

      // Visual focus update
      shelfTiles.forEach((t) => t.classList.remove('focused'));
      tile.classList.add('focused');

      window.showToast('Switching Stream', title);
      updateSubtitleCue(streamId, 0);

      // Auto-switch to cast tab for the new movie
      if (window.AuraOverlay) {
        window.AuraOverlay.switchTab('cast');
      }
    });
  });

  // 5. Inactivity Auto-Hide Engine for 100% Full-Bleed Cinema Experience
  let hideTimeout = null;
  function resetInactivityTimer() {
    if (window.AuraOverlay) {
      window.AuraOverlay.showHUD();
    }
    clearTimeout(hideTimeout);
    // If video is playing, auto-hide HUD after 4.0 seconds of no interaction
    if (player && player.isPlaying) {
      hideTimeout = setTimeout(() => {
        if (player.isPlaying && window.AuraOverlay) {
          window.AuraOverlay.hideHUD();
        }
      }, 4000);
    }
  }

  // Any keypress or mouse movement reveals HUD and resets timer
  window.addEventListener('keydown', () => resetInactivityTimer());
  window.addEventListener('mousemove', () => resetInactivityTimer());

  // 5b. Alexa+ / MCP Fire TV Command Bus (Server-Sent Events).
  // Remote surfaces (Alexa+ voice, MCP tools, REST callers) drive this TV live.
  function handleFireTvCommand(cmd) {
    if (!cmd || !cmd.command) return;
    const arg = cmd.argument || null;
    switch (cmd.command) {
      case 'play':
        if (player.video && player.video.paused) player.togglePlay();
        break;
      case 'pause':
        if (player.video && !player.video.paused) player.togglePlay();
        break;
      case 'toggle_playback':
        player.togglePlay();
        break;
      case 'seek_forward':
        player.seek(10);
        break;
      case 'seek_back':
        player.seek(-10);
        break;
      case 'restart':
        player.restart();
        break;
      case 'switch_stream':
        if (arg && player.streams[arg]) {
          player.switchStream(arg);
          updateSubtitleCue(arg, 0);
          if (window.AuraOverlay) window.AuraOverlay.switchTab('cast');
        }
        break;
      case 'open_xray':
        if (window.AuraOverlay) window.AuraOverlay.showHUD();
        break;
      case 'toggle_subtitles':
        setSubtitles(!subtitlesEnabled, false);
        break;
      case 'hide_hud':
        if (window.AuraOverlay) window.AuraOverlay.hideHUD();
        break;
      default:
        return;
    }
    window.showToast(
      'Alexa+ Command',
      `${cmd.command.replace(/_/g, ' ')}${arg ? `: ${arg}` : ''} • via ${cmd.source || 'remote'}`
    );
  }
  window.AuraStreamAPI.subscribeFireTvCommands(handleFireTvCommand);

  // 5c. Adaptive Ambient Household Mode ('A' key) — applies audio/subtitle/rating
  // adaptation through the /api/ambient-adapt endpoint.
  window.addEventListener('tv:ambient-adapt', async () => {
    const res = await window.AuraStreamAPI.adaptAmbient('family', 'medium', 'PG-13');
    const cmds = res.fire_tv_commands || {};
    window.showToast(
      'Ambient Mode Adapted',
      `Dialogue Boost: +${cmds.dialogue_boost_db || 0}dB • Subtitles: ${cmds.subtitles_enabled ? 'ON' : 'OFF'} • Rating Cap: ${cmds.content_safety_filter || 'PG-13'}`
    );
  });

  // 6. Subtitle Synchronization Engine (BUG-14)
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

  // 7. Sync HUD telemetry on timeupdate
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

  // 7b. Immediate X-Ray HUD refresh on stream switch (even while paused)
  window.addEventListener('tv:stream-switch', async (e) => {
    const { currentTime, streamId } = e.detail;
    const telem = await window.AuraStreamAPI.getTelemetry(streamId, currentTime);
    window.AuraOverlay.updateHUD(telem);
  });

  console.log('AuraStream Cinema-Grade Prime Video X-Ray Ready.');
});
