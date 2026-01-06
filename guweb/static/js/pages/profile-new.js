/**
 * Profile Page Vanilla JavaScript
 * Replaces Vue with pure JavaScript for profile rendering
 */

class ProfilePage {
    constructor() {
        this.userId = document.getElementById('profile-container').dataset.userId;
        this.currentMode = 0;
        this.data = {
            profile: null,
            scores: {
                recent: { out: [], load: false, more: { full: false, total: 0 } },
                best: { out: [], load: false, more: { full: false, total: 0 } }
            },
            maps: {
                mostplay: { out: [], load: false, more: { full: false, total: 0 } }
            }
        };
        this.init();
    }

    async init() {
        await this.loadProfile();
        this.attachEventListeners();
    }

    async loadProfile() {
        try {
            const response = await fetch(`/api/v1/get_profile?id=${this.userId}&mode=${this.currentMode}`);
            const data = await response.json();
            this.data.profile = data;
            this.renderProfile();
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    }

    async loadScores(type = 'best') {
        this.data.scores[type].load = true;
        try {
            const response = await fetch(`/api/v1/get_scores?id=${this.userId}&type=${type}&mode=${this.currentMode}`);
            const data = await response.json();
            this.data.scores[type].out = data.scores || [];
            this.data.scores[type].more.total = data.total || 0;
            this.renderScores(type);
        } catch (error) {
            console.error(`Failed to load ${type} scores:`, error);
        } finally {
            this.data.scores[type].load = false;
        }
    }

    renderProfile() {
        const profile = this.data.profile;
        if (!profile) return;

        // Render stats
        const statsContainer = document.getElementById('profile-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="osu-stats-grid">
                    <div class="osu-stat-card stagger-item">
                        <div class="osu-stat-label">Global Rank</div>
                        <div class="osu-stat-value stat-rank">
                            #${this.formatNumber(profile.rank || 0)}
                        </div>
                    </div>
                    <div class="osu-stat-card stagger-item">
                        <div class="osu-stat-label">Performance</div>
                        <div class="osu-stat-value stat-pp">
                            ${this.formatNumber(profile.pp || 0)}<span class="osu-stat-unit">pp</span>
                        </div>
                    </div>
                    <div class="osu-stat-card stagger-item">
                        <div class="osu-stat-label">Accuracy</div>
                        <div class="osu-stat-value stat-acc">
                            ${(profile.acc || 0).toFixed(2)}<span class="osu-stat-unit">%</span>
                        </div>
                    </div>
                    <div class="osu-stat-card stagger-item">
                        <div class="osu-stat-label">Play Count</div>
                        <div class="osu-stat-value stat-plays">
                            ${this.formatNumber(profile.plays || 0)}
                        </div>
                    </div>
                    <div class="osu-stat-card stagger-item">
                        <div class="osu-stat-label">Play Time</div>
                        <div class="osu-stat-value stat-playtime">
                            ${this.formatPlaytime(profile.playtime || 0)}
                        </div>
                    </div>
                    <div class="osu-stat-card stagger-item">
                        <div class="osu-stat-label">Total Score</div>
                        <div class="osu-stat-value">
                            ${this.formatNumber(profile.tscore || 0)}
                        </div>
                    </div>
                </div>
            `;
        }
    }

    renderScores(type = 'best') {
        const container = document.getElementById(`scores-${type}`);
        if (!container) return;

        const scores = this.data.scores[type].out;
        
        if (scores.length === 0) {
            container.innerHTML = `
                <div class="osu-card">
                    <div style="text-align: center; padding: 2rem;">
                        <h2 style="font-size: 3rem; margin-bottom: 1rem;">:(</h2>
                        <h3>No scores available</h3>
                        <p style="color: #999;">Try playing something?</p>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = scores.map((score, index) => this.createScoreCard(score, index)).join('');
    }

    createScoreCard(score, index) {
        const map = score.beatmap || score;
        const mods = this.getModsString(score.mods || 0);
        const grade = (score.grade || 'F').replace('X', 'SS').replace('H', '');
        const isFC = score.max_combo === map.max_combo;
        
        return `
            <div class="osu-score-card stagger-item" style="animation-delay: ${index * 0.05}s">
                <div class="osu-score-container">
                    <div class="osu-beatmap-bg" style="background-image: url(https://assets.ppy.sh/beatmaps/${map.set_id}/covers/cover.jpg)"></div>
                    <div class="osu-score-content">
                        <div class="osu-beatmap-cover">
                            <img src="https://assets.ppy.sh/beatmaps/${map.set_id}/covers/card.jpg" alt="">
                        </div>
                        <div class="osu-beatmap-info">
                            <div class="osu-beatmap-title">
                                <a href="/scores/${score.id}" style="color: #fff; text-decoration: none;">
                                    ${this.escapeHtml(map.artist)} - ${this.escapeHtml(map.title)}
                                </a>
                            </div>
                            <div class="osu-beatmap-artist">
                                [${this.escapeHtml(map.version)}]
                            </div>
                            <div class="osu-play-stats">
                                <span>${this.formatNumber(score.n100 || 0)} <span class="stat-hit-good">⬤</span></span>
                                <span>${this.formatNumber(score.n50 || 0)} <span class="stat-hit-ok">⬤</span></span>
                                <span>${this.formatNumber(score.nmiss || 0)} <span class="stat-hit-miss">⬤</span></span>
                                <span>${this.formatNumber(score.max_combo || 0)}/${this.formatNumber(map.max_combo || 0)}x ${isFC ? '<span class="combo-fc">FC</span>' : ''}</span>
                            </div>
                        </div>
                        <div class="osu-score-details">
                            <div class="osu-grade grade-${grade.toLowerCase()}">
                                ${grade}
                            </div>
                            <div class="osu-pp-display">
                                ${Math.round(score.pp || 0)}<span>pp</span>
                            </div>
                            <div class="osu-acc-display">
                                ${(score.acc || 0).toFixed(2)}%
                            </div>
                            ${mods ? `<div class="osu-score-mods">${mods.split('').map((m, i) => i % 2 === 0 ? `<span class="mod-badge">${mods.substr(i, 2)}</span>` : '').filter(Boolean).join('')}</div>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getModsString(mods) {
        const modNames = [];
        if (mods & (1 << 0)) modNames.push('NF');
        if (mods & (1 << 1)) modNames.push('EZ');
        if (mods & (1 << 3)) modNames.push('HD');
        if (mods & (1 << 4)) modNames.push('HR');
        if (mods & (1 << 5)) modNames.push('SD');
        if (mods & (1 << 6)) modNames.push('DT');
        if (mods & (1 << 9)) modNames.push('NC');
        if (mods & (1 << 7)) modNames.push('RX');
        if (mods & (1 << 10)) modNames.push('HT');
        if (mods & (1 << 12)) modNames.push('FL');
        if (mods & (1 << 13)) modNames.push('AP');
        if (mods & (1 << 14)) modNames.push('SO');
        return modNames.join('');
    }

    changeMode(mode) {
        this.currentMode = mode;
        this.loadProfile();
        this.loadScores('best');
        this.loadScores('recent');
        
        // Update button states
        document.querySelectorAll('.osu-mode-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.mode) === mode);
        });
    }

    attachEventListeners() {
        // Mode selector
        document.querySelectorAll('.osu-mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = parseInt(btn.dataset.mode);
                this.changeMode(mode);
            });
        });
    }

    formatNumber(num) {
        return num.toLocaleString();
    }

    formatPlaytime(seconds) {
        const hours = Math.floor(seconds / 3600);
        return `${hours}h`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('profile-container')) {
        window.profilePage = new ProfilePage();
        // Load initial scores
        profilePage.loadScores('best');
        profilePage.loadScores('recent');
    }
});
