/**
 * AuraStream Commercial-Grade Video Streaming Engine for Fire TV.
 * Manages hardware-accelerated HTML5 video playback, timeline scrubbing,
 * multi-modal frame extraction, and autoplay recovery state machine.
 */

class VideoPlayerEngine {
  constructor(videoId, canvasId) {
    this.video = document.getElementById(videoId);
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;

    this.streams = {
      stream_sintel: {
        title: "Sintel: The Dragon's Ascent",
        uri: "https://media.w3.org/2010/05/sintel/trailer.mp4",
        poster: "assets/tile04.jpg",
        genre: "Fantasy / Animation",
        badge: "FEATURED FILM",
      },
      stream_oceans: {
        title: "Deep Oceans: Abyssal Realms",
        uri: "https://vjs.zencdn.net/v/oceans.mp4",
        poster: "assets/tile05.jpg",
        genre: "Nature / Documentary",
        badge: "NATURE DOC",
      },
      stream_sailing: {
        title: "Costa Rica: Whale Tail Voyage",
        uri: "https://d1v0fxmwkpxbrg.cloudfront.net/boat-sailing.mp4",
        poster: "assets/tile06.jpg",
        genre: "Travel / Exploration",
        badge: "AMAZON REFERENCE",
      },
      stream_sports: {
        title: "Global Champions Cup: Madrid vs Manchester",
        uri: "https://media.w3.org/2010/05/bunny/movie.mp4",
        poster: "assets/tile07.jpg",
        genre: "Live Sports / Football",
        badge: "LIVE SPORTS",
      },
    };

    this.activeStreamId = 'stream_sintel';
    this.isPlaying = true;
    this.telemetryInterval = null;

    this.initVideoEvents();
  }

  get currentTime() {
    return this.video ? this.video.currentTime : 0;
  }

  get duration() {
    return this.video && this.video.duration ? this.video.duration : 52;
  }

  initVideoEvents() {
    if (!this.video) return;

    const affordance = document.getElementById('video-play-affordance');
    if (affordance) {
      affordance.addEventListener('click', () => {
        this.togglePlay();
      });
    }

    // Ensure muted autoplay succeeds per browser security policies
    this.video.muted = true;
    const playPromise = this.video.play();
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          this.isPlaying = true;
          this.updatePlaybackStateIcon(true);
          if (affordance) affordance.style.display = 'none';
        })
        .catch((err) => {
          console.warn('Autoplay prevented, displaying play affordance:', err);
          this.isPlaying = false;
          this.updatePlaybackStateIcon(false);
          if (affordance) affordance.style.display = 'flex';
        });
    }

    // Time update event
    this.video.addEventListener('timeupdate', () => {
      this.updateScrubUI();
    });

    // Buffered range update
    this.video.addEventListener('progress', () => {
      this.updateBufferedUI();
    });

    this.video.addEventListener('play', () => {
      this.isPlaying = true;
      this.updatePlaybackStateIcon(true);
      if (affordance) affordance.style.display = 'none';
    });

    this.video.addEventListener('pause', () => {
      this.isPlaying = false;
      this.updatePlaybackStateIcon(false);
      if (affordance) affordance.style.display = 'flex';
    });

    this.video.addEventListener('stalled', () => {
      console.warn('Video stream stalled, waiting for network...');
    });

    // Dispatch telemetry sync every second (single tracked interval)
    this.startTelemetryInterval();
  }

  startTelemetryInterval() {
    if (this.telemetryInterval) {
      clearInterval(this.telemetryInterval);
    }
    this.telemetryInterval = setInterval(() => {
      if (this.video && !this.video.paused) {
        window.dispatchEvent(
          new CustomEvent('tv:timeupdate', {
            detail: {
              currentTime: this.video.currentTime,
              streamId: this.activeStreamId,
            },
          })
        );
      }
    }, 1000);
  }

  updateScrubUI() {
    if (!this.video) return;
    const progressEl = document.getElementById('scrub-progress');
    const timeDisplayEl = document.getElementById('time-display');

    const cur = this.video.currentTime || 0;
    const dur = this.video.duration || 52;

    if (progressEl) {
      const pct = (cur / dur) * 100;
      progressEl.style.width = `${pct}%`;
    }

    if (timeDisplayEl) {
      const curM = Math.floor(cur / 60);
      const curS = Math.floor(cur % 60).toString().padStart(2, '0');
      const durM = Math.floor(dur / 60);
      const durS = Math.floor(dur % 60).toString().padStart(2, '0');
      timeDisplayEl.innerText = `${curM}:${curS} / ${durM}:${durS}`;
    }
  }

  updateBufferedUI() {
    if (!this.video || !this.video.buffered.length) return;
    const bufferedEl = document.getElementById('scrub-buffered');
    if (bufferedEl) {
      const bufferedEnd = this.video.buffered.end(this.video.buffered.length - 1);
      const dur = this.video.duration || 52;
      const pct = (bufferedEnd / dur) * 100;
      bufferedEl.style.width = `${pct}%`;
    }
  }

  updatePlaybackStateIcon(isPlaying) {
    const iconEl = document.getElementById('playback-state-icon');
    if (iconEl) {
      iconEl.innerText = isPlaying ? '❚❚' : '▶';
    }
  }

  togglePlay() {
    if (!this.video) return false;
    const affordance = document.getElementById('video-play-affordance');
    if (this.video.paused) {
      this.video.play();
      this.isPlaying = true;
      if (affordance) affordance.style.display = 'none';
    } else {
      this.video.pause();
      this.isPlaying = false;
      if (affordance) affordance.style.display = 'flex';
    }
    return this.isPlaying;
  }

  seek(delta) {
    if (!this.video) return;
    this.video.currentTime = Math.max(0, Math.min(this.duration, this.video.currentTime + delta));
  }

  restart() {
    if (!this.video) return;
    this.video.currentTime = 0;
    if (this.video.paused) {
      this.video.play().catch((e) => console.warn('Restart play prevented:', e));
    }
  }

  switchStream(streamId) {
    const stream = this.streams[streamId] || this.streams['stream_sintel'];
    if (!stream || !this.video) return;

    this.activeStreamId = streamId;
    this.video.src = stream.uri;
    if (stream.poster) {
      this.video.poster = stream.poster;
    }
    this.video.currentTime = 0;
    this.video.play().catch((e) => console.warn('Stream switch play prevented:', e));

    // Update Header metadata
    const titleEl = document.getElementById('stream-media-title');
    const badgeEl = document.getElementById('stream-pill-badge');
    if (titleEl) titleEl.innerText = stream.title;
    if (badgeEl) badgeEl.innerText = stream.badge;

    // Refresh X-Ray HUD telemetry immediately (even while paused)
    window.dispatchEvent(
      new CustomEvent('tv:stream-switch', {
        detail: { currentTime: 0, streamId: streamId },
      })
    );

    // Reset telemetry interval
    this.startTelemetryInterval();
  }

  captureFrameBase64() {
    if (!this.video || !this.canvas || !this.ctx) return null;
    try {
      this.canvas.width = 640;
      this.canvas.height = 360;
      this.ctx.drawImage(this.video, 0, 0, 640, 360);
      return this.canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
    } catch (e) {
      console.warn('Frame capture restricted (CORS), passing timestamp telemetry:', e);
      return null;
    }
  }

  setDim(isDimmed) {
    if (this.video) {
      if (isDimmed) {
        this.video.classList.add('xray-active');
      } else {
        this.video.classList.remove('xray-active');
      }
    }
    const dimLayer = document.getElementById('xray-backdrop-dim');
    if (dimLayer) {
      if (isDimmed) dimLayer.classList.add('active');
      else dimLayer.classList.remove('active');
    }
  }
}

window.VideoPlayer = VideoPlayerEngine;
