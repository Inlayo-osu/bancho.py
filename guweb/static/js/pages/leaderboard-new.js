/**
 * Leaderboard Page - Shiina Style
 */

class LeaderboardPage {
    constructor() {
        this.currentMode = 0;
        this.currentPage = 1;
        this.pageSize = 50;
        this.country = '';
        this.data = [];
        this.total = 0;
        this.init();
    }

    async init() {
        await this.loadLeaderboard();
        this.attachEventListeners();
    }

    async loadLeaderboard() {
        const container = document.getElementById('leaderboard-container');
        container.innerHTML = '<div class="loading-spinner" style="text-align: center; padding: 2rem;">Loading...</div>';

        try {
            const offset = (this.currentPage - 1) * this.pageSize;
            const url = `/api/v1/get_leaderboard?mode=${this.currentMode}&offset=${offset}&limit=${this.pageSize}${this.country ? `&country=${this.country}` : ''}`;
            const response = await fetch(url);
            const result = await response.json();
            
            this.data = result.players || [];
            this.total = result.total || 0;
            this.renderLeaderboard();
        } catch (error) {
            console.error('Failed to load leaderboard:', error);
            container.innerHTML = '<div class="osu-card"><p style="text-align: center; padding: 2rem;">Failed to load leaderboard</p></div>';
        }
    }

    renderLeaderboard() {
        const container = document.getElementById('leaderboard-container');
        
        if (this.data.length === 0) {
            container.innerHTML = '<div class="osu-card"><p style="text-align: center; padding: 2rem;">No players found</p></div>';
            return;
        }

        container.innerHTML = this.data.map((player, index) => {
            const globalRank = (this.currentPage - 1) * this.pageSize + index + 1;
            return this.createPlayerCard(player, globalRank);
        }).join('');

        this.renderPagination();
    }

    createPlayerCard(player, rank) {
        const rankClass = rank === 1 ? 'top1' : rank === 2 ? 'top2' : rank === 3 ? 'top3' : '';
        
        return `
            <div class="osu-lb-row fade-in">
                <div class="osu-lb-rank ${rankClass}">
                    #${rank}
                </div>
                <div class="osu-lb-player">
                    <img src="https://a.${window.location.hostname.replace('osu.', '')}/${player.id}" 
                         alt="${this.escapeHtml(player.name)}" 
                         class="osu-lb-avatar">
                    <img src="/static/images/flags/${player.country.toUpperCase()}.png" 
                         alt="${player.country}" 
                         class="osu-lb-flag">
                    <a href="/u/${player.id}" class="osu-lb-name" style="text-decoration: none;">
                        ${this.escapeHtml(player.name)}
                    </a>
                </div>
                <div class="osu-lb-stats">
                    <div class="osu-lb-stat">
                        <div class="osu-lb-stat-value stat-pp">${this.formatNumber(player.pp || 0)}</div>
                        <div class="osu-lb-stat-label">Performance</div>
                    </div>
                    <div class="osu-lb-stat">
                        <div class="osu-lb-stat-value stat-acc">${(player.acc || 0).toFixed(2)}%</div>
                        <div class="osu-lb-stat-label">Accuracy</div>
                    </div>
                    <div class="osu-lb-stat">
                        <div class="osu-lb-stat-value">${this.formatNumber(player.plays || 0)}</div>
                        <div class="osu-lb-stat-label">Plays</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPagination() {
        const paginationContainer = document.getElementById('pagination-container');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(this.total / this.pageSize);
        const maxButtons = 7;
        const buttons = [];

        buttons.push(`
            <button class="pagination-btn ${this.currentPage === 1 ? 'disabled' : ''}" 
                    onclick="leaderboardPage.goToPage(${this.currentPage - 1})" 
                    ${this.currentPage === 1 ? 'disabled' : ''}>
                <i class="fa-solid fa-chevron-left"></i>
            </button>
        `);

        let startPage = Math.max(1, this.currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);

        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            buttons.push(`
                <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" 
                        onclick="leaderboardPage.goToPage(${i})">
                    ${i}
                </button>
            `);
        }

        buttons.push(`
            <button class="pagination-btn ${this.currentPage === totalPages ? 'disabled' : ''}" 
                    onclick="leaderboardPage.goToPage(${this.currentPage + 1})" 
                    ${this.currentPage === totalPages ? 'disabled' : ''}>
                <i class="fa-solid fa-chevron-right"></i>
            </button>
        `);

        paginationContainer.innerHTML = `
            <div class="pagination-controls" style="display: flex; justify-content: center; gap: 8px; margin-top: 2rem;">
                ${buttons.join('')}
            </div>
            <p style="text-align: center; margin-top: 1rem; color: #999;">
                Page ${this.currentPage} of ${totalPages} (${this.formatNumber(this.total)} players)
            </p>
        `;
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.total / this.pageSize);
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.loadLeaderboard();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    changeMode(mode) {
        this.currentMode = mode;
        this.currentPage = 1;
        this.loadLeaderboard();

        document.querySelectorAll('.osu-mode-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.mode) === mode);
        });
    }

    attachEventListeners() {
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('leaderboard-container')) {
        window.leaderboardPage = new LeaderboardPage();
    }
});
