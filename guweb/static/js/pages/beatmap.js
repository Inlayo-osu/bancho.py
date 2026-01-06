/**
 * Beatmap Page - Optimized Vanilla JavaScript
 */

class BeatmapPage {
  constructor(beatmapId, mode = 0) {
    this.beatmapId = beatmapId;
    this.currentMode = mode;
    this.currentMods = 0;
    this.data = null;
    this.selectedDiff = null;
    
    this.init();
  }

  init() {
    this.container = document.getElementById('beatmap-app');
    if (!this.container) return;
    
    this.setupModeSelector();
    this.setupDiffSelector();
    this.loadBeatmap();
  }

  setupModeSelector() {
    const modeButtons = document.querySelectorAll('.mode-btn');
    modeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = parseInt(btn.dataset.mode);
        this.changeMode(mode);
      });
    });
  }

  setupDiffSelector() {
    const diffButtons = document.querySelectorAll('.diff-btn');
    diffButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const diffId = parseInt(btn.dataset.diffId);
        this.changeDifficulty(diffId);
      });
    });
  }

  async loadBeatmap() {
    Utils.setLoading(this.container, true);
    
    try {
      this.data = await api.get('/v1/get_map_info', {
        id: this.beatmapId,
        mode: this.currentMode,
        mods: this.currentMods
      });
      
      this.render();
    } catch (error) {
      console.error('Failed to load beatmap:', error);
      toast.error('Failed to load beatmap data');
    } finally {
      Utils.setLoading(this.container, false);
    }
  }

  async loadScores() {
    const scoresContainer = document.getElementById('beatmap-scores');
    if (!scoresContainer) return;
    
    const spinner = LoadingComponent.show(scoresContainer);
    
    try {
      const scores = await api.get('/v1/get_map_scores', {
        id: this.beatmapId,
        mode: this.currentMode,
        mods: this.currentMods,
        scope: 'best',
        limit: 50
      });
      
      this.renderScores(scores);
    } catch (error) {
      console.error('Failed to load scores:', error);
      scoresContainer.innerHTML = '<div class="error-state">Failed to load scores</div>';
    } finally {
      LoadingComponent.hide(spinner);
    }
  }

  changeMode(mode) {
    this.currentMode = mode;
    
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.toggle('active', parseInt(btn.dataset.mode) === mode);
    });
    
    this.loadScores();
  }

  changeDifficulty(diffId) {
    this.beatmapId = diffId;
    
    document.querySelectorAll('.diff-btn').forEach(btn => {
      btn.classList.toggle('active', parseInt(btn.dataset.diffId) === diffId);
    });
    
    this.loadBeatmap();
  }

  render() {
    if (!this.data) return;
    
    this.renderBeatmapInfo();
    this.loadScores();
  }

  renderBeatmapInfo() {
    const beatmap = this.data.beatmap;
    
    const elements = {
      title: document.getElementById('beatmap-title'),
      artist: document.getElementById('beatmap-artist'),
      mapper: document.getElementById('beatmap-mapper'),
      diff: document.getElementById('beatmap-diff'),
      bpm: document.getElementById('beatmap-bpm'),
      length: document.getElementById('beatmap-length'),
      cs: document.getElementById('beatmap-cs'),
      ar: document.getElementById('beatmap-ar'),
      od: document.getElementById('beatmap-od'),
      hp: document.getElementById('beatmap-hp')
    };
    
    if (elements.title) elements.title.textContent = beatmap.title;
    if (elements.artist) elements.artist.textContent = beatmap.artist;
    if (elements.mapper) elements.mapper.textContent = beatmap.creator;
    if (elements.diff) elements.diff.textContent = beatmap.diff.toFixed(2);
    if (elements.bpm) elements.bpm.textContent = beatmap.bpm;
    if (elements.length) elements.length.textContent = Utils.formatLength(beatmap.total_length);
    if (elements.cs) elements.cs.textContent = beatmap.cs;
    if (elements.ar) elements.ar.textContent = beatmap.ar;
    if (elements.od) elements.od.textContent = beatmap.od;
    if (elements.hp) elements.hp.textContent = beatmap.hp;
  }

  renderScores(scores) {
    const container = document.getElementById('beatmap-scores');
    if (!container) return;
    
    if (scores.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-trophy"></i>
          <p>No scores on this beatmap yet</p>
        </div>
      `;
      return;
    }
    
    const table = document.createElement('table');
    table.className = 'scores-table';
    table.innerHTML = `
      <thead>
        <tr>
          <th>Rank</th>
          <th>Player</th>
          <th>Score</th>
          <th>Accuracy</th>
          <th>PP</th>
          <th>Mods</th>
          <th>Grade</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        ${scores.map((score, i) => this.createScoreRow(score, i + 1)).join('')}
      </tbody>
    `;
    
    container.innerHTML = '';
    container.appendChild(table);
  }

  createScoreRow(score, rank) {
    const mods = Utils.getModsString(score.mods);
    const gradeClass = Utils.getGradeClass(score.grade);
    
    return `
      <tr class="score-row">
        <td class="rank">#${rank}</td>
        <td class="player">
          <img src="/static/images/flags/${score.user.country}.png" class="flag" />
          <a href="/u/${score.userid}">${Utils.escapeHtml(score.user.name)}</a>
        </td>
        <td class="score">${Utils.formatScore(score.score)}</td>
        <td class="acc">${Utils.formatAcc(score.acc)}</td>
        <td class="pp">${Math.round(score.pp)}pp</td>
        <td class="mods">${mods}</td>
        <td class="grade">
          <span class="grade-badge ${gradeClass}">${score.grade}</span>
        </td>
        <td class="date">${Utils.formatDate(score.play_time)}</td>
      </tr>
    `;
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('beatmap-app');
  if (container) {
    const beatmapId = parseInt(container.dataset.beatmapId);
    const mode = parseInt(container.dataset.mode || '0');
    
    if (beatmapId) {
      window.beatmapPage = new BeatmapPage(beatmapId, mode);
    }
  }
});
