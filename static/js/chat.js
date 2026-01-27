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
        addMessage(data.response || "No response from bot", false);
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("Sorry, something went wrong... 😕", false);
    });
}

// Enter key support
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault(); // Stop form submit behavior
        sendMessage();
    }
});

// Optional: Welcome message when page loads
window.onload = function() {
    addMessage("Hello! I'm RuleBot. How can I help you today? 😊", false);
};