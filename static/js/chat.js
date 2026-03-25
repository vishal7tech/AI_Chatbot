function addMessage(text, isUser = false) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    if (isUser) {
        msgDiv.classList.add('user');
    } else {
        msgDiv.classList.add('bot');
    }
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);

    // Auto scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message) return;

    // Show user message
    addMessage(message, true);

    // Clear input
    input.value = '';

    // Send to backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let msg = data.response || "No response from bot";
            addMessage(msg, false);

            // Enhanced confidence display
            if (data.confidence !== undefined && data.confidence > 0) {
                const chatBox = document.getElementById('chat-box');
                const confDiv = document.createElement('div');
                confDiv.style.fontSize = "0.75rem";
                confDiv.style.textAlign = "left";
                confDiv.style.marginTop = "-8px";
                confDiv.style.marginBottom = "10px";
                confDiv.style.marginLeft = "12px";
                confDiv.style.padding = "4px 8px";
                confDiv.style.borderRadius = "12px";
                confDiv.style.display = "inline-block";
                
                // Color coding based on confidence
                const confidence = parseFloat(data.confidence);
                if (confidence >= 80) {
                    confDiv.style.backgroundColor = "#d4edda";
                    confDiv.style.color = "#155724";
                    confDiv.textContent = `🎯 High Confidence: ${confidence.toFixed(1)}%`;
                } else if (confidence >= 60) {
                    confDiv.style.backgroundColor = "#fff3cd";
                    confDiv.style.color = "#856404";
                    confDiv.textContent = `🤔 Medium Confidence: ${confidence.toFixed(1)}%`;
                } else {
                    confDiv.style.backgroundColor = "#f8d7da";
                    confDiv.style.color = "#721c24";
                    confDiv.textContent = `⚠️ Low Confidence: ${confidence.toFixed(1)}%`;
                }
                
                chatBox.appendChild(confDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Sorry, something went wrong... 😕", false);
        });
}

// Enter key support
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        e.preventDefault(); // Stop form submit behavior
        sendMessage();
    }
});

// Optional: Welcome message when page loads
window.onload = function () {
    addMessage("🤖 Hello! I'm your AI Assistant. I can help with greetings, fees, appointments, and more. Try asking me anything! 😊", false);
};