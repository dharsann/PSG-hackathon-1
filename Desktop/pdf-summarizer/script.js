document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file-input");
  if (fileInput) {
    fileInput.value = "";
  }
});

function openChatbot() {
  const chatbot = document.getElementById("chatbot");
  chatbot.style.display = "flex";
}

function closeChatbot() {
  const chatbot = document.getElementById("chatbot");
  chatbot.style.display = "none";
}

async function sendMessage() {
  const input = document.getElementById("chatbot-input");
  const body = document.getElementById("chatbot-body");

  if (input.value.trim() === "") {
    alert("Please type a message before sending.");
    return;
  }

  const userMessage = document.createElement("div");
  userMessage.className = "message user-message";
  userMessage.textContent = input.value;
  body.appendChild(userMessage);

  const userQuery = input.value;
  input.value = "";
  body.scrollTop = body.scrollHeight;

  try {
    const loadingMessage = document.createElement("div");
    loadingMessage.className = "message bot-message";
    loadingMessage.textContent = "Thinking...";
    body.appendChild(loadingMessage);

    const formData = new FormData();
    formData.append("message", userQuery);

    const response = await fetch("http://127.0.0.1:8000/chat/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    const botReply = data.reply;

    body.removeChild(loadingMessage);

    const botMessage = document.createElement("div");
    botMessage.className = "message bot-message";
    botMessage.textContent = botReply;
    body.appendChild(botMessage);
    body.scrollTop = body.scrollHeight;
  } catch (error) {
    const errorMessage = document.createElement("div");
    errorMessage.className = "message bot-message";
    errorMessage.textContent = "Sorry, there was an error processing your request.";
    body.appendChild(errorMessage);
    body.scrollTop = body.scrollHeight;
    console.error("Error:", error);
  }
}

async function uploadFile() {
  const fileInput = document.querySelector('input[type="file"]');
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select a file to upload.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://127.0.0.1:8000/upload/", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    alert("File uploaded successfully. You can now start chatting.");

    const chatbotButton = document.querySelector("button[onclick='openChatbot()']");
    chatbotButton.disabled = false;
    console.log("Uploaded Document Content:", data.content);
  } catch (error) {
    alert("File upload failed. Please try again.");
    console.error("Error:", error);
  }
}
