document.addEventListener("DOMContentLoaded", function () {

    /* ================= SIDEBAR ACTIVE SWITCH ================= */
    const workers = document.querySelectorAll(".worker-card");

    workers.forEach(worker => {
        worker.addEventListener("click", function () {
            workers.forEach(w => w.classList.remove("active"));
            this.classList.add("active");
        });
    });

    /* ================= SEND MESSAGE ================= */
    const sendBtn = document.querySelector(".send-btn");
    const input = document.querySelector(".chat-input input");
    const chatMessages = document.querySelector(".chat-messages");

    function sendMessage() {
        const messageText = input.value.trim();
        if (messageText === "") return;

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", "right");

        messageDiv.innerHTML = `
            <div class="bubble">${messageText}</div>
            <span>${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        `;

        chatMessages.appendChild(messageDiv);
        input.value = "";

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendBtn.addEventListener("click", sendMessage);

    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    /* ================= DARK MODE ================= */
    const toggleBtn = document.getElementById("themeToggle");

    toggleBtn.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");

        if (document.body.classList.contains("dark-mode")) {
            toggleBtn.textContent = "☀️";
        } else {
            toggleBtn.textContent = "🌙";
        }
    });

});
