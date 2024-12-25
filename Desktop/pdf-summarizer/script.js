function openChatbot() {
    const chatbot = document.getElementById("chatbot");
    chatbot.style.display = "flex";
  }
  
  function closeChatbot() {
    const chatbot = document.getElementById("chatbot");
    chatbot.style.display = "none";
  }
  
  function sendMessage() {
    const input = document.getElementById("chatbot-input");
    const body = document.getElementById("chatbot-body");
  
    if (input.value.trim() !== "") {
      // Append user's message
      const userMessage = document.createElement("div");
      userMessage.className = "message user-message";
      userMessage.textContent = input.value;
      body.appendChild(userMessage);
  
      // Simulate a bot response
      setTimeout(() => {
        const botMessage = document.createElement("div");
        botMessage.className = "message bot-message";
        botMessage.textContent = "Thank you for your message! I’ll get back to you shortly.";
        body.appendChild(botMessage);
        body.scrollTop = body.scrollHeight;
      }, 1000);
  
      input.value = "";
      body.scrollTop = body.scrollHeight;
    }
  }
  