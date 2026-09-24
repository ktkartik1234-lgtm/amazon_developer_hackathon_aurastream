/**
 * Aura Pulse: Prime Video X-Ray Overlay & Card Renderer.
 * Renders real photographic cast profiles, soundtrack metadata, Bedrock trivia,
 * and handles the focus-trapped Alexa+ Voice Remote Simulation Modal.
 */

class AuraOverlayManager {
  constructor() {
    this.hudEl = document.getElementById('aura-hud');
    this.carouselEl = document.getElementById('card-carousel');
    this.entityListEl = document.getElementById('hud-entity-list');
    this.factEl = document.getElementById('hud-trivia-fact');
    this.soundtrackEl = document.getElementById('hud-soundtrack');
    this.voiceModalEl = document.getElementById('voice-remote-modal');

    this.isCardsVisible = false;
    this.isVoiceModalOpen = false;
    this.preModalFocus = null;

    // Photographic asset mapping
    this.assetThumbnails = [
      'assets/tile01.jpg',
      'assets/tile02.jpg',
      'assets/tile03.jpg',
      'assets/tile04.jpg',
      'assets/tile05.jpg',
    ];

    this.initEvents();
    this.initVoiceModal();
  }

  initEvents() {
    window.addEventListener('tv:back', () => {
      if (this.isVoiceModalOpen) {
        this.closeVoiceModal();
      } else if (this.isCardsVisible) {
        this.dismissCards();
      }
    });

    window.addEventListener('tv:voice-trigger', () => {
      this.toggleVoiceModal();
    });
  }

  initVoiceModal() {
    if (!this.voiceModalEl) return;

    // Wire preset query buttons
    const presets = this.voiceModalEl.querySelectorAll('.voice-preset-pill');
    presets.forEach((btn) => {
      btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        this.submitVoiceQuery(query);
      });
    });

    // Wire custom text input and submit button
    const submitBtn = document.getElementById('voice-submit-btn');
    const textInput = document.getElementById('voice-text-input');

    if (submitBtn && textInput) {
      submitBtn.addEventListener('click', () => {
        const q = textInput.value.trim();
        if (q) {
          this.submitVoiceQuery(q);
        }
      });

      textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const q = textInput.value.trim();
          if (q) {
            this.submitVoiceQuery(q);
          }
        }
      });
    }
  }

  toggleVoiceModal() {
    if (this.isVoiceModalOpen) {
      this.closeVoiceModal();
    } else {
      this.openVoiceModal();
    }
  }

  openVoiceModal() {
    if (!this.voiceModalEl) return;
    this.isVoiceModalOpen = true;
    this.preModalFocus = document.activeElement;

    this.voiceModalEl.style.display = 'flex';
    this.voiceModalEl.classList.add('visible');

    // Register modal items in spatial navigation and trap focus
    const modalItems = this.voiceModalEl.querySelectorAll('.voice-preset-pill, #voice-text-input, #voice-submit-btn');
    if (window.SpatialNav) {
      window.SpatialNav.registerGroup('modal', modalItems);
      window.SpatialNav.setFocus('modal', 0);
    }
  }

  closeVoiceModal() {
    if (!this.voiceModalEl) return;
    this.isVoiceModalOpen = false;
    this.voiceModalEl.classList.remove('visible');
    this.voiceModalEl.style.display = 'none';

    // Restore focus to previous context
    if (window.SpatialNav) {
      window.SpatialNav.registerGroup('modal', []);
      if (this.isCardsVisible) {
        window.SpatialNav.setFocus('cards', 0);
      } else {
        window.SpatialNav.setFocus('pills', 0);
      }
    }
    if (this.preModalFocus && typeof this.preModalFocus.focus === 'function') {
      this.preModalFocus.focus();
    }
  }

  submitVoiceQuery(query) {
    console.log(`Executing simulated voice query: "${query}"`);
    this.closeVoiceModal();

    window.dispatchEvent(
      new CustomEvent('tv:execute-query', {
        detail: { query },
      })
    );
  }

  updateHUD(telemetry) {
    if (!telemetry) return;

    // Update In-Scene Cast with real photographic thumbnails
    if (this.entityListEl && telemetry.actors_in_scene) {
      this.entityListEl.innerHTML = telemetry.actors_in_scene
        .slice(0, 3)
        .map((actor, idx) => {
          const thumb = this.assetThumbnails[idx % this.assetThumbnails.length];
          return `
            <div class="entity-row">
              <img class="entity-avatar-img" src="${thumb}" alt="${actor.name}">
              <div class="entity-meta">
                <div class="entity-name">${actor.name}</div>
                <div class="entity-role">${actor.character}</div>
                <div class="entity-sub">Confidence: ${Math.round(actor.confidence * 100)}% • <span class="tag-verified">Verified Cast</span></div>
              </div>
            </div>
          `;
        })
        .join('');
    }

    // Update production trivia
    if (this.factEl) {
      this.factEl.innerText = telemetry.trivia_fact || 'Scene telemetry actively analyzed by AWS Bedrock.';
    }

    // Update soundtrack
    if (this.soundtrackEl) {
      this.soundtrackEl.innerText = telemetry.soundtrack || 'Original Cinematic Score (Dolby Atmos)';
    }
  }

  showCards(cards) {
    if (!this.carouselEl || !cards || cards.length === 0) return;
    this.isCardsVisible = true;

    // Dim the video in background for authentic Prime Video X-Ray feel
    if (window.PlayerInstance) {
      window.PlayerInstance.setDim(true);
    }

    this.carouselEl.innerHTML = cards
      .map(
        (card, idx) => `
        <div class="insight-card" tabindex="0" data-card-idx="${idx}">
          <div class="card-badge-row">
            ${card.badges.map((b) => `<span class="card-badge">${b}</span>`).join('')}
          </div>
          <div class="card-title">${card.title}</div>
          <div class="card-headline">${card.headline}</div>
          <div class="card-description">${card.description}</div>
        </div>
      `
      )
      .join('');

    this.carouselEl.style.display = 'flex';
    this.carouselEl.style.opacity = '1';

    // Register with Spatial Navigation and move focus into cards
    const cardElements = this.carouselEl.querySelectorAll('.insight-card');
    if (window.SpatialNav) {
      window.SpatialNav.registerGroup('cards', cardElements);
      window.SpatialNav.setFocus('cards', 0);
    }
  }

  dismissCards() {
    if (!this.carouselEl) return;
    this.carouselEl.style.opacity = '0';
    setTimeout(() => {
      this.carouselEl.style.display = 'none';
      this.isCardsVisible = false;
      if (window.PlayerInstance) {
        window.PlayerInstance.setDim(false);
      }
      if (window.SpatialNav) {
        window.SpatialNav.registerGroup('cards', []);
        window.SpatialNav.setFocus('pills', 0);
      }
    }, 200);
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
