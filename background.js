// Global default
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: false })
    .catch(() => {});
  chrome.sidePanel.setOptions({ enabled: false }).catch(() => {});
});

// Tab ID and its Port record: Map<tabId, port>
const openSidepanels = new Map();

// Extension icon click handle karna (Toggle Open / Close)
chrome.action.onClicked.addListener((tab) => {
  if (!tab.id) return;

  const existingPort = openSidepanels.get(tab.id);
  if (existingPort) {
    // TOGGLE CLOSE: Agar already open hai, toh close message bhejo
    existingPort.postMessage({ action: "closeSidePanel" });
    openSidepanels.delete(tab.id);
    return;
  }

  // TOGGLE OPEN:
  // IMPORTANT: Do NOT await setOptions here! Awaiting breaks Chrome's user-gesture token chain.
  chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true,
  });

  // Call open immediately in the same synchronous user gesture turn
  chrome.sidePanel.open({ tabId: tab.id });
});

// Listen for sidepanel connection to track open tabs
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === "siora-sidepanel") {
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
      if (!tabs || tabs.length === 0 || !tabs[0].id) return;
      const tabId = tabs[0].id;

      openSidepanels.set(tabId, port);

      port.onDisconnect.addListener(() => {
        openSidepanels.delete(tabId);
      });
    });
  }
});

// Relay message from sidepanel to content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Background received : ", request);

  if (request.action === "getPageContext") {
    chrome.tabs.query({ active: true, lastFocusedWindow: true }, (tabs) => {
      if (!tabs || tabs.length === 0 || !tabs[0].id) {
        console.error("No active tab found");
        sendResponse({ success: false, error: "No active tab found" });
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, request, (response) => {
        if (chrome.runtime.lastError) {
          console.error(
            "Error talking to content script:",
            chrome.runtime.lastError.message,
          );
          sendResponse({
            success: false,
            error: chrome.runtime.lastError.message,
          });
          return;
        }

        console.log("Response from content script:", response);
        sendResponse(response);
      });
    });
    return true;
  }
});
