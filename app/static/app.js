const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const messages = document.querySelector("#messages");
const statusEl = document.querySelector("#status");

let sessionId = localStorage.getItem("faqBotSessionId");

function addMessage(text, kind) {
  const node = document.createElement("article");
  node.className = `message ${kind}`;
  const p = document.createElement("p");
  p.textContent = text;
  node.appendChild(p);
  messages.appendChild(node);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  input.disabled = true;
  form.querySelector("button").disabled = true;
  statusEl.textContent = "Thinking";
  addMessage(message, "user");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        student_identity: "web-demo"
      })
    });
    const data = await response.json();
    sessionId = data.session_id;
    localStorage.setItem("faqBotSessionId", sessionId);
    addMessage(data.answer, "bot");
    statusEl.textContent = "Ready";
  } catch (error) {
    addMessage("The bot could not process that request right now.", "bot", true);
    statusEl.textContent = "Error";
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
});
