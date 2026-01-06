/**
 * Leaderboard Page - Optimized Vanilla JavaScript
 */

class LeaderboardPage {
  constructor() {
    this.currentMode = 0;
    this.currentMods = 0;
    this.currentCountry = '';
    this.currentPage = 0;
    this.limit = 50;
    this.data = [];
    this.loading = false;
    
    this.init();
  }

  init() {
    this.container = document.getElementById('leaderboard-app');
    if (!this.container) return;
    
    this.setupControls();
    this.loadLeaderboard();
  }

  setupControls() {
    // Mode selector
    const modeButtons = document.querySelectorAll('.mode-btn');
    modeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        this.changeMode(parseInt(btn.dataset.mode));
      });
    });
    
    // Country filter
    const countrySelect = document.getElementById('country-select');
    if (countrySelect) {
      countrySelect.addEventListener('change', (e) => {
        this.currentCountry = e.target.value;
        this.currentPage = 0;
        this.loadLeaderboard();
      });
    }
    
    // Pagination
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    if (prevBtn) {
      prevBtn.addEventListener('click', () => this.previousPage());
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.nextPage());
    }
  }

  async loadLeaderboard() {
    if (this.loading) return;
    
    this.loading = true;
    Utils.setLoading(this.container, true);
    
    try {
      this.data = await api.get('/v1/get_leaderboard', {
        mode: this.currentMode,
        mods: this.currentMods,
        country: this.currentCountry,
        page: this.currentPage,
        limit: this.limit
      });
      
      this.render();
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
      toast.error('Failed to load leaderboard');
    } finally {
      this.loading = false;
      Utils.setLoading(this.container, false);
    }
  }

  changeMode(mode) {
    this.currentMode = mode;
    this.currentPage = 0;
    
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.toggle('active', parseInt(btn.dataset.mode) === mode);
    });
    
    this.loadLeaderboard();
  }

  previousPage() {
    if (this.currentPage > 0) {
      this.currentPage--;
      this.loadLeaderboard();
    }
  }

  nextPage() {
    if (this.data.length === this.limit) {
      this.currentPage++;
      this.loadLeaderboard();
    }
  }

  render() {
    const container = document.getElementById('leaderboard-list');
    if (!container) return;
    
    if (this.data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-trophy"></i>
          <p>No players found</p>
        </div>
      `;
      return;
    }
    
    container.innerHTML = this.data.map((player, i) => 
      this.createPlayerCard(player, this.currentPage * this.limit + i + 1)
    ).join('');
    
    this.updatePagination();
  }

  createPlayerCard(player, rank) {
    const stats = player.stats;
    
    return `
      <div class="leaderboard-row">
        <div class="leaderboard-rank">#${rank}</div>
        <div class="leaderboard-player">
          <img src="/static/images/flags/${player.country}.png" class="flag" />
          <div class="player-avatar">
            <img src="https://a.${window.location.hostname}/${player.id}" alt="${player.name}" loading="lazy">
          </div>
          <a href="/u/${player.id}" class="player-name">${Utils.escapeHtml(player.name)}</a>
        </div>
        <div class="leaderboard-stats">
          <div class="stat-item">
            <span class="stat-label">PP</span>
            <span class="stat-value">${Utils.formatPP(stats.pp)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Accuracy</span>
            <span class="stat-value">${Utils.formatAcc(stats.acc)}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Plays</span>
            <span class="stat-value">${Utils.formatNumber(stats.plays)}</span>
          </div>
        </div>
      </div>
    `;
  }

  updatePagination() {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    
    if (prevBtn) {
      prevBtn.disabled = this.currentPage === 0;
    }
    
    if (nextBtn) {
      nextBtn.disabled = this.data.length < this.limit;
    }
    
    if (pageInfo) {
      pageInfo.textContent = `Page ${this.currentPage + 1}`;
    }
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('leaderboard-app')) {
    window.leaderboardPage = new LeaderboardPage();
  }
});
