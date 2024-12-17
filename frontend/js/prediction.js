document.addEventListener('DOMContentLoaded', function() {
    const aiAssistant = document.querySelector('.ai-assistant');
    const minimizeBtn = document.querySelector('.minimize-btn');
    const maximizeBtn = document.querySelector('.maximize-btn');
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.querySelector('.chat-input input');
    const sendButton = document.querySelector('.chat-input button');

    let messageHistory = [];

    // 添加消息到聊天界面
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <span class="message-text">${content}</span>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 发送消息到后端
    async function sendMessage(message) {
        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    history: messageHistory
                })
            });

            const data = await response.json();
            
            if (data.success) {
                messageHistory = data.messages;
                // 获取最后一条助手消息
                const lastMessage = messageHistory[messageHistory.length - 1];
                addMessage(lastMessage.content, false);
            } else {
                addMessage('抱歉,出现了一些错误,请稍后重试。', false);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('抱歉,连接服务器时出现错误。', false);
        }
    }

    // 发送按钮点击事件
    sendButton.addEventListener('click', () => {
        const message = chatInput.value.trim();
        if (message) {
            addMessage(message, true);
            sendMessage(message);
            chatInput.value = '';
        }
    });

    // 输入框回车事件
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });

    // 最小化/最大化功能
    minimizeBtn.addEventListener('click', function() {
        aiAssistant.classList.add('minimized');
        minimizeBtn.style.display = 'none';
        maximizeBtn.style.display = 'block';
    });

    maximizeBtn.addEventListener('click', function() {
        aiAssistant.classList.remove('minimized');
        maximizeBtn.style.display = 'none';
        minimizeBtn.style.display = 'block';
    });
}); 