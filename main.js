const { app, BrowserWindow, ipcMain, globalShortcut } = require('electron');
const { join } = require('path');
const { updateElectronApp } = require('update-electron-app');

// __dirname is available in CommonJS
// Check if we're in development mode
const isDev = process.env.NODE_ENV === 'development' || process.defaultApp || /[\\|/]electron-prebuilt[\\|/]/.test(process.execPath) || /[\\|/]electron[\\|/]/.test(process.execPath);

if (!isDev) {
  updateElectronApp();
}

// Handle Squirrel startup events on Windows
if (process.platform === 'win32') {
  const squirrelCommand = process.argv[1];
  if (squirrelCommand) {
    switch (squirrelCommand) {
      case '--squirrel-install':
      case '--squirrel-updated':
      case '--squirrel-uninstall':
      case '--squirrel-obsolete':
        app.quit();
        return;
    }
  }
}

function getIconPath() {
  // Use appropriate icon format for each platform
  if (process.platform === 'win32') {
    return join(__dirname, 'assets', 'icon.ico'); // Windows prefers .ico
  } else if (process.platform === 'darwin') {
    return join(__dirname, 'assets', 'icon.icns'); // macOS uses .icns
  } else {
    return join(__dirname, 'assets', 'icon.png'); // Linux uses .png
  }
}

function createWindow () {
  const win = new BrowserWindow({
    width: 1400,
    height: 850,
    transparent: true,  // Temporarily disabled for testing
    frame: false,       // Temporarily enabled for testing
    show: false, // Don't show until ready
    icon: getIconPath(),
    vibrancy: 'ultra-dark',
    blur: 50,
    backgroundColor: 'rgba(211, 211, 211, 0.65)', 
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webviewTag: true,
      preload: join(__dirname, 'preload.js')
    }
  });

  // Show window when ready to prevent white flash
  win.once('ready-to-show', () => {
    win.show();
  });

  win.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();
  
  // Register global shortcuts
  // Cmd+L: Toggle chat panel
  globalShortcut.register('CommandOrControl+L', () => {
    const focusedWindow = BrowserWindow.getFocusedWindow();
    if (focusedWindow) {
      console.log('Global Cmd+L shortcut triggered');
      focusedWindow.webContents.send('toggle-chat-panel');
    }
  });
  
  // Cmd+K: Toggle tabbar
  globalShortcut.register('CommandOrControl+K', () => {
    const focusedWindow = BrowserWindow.getFocusedWindow();
    if (focusedWindow) {
      console.log('Global Cmd+K shortcut triggered');
      focusedWindow.webContents.send('toggle-tabbar');
    }
  });
});

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
  console.log('Show browser view:', show);
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  // Unregister all shortcuts
  globalShortcut.unregisterAll();
});
