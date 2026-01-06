/**
 * Utility Functions - Formatting
 * Number, date, and data formatting utilities
 */

const Utils = {
  // Number formatting
  formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  },

  formatPP(pp) {
    return Math.round(pp).toLocaleString() + 'pp';
  },

  formatScore(score) {
    return score.toLocaleString();
  },

  formatAcc(acc) {
    return acc.toFixed(2) + '%';
  },

  // Time formatting
  formatPlaytime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  },

  formatLength(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  },

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  },

  formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  // Mods utilities
  getModsString(modsValue) {
    if (modsValue === 0) return 'NM';
    
    const MOD_MAP = {
      1: 'NF', 2: 'EZ', 4: 'TD', 8: 'HD',
      16: 'HR', 32: 'SD', 64: 'DT', 128: 'RX',
      256: 'HT', 512: 'NC', 1024: 'FL', 2048: 'AT',
      4096: 'SO', 8192: 'AP', 16384: 'PF', 536870912: 'V2'
    };
    
    let mods = [];
    for (const [value, name] of Object.entries(MOD_MAP)) {
      if (modsValue & parseInt(value)) {
        mods.push(name);
      }
    }
    
    let result = mods.join('');
    
    // Handle special cases
    if (result.includes('NC') && result.includes('DT')) {
      result = result.replace('DT', '');
    }
    if (result.includes('PF') && result.includes('SD')) {
      result = result.replace('SD', '');
    }
    
    return result || 'NM';
  },

  // Grade utilities
  getGradeColor(grade) {
    const colors = {
      'XH': '#d4d4d4', 'X': '#ffdd55',
      'SH': '#d4d4d4', 'S': '#ffdd55',
      'A': '#88da20', 'B': '#4a9beb',
      'C': '#d08cf7', 'D': '#ff6666', 'F': '#666666'
    };
    return colors[grade.toUpperCase().replace('SS', 'X')] || '#ffffff';
  },

  getGradeClass(grade) {
    return `rank-${grade.toLowerCase().replace('ss', 'x')}`;
  },

  // Mode utilities
  getModeInfo(mode) {
    const modes = {
      0: { name: 'osu!', icon: 'fa-circle', color: '#ff66aa' },
      1: { name: 'osu!taiko', icon: 'fa-drum', color: '#ff8c1a' },
      2: { name: 'osu!catch', icon: 'fa-apple-alt', color: '#66cc66' },
      3: { name: 'osu!mania', icon: 'fa-th', color: '#a366ff' }
    };
    return modes[mode] || modes[0];
  },

  // DOM utilities
  createElement(tag, className, content) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (content) el.textContent = content;
    return el;
  },

  setLoading(element, isLoading) {
    if (isLoading) {
      element.classList.add('load');
    } else {
      element.classList.remove('load');
    }
  },

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  },

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
};

// Export to global scope
window.Utils = Utils;
