const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  navigateTo: (url) => ipcRenderer.invoke('navigate-to', url),
  goBack: () => ipcRenderer.invoke('go-back'),
  goForward: () => ipcRenderer.invoke('go-forward'),
  showBrowserView: (show) => ipcRenderer.invoke('show-browserview', show),
  // Context menu functions
  openContextMenu: (x, y, options) => ipcRenderer.invoke('show-context-menu', x, y, options),
  // Engine selection communication
  setEngine: (engineName) => {
    localStorage.setItem('selectedEngine', engineName);
    // Communicate with parent window
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'ENGINE_CHANGED', engine: engineName }, '*');
    }
  },
  getEngine: () => {
    return localStorage.getItem('selectedEngine') || 'Bing';
  },
  // Session persistence
  saveBrowserState: (state) => ipcRenderer.invoke('save-browser-state', state),
  loadBrowserState: () => ipcRenderer.invoke('load-browser-state'),
  // Webview reload
  reloadWebview: () => ipcRenderer.send('reload-webview')
});
