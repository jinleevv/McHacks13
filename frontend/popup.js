const btn = document.getElementById("toggle");
const status = document.getElementById("status");

let active = false;

btn.onclick = async () => {
  active = !active;

  const [tab] = await chrome.tabs.query({
    active: true,
    currentWindow: true,
  });

  chrome.tabs.sendMessage(tab.id, {
    action: active ? "START_CAMERA" : "STOP_CAMERA",
  });

  btn.textContent = active ? "Stop Camera" : "Start Camera";
  status.textContent = active ? "Status: Running" : "Status: Idle";
};
