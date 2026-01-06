/**
 * Home Page - Optimized Vanilla JavaScript
 */

class HomePage {
  constructor() {
    this.stats = {
      online_users: 0,
      registered_users: 0
    };
    
    this.init();
  }

  init() {
    this.container = document.getElementById('home-app');
    if (!this.container) return;
    
    this.loadStats();
    this.animateOnScroll();
  }

  async loadStats() {
    try {
      this.stats = await api.get('/v1/get_player_count');
      this.renderStats();
      this.animateStats();
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }

  renderStats() {
    const onlineEl = document.getElementById('stat-online-users');
    const registeredEl = document.getElementById('stat-registered-users');
    
    if (onlineEl) onlineEl.textContent = this.stats.counts.online;
    if (registeredEl) registeredEl.textContent = this.stats.counts.total;
  }

  animateStats() {
    const statElements = document.querySelectorAll('.stat-card-value');
    
    statElements.forEach(el => {
      const target = parseInt(el.textContent);
      const duration = 2000;
      const start = 0;
      const startTime = performance.now();
      
      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target - start) * easeOut);
        
        el.textContent = current;
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          el.textContent = target;
        }
      };
      
      requestAnimationFrame(animate);
    });
  }

  animateOnScroll() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    }, {
      threshold: 0.1
    });

    document.querySelectorAll('.animate-fadeIn').forEach(el => {
      observer.observe(el);
    });
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('home-app')) {
    window.homePage = new HomePage();
  }
});
