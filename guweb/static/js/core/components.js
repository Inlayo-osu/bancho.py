/**
 * Component System - Vanilla JavaScript
 * Lightweight component system for reusable UI
 */

class Component {
  constructor(element) {
    this.element = element;
    this.state = {};
    this.init();
  }

  init() {
    // Override in subclass
  }

  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.render();
  }

  render() {
    // Override in subclass
  }

  destroy() {
    // Cleanup
    this.element.innerHTML = '';
  }
}

// Card Component
class CardComponent extends Component {
  constructor(element, options = {}) {
    super(element);
    this.options = options;
  }

  init() {
    this.element.classList.add('card');
    if (this.options.className) {
      this.element.classList.add(this.options.className);
    }
  }

  setContent(html) {
    this.element.innerHTML = html;
  }
}

// Modal Component
class ModalComponent extends Component {
  constructor() {
    const element = document.createElement('div');
    element.className = 'modal';
    document.body.appendChild(element);
    super(element);
  }

  init() {
    this.element.addEventListener('click', (e) => {
      if (e.target === this.element) {
        this.close();
      }
    });
  }

  open(content) {
    this.element.innerHTML = `
      <div class="modal-content">
        <button class="modal-close">&times;</button>
        <div class="modal-body">${content}</div>
      </div>
    `;
    
    const closeBtn = this.element.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => this.close());
    
    this.element.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.element.classList.remove('active');
    document.body.style.overflow = '';
    setTimeout(() => {
      this.element.innerHTML = '';
    }, 300);
  }

  destroy() {
    this.close();
    this.element.remove();
  }
}

// Toast Notification Component
class ToastComponent {
  constructor() {
    this.container = document.createElement('div');
    this.container.className = 'toast-container';
    document.body.appendChild(this.container);
  }

  show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = this.getIcon(type);
    toast.innerHTML = `
      <i class="fas ${icon}"></i>
      <span>${Utils.escapeHtml(message)}</span>
    `;
    
    this.container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  getIcon(type) {
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
  }

  success(message, duration) {
    this.show(message, 'success', duration);
  }

  error(message, duration) {
    this.show(message, 'error', duration);
  }

  warning(message, duration) {
    this.show(message, 'warning', duration);
  }

  info(message, duration) {
    this.show(message, 'info', duration);
  }
}

// Tabs Component
class TabsComponent extends Component {
  init() {
    this.tabs = this.element.querySelectorAll('.tab-button');
    this.panels = this.element.querySelectorAll('.tab-panel');
    
    this.tabs.forEach(tab => {
      tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
    });
    
    // Activate first tab
    if (this.tabs.length > 0) {
      this.switchTab(this.tabs[0].dataset.tab);
    }
  }

  switchTab(tabId) {
    this.tabs.forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === tabId);
    });
    
    this.panels.forEach(panel => {
      panel.classList.toggle('active', panel.dataset.tab === tabId);
    });
  }
}

// Loading Spinner Component
class LoadingComponent {
  static show(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    element.appendChild(spinner);
    return spinner;
  }

  static hide(spinner) {
    if (spinner && spinner.parentNode) {
      spinner.remove();
    }
  }
}

// Export to global
window.Component = Component;
window.CardComponent = CardComponent;
window.ModalComponent = ModalComponent;
window.ToastComponent = ToastComponent;
window.TabsComponent = TabsComponent;
window.LoadingComponent = LoadingComponent;

// Global toast instance
window.toast = new ToastComponent();
