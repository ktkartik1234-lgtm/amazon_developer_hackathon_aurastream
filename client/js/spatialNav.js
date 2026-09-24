/**
 * Spatial Navigation & Focus Manager State Machine for Amazon Fire TV (Fire OS & Vega OS).
 * 
 * Context Hierarchy:
 * modal (Highest priority, focus-trapped)
 *   ↓ (Back dismisses)
 * cards (Insight X-Ray carousel, focus-trapped)
 *   ↓ (Back dismisses)
 * shelf (More Like This catalog)
 *   ↕ (Up/Down)
 * pills (Action Dock)
 *   ↕ (Up/Down)
 * controls (Video Playback Timeline & Scrub Bar)
 */

class SpatialNavigationManager {
  constructor() {
    this.focusGroups = {
      shelf: [],
      cards: [],
      pills: [],
      controls: [],
      modal: [],
    };

    this.currentContext = 'pills';
    this.currentIndex = 0;

    this.initKeyListeners();
    this.initRemoteMediaKeys();
  }

  registerGroup(contextName, elements) {
    this.focusGroups[contextName] = Array.from(elements || []);
  }

  setFocus(contextName, index = 0) {
    const group = this.focusGroups[contextName];
    if (!group || group.length === 0) return;

    this.currentContext = contextName;
    this.currentIndex = Math.max(0, Math.min(index, group.length - 1));

    // Remove focused class from all elements across all groups
    Object.values(this.focusGroups).flat().forEach((el) => {
      if (el && el.classList) {
        el.classList.remove('focused');
        if (typeof el.blur === 'function') el.blur();
      }
    });

    const activeEl = group[this.currentIndex];
    if (activeEl) {
      activeEl.classList.add('focused');
      if (typeof activeEl.focus === 'function') {
        activeEl.focus();
      }
      if (typeof activeEl.scrollIntoView === 'function') {
        activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }

  initKeyListeners() {
    window.addEventListener('keydown', (e) => {
      const key = e.key;
      const code = e.keyCode;

      // Handle Fire TV Back key (Escape 27 or Android Back Keycode 4 or Backspace)
      if (key === 'Escape' || key === 'Backspace' || code === 4 || code === 27) {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('tv:back'));
        return;
      }

      // Handle Select / Enter (DOM Enter 13, Keycode 66, Fire TV Center 23)
      if (key === 'Enter' || code === 13 || code === 66 || code === 23) {
        // If user is typing in text input, let default Enter behavior occur
        if (e.target && e.target.id === 'voice-text-input') {
          return;
        }

        e.preventDefault();
        const activeEl = this.focusGroups[this.currentContext]?.[this.currentIndex];
        if (activeEl) {
          activeEl.click();
        } else if (this.currentContext === 'controls') {
          if (window.PlayerInstance) {
            window.PlayerInstance.togglePlay();
          }
        }
        return;
      }

      // Handle Left (37 or 21)
      if (key === 'ArrowLeft' || code === 37 || code === 21) {
        e.preventDefault();
        this.navigate(-1, 0);
        return;
      }

      // Handle Right (39 or 22)
      if (key === 'ArrowRight' || code === 39 || code === 22) {
        e.preventDefault();
        this.navigate(1, 0);
        return;
      }

      // Handle Up (38 or 19)
      if (key === 'ArrowUp' || code === 38 || code === 19) {
        e.preventDefault();
        this.navigate(0, -1);
        return;
      }

      // Handle Down (40 or 20)
      if (key === 'ArrowDown' || code === 40 || code === 20) {
        e.preventDefault();
        this.navigate(0, 1);
        return;
      }

      // Alexa Voice trigger shortcut 'v' or 'V'
      if (key === 'v' || key === 'V') {
        // Only trigger if not currently typing in an input
        if (e.target && e.target.tagName === 'INPUT') return;
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('tv:voice-trigger'));
      }
    });
  }

  initRemoteMediaKeys() {
    // Document-level handlers for dedicated Fire TV Remote media hardware buttons
    window.addEventListener('keydown', (e) => {
      const code = e.keyCode;
      const key = e.key;

      // Play / Pause Toggle (MediaPlayPause 179 or 85)
      if (key === 'MediaPlayPause' || code === 179 || code === 85) {
        e.preventDefault();
        if (window.PlayerInstance) {
          window.PlayerInstance.togglePlay();
        }
      }

      // Fast Forward (MediaFastForward 228 or 90) -> seek +10s
      if (key === 'MediaFastForward' || code === 228 || code === 90) {
        e.preventDefault();
        if (window.PlayerInstance) {
          window.PlayerInstance.seek(10);
        }
      }

      // Rewind (MediaRewind 227 or 89) -> seek -10s
      if (key === 'MediaRewind' || code === 227 || code === 89) {
        e.preventDefault();
        if (window.PlayerInstance) {
          window.PlayerInstance.seek(-10);
        }
      }
    });
  }

  navigate(dx, dy) {
    // Context-trapped modes: modal and cards do not allow vertical escape via arrows
    if (this.currentContext === 'modal') {
      const group = this.focusGroups['modal'];
      if (!group || group.length === 0) return;
      const step = dx !== 0 ? dx : dy;
      const nextIdx = Math.max(0, Math.min(group.length - 1, this.currentIndex + step));
      this.setFocus('modal', nextIdx);
      return;
    }

    if (this.currentContext === 'cards') {
      const group = this.focusGroups['cards'];
      if (!group || group.length === 0) return;
      if (dx !== 0) {
        const nextIdx = Math.max(0, Math.min(group.length - 1, this.currentIndex + dx));
        this.setFocus('cards', nextIdx);
      }
      return;
    }

    // Horizontal navigation within active context
    if (dx !== 0) {
      if (this.currentContext === 'controls') {
        // In controls bar, left/right scrubs video by 5 seconds
        if (window.PlayerInstance) {
          window.PlayerInstance.seek(dx * 5);
        }
        return;
      }

      const group = this.focusGroups[this.currentContext];
      if (group && group.length > 0) {
        const nextIdx = this.currentIndex + dx;
        if (nextIdx >= 0 && nextIdx < group.length) {
          this.setFocus(this.currentContext, nextIdx);
        }
      }
      return;
    }

    // Vertical transitions between tiers: shelf <-> pills <-> controls
    if (dy < 0) {
      // UP ARROW
      if (this.currentContext === 'controls') {
        this.setFocus('pills', 0);
      } else if (this.currentContext === 'pills') {
        if (this.focusGroups.shelf && this.focusGroups.shelf.length > 0) {
          this.setFocus('shelf', 0);
        }
      }
    } else if (dy > 0) {
      // DOWN ARROW
      if (this.currentContext === 'shelf') {
        this.setFocus('pills', 0);
      } else if (this.currentContext === 'pills') {
        this.setFocus('controls', 0);
      }
    }
  }
}

window.SpatialNav = new SpatialNavigationManager();
