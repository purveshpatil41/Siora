console.log("SIORA SIDEPANEL JS LOADED");

import { marked } from "marked";
import DOMPurify from "dompurify";

const sidePanelPort = chrome.runtime.connect({ name : "siora-sidepanel"});
sidePanelPort.onMessage.addListener((msg) => {
  if(msg.action == 'closeSidePanel'){
    window.close();
  }
});

let currentConversationId = null;
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const chatContainer = document.querySelector(".chat-container");

const themeToggleBtn = document.getElementById("theme-toggle-btn");
const themeIcon = themeToggleBtn.querySelector(".material-symbols-outlined");

themeToggleBtn.addEventListener("click", () => {
  const currentTheme =
    document.documentElement.getAttribute("data-theme") || "light";

  if (currentTheme === "light") {
    document.documentElement.setAttribute("data-theme", "dark");
    themeIcon.textContent = "light_mode";
  } else {
    document.documentElement.setAttribute("data-theme", "light");

    themeIcon.textContent = "dark_mode";
  }
});

userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = userInput.scrollHeight + "px";
});

sendBtn.addEventListener("click", () => {
  const message = userInput.value.trim();
  if (message.trim() === "") return;

  // Hide welcome section
  const welcomeSection = document.querySelector(".welcome-section");
  if (welcomeSection) {
    welcomeSection.style.display = "none";
  }

  // Show user's message
  const messageDiv = document.createElement("div");
  messageDiv.className = "message user-message";

  const bubbleDiv = document.createElement("div");
  bubbleDiv.className = "bubble";

  const p = document.createElement("p");
  p.textContent = message;

  bubbleDiv.appendChild(p);
  messageDiv.appendChild(bubbleDiv);
  chatContainer.appendChild(messageDiv);

  userInput.value = "";
  userInput.style.height = "auto";
  chatContainer.scrollTop = chatContainer.scrollHeight;

  // Get current page context
  chrome.runtime.sendMessage({ action: "getPageContext" }, async (response) => {
    // Graceful degradation: agar content script available nahi hai ya fail hua
    const context = (response && response.success && response.context) ? response.context : {
      url: null,
      title: "General Study Context",
      videoTimestamp: null,
      selectedText: null,
    };

    console.log("Context used:", context);

    // Send question + context to FastAPI
    try {
      const apiResponse = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_query: message,
          conversation_id: currentConversationId,
          context: {
            url: context.url,   
            title: context.title,
            videoTimestamp: context.videoTimestamp,
            selectedText: context.selectedText,
          },
        }),
      });

      if (!apiResponse.ok) {
        throw new Error(`FastAPI returned ${apiResponse.status}`);
      }

      const data = await apiResponse.json();

      console.log("AI response:", data);

      if (data.conversation_id) {
        currentConversationId = data.conversation_id;
      }

      // Show AI response
      const aiMessageDiv = document.createElement("div");
      aiMessageDiv.className = "message ai-message";

      const aiContentDiv = document.createElement("div");
      aiContentDiv.className = "ai-content";
      aiContentDiv.innerHTML = DOMPurify.sanitize(marked.parse(data.answer));

      aiMessageDiv.appendChild(aiContentDiv);
      chatContainer.appendChild(aiMessageDiv);

      chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (error) {
      console.error("Failed to get AI response:", error);
      const errDiv = document.createElement("div");
      errDiv.className = "message ai-message";
      const errContent = document.createElement("div");
      errContent.className = "ai-content";
      errContent.innerHTML = `<p style="color: #ef4444;">⚠️ <em>Could not connect to Siora backend (${error.message}). Please check if your backend server is running.</em></p>`;
      errDiv.appendChild(errContent);
      chatContainer.appendChild(errDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  });
});

userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendBtn.click();
  }
});
