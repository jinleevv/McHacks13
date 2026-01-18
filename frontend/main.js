const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

// Global reference to prevent garbage collection
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    title: "Jarvis",
    width: 1200,
    height: 800,
    // transparent: false,
    frame: true,
    // hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    // alwaysOnTop: false,
    backgroundColor: "#1a1a1a",
  });

  // Load the UI file
  mainWindow.loadFile("index.html").then((r) => {});

  // remove the default menu bar (File, Edit, etc.) for a cleaner app look
  mainWindow.setMenuBarVisibility(false);

  // Handle quit-app IPC from renderer
  ipcMain.on("quit-app", () => {
    app.quit();
  });

  // Restore alwaysOnTop if window loses focus due to background clicks
  // mainWindow.on("blur", () => {
  //   setTimeout(() => {
  //     if (mainWindow) {
  //       mainWindow.setAlwaysOnTop(true, "normal");
  //     }
  //   }, 50);
  // });
}

// App Lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
