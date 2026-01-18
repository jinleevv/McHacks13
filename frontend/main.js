const { app, BrowserWindow } = require('electron');
const path = require('path');

// Global reference to prevent garbage collection
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    title: "Smart Gesture Camera",
    backgroundColor: '#1e1e1e', // Dark mode background
    webPreferences: {
      nodeIntegration: false, // Security best practice
      contextIsolation: true, // Security best practice
    }
  });

  // Load the UI file
  mainWindow.loadFile('index.html').then(r => {});

  // remove the default menu bar (File, Edit, etc.) for a cleaner app look
  mainWindow.setMenuBarVisibility(false);
}

// App Lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});