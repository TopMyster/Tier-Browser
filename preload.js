import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  navigateTo: (url) => ipcRenderer.invoke('navigate-to', url),
  goBack: () => ipcRenderer.invoke('go-back'),
  goForward: () => ipcRenderer.invoke('go-forward'),
  showBrowserView: (show) => ipcRenderer.invoke('show-browserview', show),
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
  }
});
