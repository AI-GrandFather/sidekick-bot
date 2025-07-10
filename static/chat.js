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

function appendMessage(role, content) {
    const div = document.createElement("div");
    div.innerHTML = `<strong>${role}:</strong> ${content}`;
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
}

async function sendMessage() {
    const message = messageInput.value.trim();
    const criteria = criteriaInput.value.trim();
    const file = imageInput.files[0];

    if (!message && !file) return;

    appendMessage("You", message);
    messageInput.value = "";
    criteriaInput.value = "";
    imageInput.value = "";

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
        data.messages.forEach((m) => appendMessage(m.role, m.content));
    } catch (err) {
        appendMessage("Assistant", "Something went wrong. Please try again.");
    }
}
