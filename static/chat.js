// chat.js
const toggleBtn = document.getElementById("chatToggle");
const chatbox = document.getElementById("chatbox");
const closeBtn = document.getElementById("closeChat");
const messageInput = document.getElementById("message");
const criteriaInput = document.getElementById("criteria");
const imageInput = document.getElementById("image");
const history = document.getElementById("history");

// Toggle chat visibility
toggleBtn.addEventListener("click", () => {
    chatbox.style.display = chatbox.style.display === "flex" ? "none" : "flex";
});

closeBtn.addEventListener("click", () => {
    chatbox.style.display = "none";
});

messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function appendMessage(role, content) {
    const div = document.createElement("div");
    div.className = `chat ${role}`;
    div.textContent = content;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    const criteria = criteriaInput.value.trim();
    const file = imageInput.files[0];

    if (!message && !file) return;

    appendMessage("user", message);
    messageInput.value = "";
    criteriaInput.value = "";
    imageInput.value = "";

    // Show typing indicator
    const typingDiv = document.createElement("div");
    typingDiv.className = "chat assistant typing";
    typingDiv.textContent = "Customer Support is typing...";
    history.appendChild(typingDiv);
    history.scrollTop = history.scrollHeight;

    const formData = new FormData();
    formData.append("message", message);
    formData.append("criteria", criteria);
    if (file) formData.append("image", file);

    try {
        const res = await fetch("/chat", {
            method: "POST",
            body: formData,
        });
        const data = await res.json();

        history.removeChild(typingDiv);

        data.messages.forEach((m) => {
            if (
                typeof m.content === "string" &&
                !m.content.startsWith("Evaluator Feedback") &&
                (m.role === "assistant" || m.role === "user")
            ) {
                appendMessage(m.role, m.content);
            }
        });
    } catch (err) {
        history.removeChild(typingDiv);
        appendMessage("assistant", "Something went wrong. Please try again.");
    }
}
