const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

function appendMessage(content, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    msg.innerHTML = sender === "bot" ? marked.parse(content) : content;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

// function sendMessage() {
//     const message = userInput.value.trim();
//     if (!message) return;

//     appendMessage(message, "user");
//     userInput.value = "";

//     appendMessage("Searching", "bot");

//     fetch("/chat", {
//         method: "POST",
//         headers: {"Content-Type": "application/json"},
//         body: JSON.stringify({message})
//     })
//     .then(res => res.json())
//     .then(data => {
//         document.querySelector(".bot-message:last-child").remove();
//         appendMessage(data.response, "bot");
//     })
//     .catch(err => {
//         console.error("Error:", err);
//     });
// }


function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    userInput.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message})
    })
    .then(res => res.json())
    .then(data => {
        appendMessage(data.response, "bot");
    })
    .catch(err => {
        console.error("Error:", err);
    });
}
