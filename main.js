const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { updateElectronApp } = require('update-electron-app')

if (!isDev && require('electron-squirrel-startup')) {
  updateElectronApp({
    updateSource: {
      type: UpdateSourceType.ElectronPublicUpdateService,
      repo: 'TopMyster/IsleBrowser'
    },
    updateInterval: '1 hour',
  });
}


if (require('electron-squirrel-startup')) app.quit();

function createWindow () {
  const win = new BrowserWindow({
    width: 1400,
    height: 850,
    transparent: true,
    frame: false,
    show: false, // Don't show until ready
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webviewTag: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Show window when ready to prevent white flash
  win.once('ready-to-show', () => {
    win.show();
  });

  win.loadFile('Index.html');
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    win.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

// IPC handlers for browser functionality
ipcMain.handle('navigate-to', async (event, url) => {
  // Handle navigation logic here
  console.log('Navigate to:', url);
});

ipcMain.handle('go-back', async (event) => {
  // Handle back navigation
  console.log('Go back');
});

ipcMain.handle('go-forward', async (event) => {
  // Handle forward navigation
  console.log('Go forward');
});

ipcMain.handle('show-browserview', async (event, show) => {
  // Handle browser view visibility
  console.log('Show browser view:', show);
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
