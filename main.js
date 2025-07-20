// main.js
import { app, BrowserWindow, ipcMain } from 'electron';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import electronSquirrelStartup from 'electron-squirrel-startup';
import electronIsDev from 'electron-is-dev';
import 'update-electron-app'; // Automatically update Electron app
import { updateElectronApp } from 'update-electron-app';

// ES6 equivalent of __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

if (!electronIsDev) {
  updateElectronApp();
}

// Enable live reload for Electron during development
if (electronSquirrelStartup) app.quit();

function getIconPath() {
  // Use icon.icns for all platforms
  return join(__dirname, 'assets', 'icon.icns');
}

function createWindow () {
  const win = new BrowserWindow({
    width: 1400,
    height: 850,
    transparent: true,  // Temporarily disabled for testing
    frame: false,       // Temporarily enabled for testing
    show: false, // Don't show until ready
    icon: getIconPath(), // <-- Set the icon here
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

  win.loadFile('Index.html');
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development' || electronIsDev) {
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
