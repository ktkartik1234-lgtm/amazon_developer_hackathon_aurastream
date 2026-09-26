/**
 * AuraStream: Prime Video X-Ray Overlay & Cinema Interaction Manager.
 * Orchestrates:
 * - Dynamic X-Ray Tab Switching (In Scene, Music, Trivia, Tactical, Recap, Catalog)
 * - Auto-hiding HUD & 100% Full-Bleed Cinema Mode
 * - Authentic Alexa Living Room Bottom Light-Bar & Voice Reasoning Cards
 * - Time-Synchronized Subtitles
 */

class AuraOverlayManager {
  constructor() {
    this.headerEl = document.getElementById('tv-header');
    this.drawerEl = document.getElementById('xray-drawer');
    this.dimScrimEl = document.getElementById('video-dim-scrim');
    this.tabs = document.querySelectorAll('.xray-tab');
    this.trayPanes = document.querySelectorAll('.tray-pane');

    this.alexaBarEl = document.getElementById('alexa-voice-bar');
    this.alexaCardEl = document.getElementById('alexa-response-card');
    this.alexaTranscriptEl = document.getElementById('alexa-active-transcript');
    this.alexaBodyEl = document.getElementById('alexa-response-body');
    this.alexaModelTagEl = document.getElementById('alexa-model-tag');

    this.currentTab = 'cast';
    this.isHUDVisible = true;
    this.isAlexaBarOpen = false;
    this.isAlexaCardOpen = false;

    this.assetThumbnails = [
      'assets/tile01.jpg',
      'assets/tile02.jpg',
      'assets/tile03.jpg',
      'assets/tile04.jpg',
      'assets/tile05.jpg',
    ];

    this.initTabEvents();
    this.initAlexaEvents();
  }

  initTabEvents() {
    this.tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const tabId = tab.getAttribute('data-tab');
        this.switchTab(tabId);
      });
    });
  }

  switchTab(tabId) {
    this.currentTab = tabId;

    // Update active tab button style
    this.tabs.forEach((t) => {
      if (t.getAttribute('data-tab') === tabId) {
        t.classList.add('active');
      } else {
        t.classList.remove('active');
      }
    });

    // Display corresponding tray pane
    this.trayPanes.forEach((pane) => {
      if (pane.id === `tray-${tabId}`) {
        pane.style.display = 'block';
        pane.classList.add('active');
      } else {
        pane.style.display = 'none';
        pane.classList.remove('active');
      }
    });

    // Update spatial navigation focus targets for the active tray
    if (window.SpatialNav) {
      const activePane = document.getElementById(`tray-${tabId}`);
      if (activePane) {
        const focusables = activePane.querySelectorAll('[tabindex="0"]');
        window.SpatialNav.registerGroup('tray', focusables);
      }
    }
  }

  showHUD() {
    this.isHUDVisible = true;
    if (this.headerEl) this.headerEl.classList.remove('hidden');
    if (this.drawerEl) this.drawerEl.classList.remove('hidden');
    if (this.dimScrimEl) this.dimScrimEl.classList.add('active');
  }

  hideHUD() {
    if (this.isAlexaBarOpen || this.isAlexaCardOpen) return; // Keep visible if interacting with Alexa
    this.isHUDVisible = false;
    if (this.headerEl) this.headerEl.classList.add('hidden');
    if (this.drawerEl) this.drawerEl.classList.add('hidden');
    if (this.dimScrimEl) this.dimScrimEl.classList.remove('active');
  }

  toggleHUD() {
    if (this.isHUDVisible) {
      this.hideHUD();
    } else {
      this.showHUD();
    }
  }

  initAlexaEvents() {
    // Alexa prompt chips
    const chips = document.querySelectorAll('.alexa-chip');
    chips.forEach((chip) => {
      chip.addEventListener('click', async () => {
        const query = chip.getAttribute('data-query');
        this.executeAlexaQuery(query);
      });
    });

    window.addEventListener('tv:voice-trigger', () => {
      this.toggleAlexaBar();
    });

    window.addEventListener('tv:back', () => {
      if (this.isAlexaCardOpen) {
        this.closeAlexaCard();
      } else if (this.isAlexaBarOpen) {
        this.closeAlexaBar();
      } else if (this.isHUDVisible) {
        this.hideHUD();
      }
    });
  }

  toggleAlexaBar() {
    if (this.isAlexaBarOpen) {
      this.closeAlexaBar();
    } else {
      this.openAlexaBar();
    }
  }

  openAlexaBar() {
    this.isAlexaBarOpen = true;
    if (this.alexaBarEl) {
      this.alexaBarEl.style.display = 'flex';
    }
    this.showHUD();

    if (window.SpatialNav) {
      const chips = document.querySelectorAll('.alexa-chip');
      window.SpatialNav.registerGroup('alexa', chips);
      window.SpatialNav.setFocus('alexa', 0);
    }
  }

  closeAlexaBar() {
    this.isAlexaBarOpen = false;
    if (this.alexaBarEl) {
      this.alexaBarEl.style.display = 'none';
    }
    if (window.SpatialNav) {
      window.SpatialNav.setFocus('tabs', 0);
    }
  }

  async executeAlexaQuery(query) {
    if (this.alexaTranscriptEl) {
      this.alexaTranscriptEl.innerText = `"${query}"`;
    }

    const player = window.PlayerInstance;
    const streamId = player ? player.activeStreamId : 'stream_sintel';
    const currentTime = player ? player.currentTime : 0;
    const frameBase64 = player ? player.captureFrameBase64() : null;

    // Send query to AWS Bedrock via AuraStream API
    const res = await window.AuraStreamAPI.sendMultimodalQuery(
      streamId,
      currentTime,
      query,
      frameBase64
    );

    this.showAlexaResponse(query, res);
  }

  showAlexaResponse(query, res) {
    this.isAlexaCardOpen = true;
    if (this.alexaBarEl) this.alexaBarEl.style.display = 'none';

    if (this.alexaCardEl) {
      this.alexaCardEl.style.display = 'block';
    }
    if (this.alexaBodyEl) {
      this.alexaBodyEl.innerText = res.summary || (res.insights && res.insights[0]) || 'Analysis complete.';
    }
    if (this.alexaModelTagEl) {
      this.alexaModelTagEl.innerText = `${res.model_used} • ${(res.confidence_score * 100).toFixed(0)}% Confidence`;
    }

    // Auto-switch to the relevant X-Ray tab for rich context
    const qLower = query.toLowerCase();
    if (qLower.includes('soundtrack') || qLower.includes('song') || qLower.includes('music')) {
      this.switchTab('music');
    } else if (qLower.includes('tactic') || qLower.includes('soccer') || qLower.includes('formation')) {
      this.switchTab('tactics');
    } else if (qLower.includes('recap') || qLower.includes('catch up') || qLower.includes('plot')) {
      this.switchTab('recap');
    } else if (qLower.includes('who') || qLower.includes('actor') || qLower.includes('cast')) {
      this.switchTab('cast');
    }
  }

  closeAlexaCard() {
    this.isAlexaCardOpen = false;
    if (this.alexaCardEl) {
      this.alexaCardEl.style.display = 'none';
    }
    if (window.SpatialNav) {
      window.SpatialNav.setFocus('tabs', 0);
    }
  }

  updateHUD(telem) {
    if (!telem) return;

    // 1. Update In Scene Cast
    const castRow = document.getElementById('cast-cards-row');
    const countBadge = document.getElementById('cast-count-badge');
    if (countBadge) {
      countBadge.innerText = (telem.actors_in_scene || []).length;
    }

    if (castRow && telem.actors_in_scene && telem.actors_in_scene.length) {
      castRow.innerHTML = telem.actors_in_scene
        .map((actor, idx) => {
          const thumb = this.assetThumbnails[idx % this.assetThumbnails.length];
          const conf = Math.round((actor.confidence || 0.95) * 100);
          return `
            <div class="cast-card ${idx === 0 ? 'focused' : ''}" tabindex="0">
              <div class="cast-portrait-wrap">
                <img class="cast-portrait" src="${thumb}" alt="${actor.name}">
                <span class="verified-glyph" title="Verified Cast">✓</span>
              </div>
              <div class="cast-details">
                <div class="character-name">${actor.character || actor.name}</div>
                <div class="actor-name">${actor.name}</div>
                <div class="role-tag">${actor.bio_snippet || 'Cast Member'}</div>
                <div class="confidence-tag">${conf}% Bedrock Match</div>
              </div>
            </div>
          `;
        })
        .join('');

      // Re-register with SpatialNav if cast tab is active
      if (this.currentTab === 'cast' && window.SpatialNav) {
        const cards = castRow.querySelectorAll('.cast-card');
        window.SpatialNav.registerGroup('tray', cards);
      }
    }

    // 2. Update Soundtrack
    const trackEl = document.getElementById('tray-soundtrack-title');
    if (trackEl && telem.soundtrack) {
      trackEl.innerText = telem.soundtrack;
    }

    // 3. Update Trivia
    const triviaEl = document.getElementById('tray-trivia-text');
    if (triviaEl && telem.trivia_fact) {
      triviaEl.innerText = telem.trivia_fact;
    }

    // 4. Update Header stream title & genre badge
    const titleEl = document.getElementById('stream-media-title');
    const badgeEl = document.getElementById('stream-pill-badge');
    if (titleEl && telem.title) titleEl.innerText = telem.title;
    if (badgeEl && telem.genre) badgeEl.innerText = telem.genre.toUpperCase();
  }

  getActiveSubtitle(streamId, currentTime) {
    const db = window.AuraSceneDatabase;
    if (!db || !db[streamId]) return null;
    const timeline = db[streamId].timeline || [];
    for (const entry of timeline) {
      const [start, end] = entry.time_range;
      if (currentTime >= start && currentTime <= end) {
        return entry.subtitles || null;
      }
    }
    return null;
  }
}

window.AuraOverlay = new AuraOverlayManager();
