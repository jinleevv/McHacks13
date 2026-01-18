const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

// Global reference to prevent garbage collection
let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    title: "Smart Gesture Camera",
    transparent: true,
    frame: false,
    // Extra config for MacOS
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    fullscreen: true,
    alwaysOnTop: true,
    backgroundColor: "#00000000", // Fully transparent
    hasShadow: false, // Remove shadow on macOS
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // macOS specific - ensure transparency works
  if (process.platform === "darwin") {
    mainWindow.setAlwaysOnTop(true, "screen-saver");
    mainWindow.setWindowButtonVisibility(false);
    mainWindow.setBackgroundColor("#00000000");
    mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
    app.dock.hide();
  } else {
    mainWindow.setAlwaysOnTop(true, "normal");
  }

  // Load the UI file
  mainWindow.loadFile("index.html").then((r) => {});

  // remove the default menu bar (File, Edit, etc.) for a cleaner app look
  mainWindow.setMenuBarVisibility(false);

  // Default to allowing background click-through
  mainWindow.setIgnoreMouseEvents(true, { forward: true });

  // Handle mouse enter/leave events from renderer to re-enable UI clicks
  ipcMain.on("set-ignore-mouse-events", (event, ignore) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win) {
      win.setIgnoreMouseEvents(ignore, { forward: true });
      // Keep window on top even when passing clicks through
      if (ignore) {
        win.setAlwaysOnTop(true, "normal");
      }
    }
  });

  // Handle restore-on-top IPC from renderer
  ipcMain.on("restore-on-top", () => {
    if (mainWindow) {
      mainWindow.setAlwaysOnTop(true, "normal");
    }
  });

  // Handle quit-app IPC from renderer
  ipcMain.on("quit-app", () => {
    app.quit();
  });

  // Restore alwaysOnTop if window loses focus due to background clicks
  mainWindow.on("blur", () => {
    setTimeout(() => {
      if (mainWindow) {
        mainWindow.setAlwaysOnTop(true, "normal");
      }
    }, 50);
  });
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
