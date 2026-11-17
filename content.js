// Content Script - Runs inside the webpage
// This script can access the DOM and collect page information
console.log('Siora content script loaded on:', window.location.href);
console.log("🔥 SIORA CONTENT.JS IS RUNNING");

function collectPageContext() {
    const video = document.querySelector('video');
    const context = {
        url: window.location.href,
        title: document.title,
        selectedText: window.getSelection().toString().trim(),
        videoTimestamp: video ? video.currentTime : null,
        collectionTimestamp: new Date().toISOString(),
    };

    return context;
}

// Listen for messages from sidepanel (via background.js)

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Content script received:", request);
    if (request.action === 'getPageContext') {
        const context = collectPageContext();

        sendResponse(
            {
                success: true,
                context: context
            }
        );
    }
    return true;
});