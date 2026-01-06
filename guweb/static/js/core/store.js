/**
 * State Management - Simple reactive state
 */

class Store {
  constructor(initialState = {}) {
    this._state = initialState;
    this._listeners = new Map();
  }

  get state() {
    return this._state;
  }

  setState(updates) {
    const oldState = { ...this._state };
    this._state = { ...this._state, ...updates };
    this._notify(oldState, this._state);
  }

  subscribe(key, callback) {
    if (!this._listeners.has(key)) {
      this._listeners.set(key, []);
    }
    this._listeners.get(key).push(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this._listeners.get(key);
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    };
  }

  _notify(oldState, newState) {
    for (const [key, callbacks] of this._listeners) {
      if (oldState[key] !== newState[key]) {
        callbacks.forEach(callback => callback(newState[key], oldState[key]));
      }
    }
  }
}

// Session Store
const sessionStore = new Store({
  authenticated: false,
  user: null
});

// Load session from global window object
if (typeof window.session !== 'undefined') {
  sessionStore.setState({
    authenticated: window.session.authenticated,
    user: window.session.user_data
  });
}

// Export
window.Store = Store;
window.sessionStore = sessionStore;
