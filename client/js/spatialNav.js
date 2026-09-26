/**
 * Spatial Navigation & Focus Manager State Machine for Amazon Fire TV.
 * Manages D-Pad navigation across Prime Video X-Ray Tabs, Content Tray, and Alexa Voice Bar.
 * 
 * Hierarchy:
 * alexa (Top priority when Voice Bar is active)
 *   ↓
 * tabs (X-Ray Navigation: In Scene | Music | Trivia | Tactical | Recap | Catalog)
 *   ↕ (Up / Down)
 * tray (Active items: Cast cards, Music details, Trivia, Tactics, Shelf tiles)
 */

class SpatialNavigationManager {
  constructor() {
    this.focusGroups = {
      tabs: [],
      tray: [],
      alexa: [],
    };

    this.currentContext = 'tabs';
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

    // Clear focus from all elements
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

      // Handle Fire TV Back key (Escape 27, Android Back 4, Backspace 8)
      if (key === 'Escape' || key === 'Backspace' || code === 4 || code === 27) {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('tv:back'));
        return;
      }

      // Handle Select / Enter (DOM Enter 13, Keycode 66, Fire TV Center 23)
      if (key === 'Enter' || code === 13 || code === 66 || code === 23) {
        e.preventDefault();
        const activeEl = this.focusGroups[this.currentContext]?.[this.currentIndex];
        if (activeEl) {
          activeEl.click();
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

      // Spacebar toggles Play / Pause and toggles X-Ray
      if (key === ' ' || code === 32) {
        e.preventDefault();
        if (window.PlayerInstance) {
          window.PlayerInstance.togglePlay();
        }
        return;
      }

      // Alexa Voice trigger shortcut 'v' or 'V'
      if (key === 'v' || key === 'V') {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent('tv:voice-trigger'));
        return;
      }
    });
  }

  initRemoteMediaKeys() {
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
    // If Alexa bar is open, horizontal navigation moves across chips
    if (this.currentContext === 'alexa') {
      const group = this.focusGroups['alexa'];
      if (!group || group.length === 0) return;
      const step = dx !== 0 ? dx : dy;
      const nextIdx = Math.max(0, Math.min(group.length - 1, this.currentIndex + step));
      this.setFocus('alexa', nextIdx);
      return;
    }

    // Horizontal navigation within active context
    if (dx !== 0) {
      const group = this.focusGroups[this.currentContext];
      if (group && group.length > 0) {
        const nextIdx = this.currentIndex + dx;
        if (nextIdx >= 0 && nextIdx < group.length) {
          this.setFocus(this.currentContext, nextIdx);
          // If navigating across tabs, switch the tab content immediately
          if (this.currentContext === 'tabs') {
            const activeTab = group[nextIdx];
            if (activeTab) {
              const tabId = activeTab.getAttribute('data-tab');
              if (window.AuraOverlay) {
                window.AuraOverlay.switchTab(tabId);
              }
            }
          }
        }
      }
      return;
    }

    // Vertical navigation between tabs and tray
    if (dy < 0) {
      // UP ARROW: if in tray, move to tabs
      if (this.currentContext === 'tray') {
        this.setFocus('tabs', 0);
      }
    } else if (dy > 0) {
      // DOWN ARROW: if in tabs, move into active tray
      if (this.currentContext === 'tabs') {
        const trayGroup = this.focusGroups['tray'];
        if (trayGroup && trayGroup.length > 0) {
          this.setFocus('tray', 0);
        }
      }
    }
  }
}

window.SpatialNav = new SpatialNavigationManager();
