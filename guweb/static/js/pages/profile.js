/**
 * Profile Page - Optimized Vanilla JavaScript
 */

class ProfilePage {
  constructor(userId, mode = 0) {
    this.userId = userId;
    this.currentMode = mode;
    this.currentMods = 0;
    this.data = null;
    this.loading = false;
    
    this.init();
  }

  init() {
    this.container = document.getElementById('profile-app');
    if (!this.container) return;
    
    this.setupModeSelector();
    this.loadProfile();
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

  async loadProfile() {
    this.setLoading(true);
    
    try {
      this.data = await api.get('/v1/get_profile_data', {
        id: this.userId,
        mode: this.currentMode,
        mods: this.currentMods
      });
      
      this.render();
    } catch (error) {
      console.error('Failed to load profile:', error);
      toast.error('Failed to load profile data');
    } finally {
      this.setLoading(false);
    }
  }

  async changeMode(mode) {
    this.currentMode = mode;
    
    // Update active button
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.toggle('active', parseInt(btn.dataset.mode) === mode);
    });
    
    await this.loadProfile();
  }

  render() {
    if (!this.data) return;
    
    this.renderStats();
    this.renderScores();
  }

  renderStats() {
    const stats = this.data.stats[this.currentMode];
    if (!stats) return;
    
    const elements = {
      rank: document.getElementById('stat-rank'),
      countryRank: document.getElementById('stat-country-rank'),
      pp: document.getElementById('stat-pp'),
      acc: document.getElementById('stat-acc'),
      plays: document.getElementById('stat-plays'),
      playtime: document.getElementById('stat-playtime')
    };
    
    if (elements.rank) elements.rank.textContent = `#${Utils.formatNumber(stats.rank)}`;
    if (elements.countryRank) elements.countryRank.textContent = `#${Utils.formatNumber(stats.country_rank)}`;
    if (elements.pp) elements.pp.textContent = Utils.formatPP(stats.pp);
    if (elements.acc) elements.acc.textContent = Utils.formatAcc(stats.acc);
    if (elements.plays) elements.plays.textContent = Utils.formatNumber(stats.plays);
    if (elements.playtime) elements.playtime.textContent = Utils.formatPlaytime(stats.playtime);
  }

  renderScores() {
    this.renderScoreList('best-scores', this.data.best_scores || []);
    this.renderScoreList('recent-scores', this.data.recent_scores || []);
  }

  renderScoreList(containerId, scores) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (scores.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No scores yet</p>
        </div>
      `;
      return;
    }
    
    container.innerHTML = scores.map(score => this.createScoreCard(score)).join('');
  }

  createScoreCard(score) {
    const mods = Utils.getModsString(score.mods);
    const gradeClass = Utils.getGradeClass(score.grade);
    
    return `
      <div class="score-card">
        <div class="score-beatmap">
          <div class="beatmap-cover">
            <img src="https://assets.ppy.sh/beatmaps/${score.beatmap.set_id}/covers/card.jpg" 
                 alt="${Utils.escapeHtml(score.beatmap.title)}" 
                 loading="lazy">
          </div>
          <div class="beatmap-info">
            <a href="/scores/${score.id}" class="beatmap-title">
              ${Utils.escapeHtml(score.beatmap.title)} [${Utils.escapeHtml(score.beatmap.version)}]
            </a>
            <div class="beatmap-artist">${Utils.escapeHtml(score.beatmap.artist)}</div>
            <div class="score-time">${Utils.formatTime(score.play_time)}</div>
          </div>
        </div>
        
        <div class="score-details">
          ${mods !== 'NM' ? `<div class="score-mods"><span class="mod-badge">+${mods}</span></div>` : ''}
          <div class="score-pp">${Math.round(score.pp)}pp</div>
          <div class="score-acc">${Utils.formatAcc(score.acc)}</div>
        </div>
        
        <div class="score-grade">
          <span class="grade-badge ${gradeClass}">${score.grade}</span>
        </div>
        
        <div class="score-stats">
          <span class="stat-hit good">${score.n300} ⬤</span>
          <span class="stat-hit ok">${score.n100} ⬤</span>
          <span class="stat-hit miss">${score.nmiss} ⬤</span>
          <span class="combo">${score.max_combo}x</span>
        </div>
      </div>
    `;
  }

  setLoading(loading) {
    this.loading = loading;
    Utils.setLoading(this.container, loading);
  }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('profile-app');
  if (container) {
    const userId = parseInt(container.dataset.userId);
    const mode = parseInt(container.dataset.mode || '0');
    
    if (userId) {
      window.profilePage = new ProfilePage(userId, mode);
    }
  }
});
