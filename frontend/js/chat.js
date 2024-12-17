class ChatUI {
    constructor() {
        console.log('ChatUI initialized');
        this.messagesContainer = document.getElementById('chat-messages');
        this.input = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-btn');
        this.chatHistory = [];

        // 检查元素是否存在
        if (!this.messagesContainer || !this.input || !this.sendButton) {
            console.error('Required elements not found');
            return;
        }

        this.sendButton.addEventListener('click', () => {
            console.log('Send button clicked');
            this.sendMessage();
        });
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        try {
            console.log('Sending message:', this.input.value);
            const message = this.input.value.trim();
            if (!message) return;

            // 添加用户消息到界面
            this.addMessage('user', message);
            this.input.value = '';

            // 检查后端服务器是否可用
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: this.chatHistory
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                const content = data.messages[0].content;
                this.addMessage('assistant', content);
                this.chatHistory.push(
                    { role: 'user', content: message },
                    { role: 'assistant', content: content }
                );

                // 显示输出日志
                if (data.output_log) {
                    data.output_log.forEach(log => {
                        this.addMessage('assistant', log); // 将输出日志添加到聊天界面
                    });
                }
            } else {
                console.error('Server error:', data.error);
                this.addMessage('system', `错误: ${data.error}`);
            }
        } catch (error) {
            console.error('Network error:', error);
            this.addMessage('system', '网络连接错误，请确保后端服务器正在运行');
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        const timestamp = new Date().toLocaleTimeString(); // 获取当前时间
        messageDiv.innerHTML = `
            <div class="message-content">
                ${content}
                <span class="timestamp">${timestamp}</span> <!-- 添加时间戳 -->
            </div>
        `;
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
}

// 初始化聊天界面
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing ChatUI');
    new ChatUI();
});