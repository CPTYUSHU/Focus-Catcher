// Chat Application State
const state = {
    chats: [],
    currentChatId: null,
    isLoading: false
};

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('messages-container');
const chatList = document.getElementById('chat-list');
const newChatBtn = document.getElementById('new-chat-btn');

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChatsFromStorage();
    setupEventListeners();
    
    // If no chats exist, create a new one
    if (state.chats.length === 0) {
        createNewChat();
    } else {
        // Load the most recent chat
        switchToChat(state.chats[0].id);
    }
});

// Event Listeners
function setupEventListeners() {
    chatForm.addEventListener('submit', handleSubmit);
    newChatBtn.addEventListener('click', createNewChat);
    
    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });
    
    // Handle Enter key (without Shift)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Example prompts
    document.querySelectorAll('.example-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            userInput.value = prompt;
            chatForm.dispatchEvent(new Event('submit'));
        });
    });
}

// Handle Form Submit
async function handleSubmit(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message || state.isLoading) return;
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Hide welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Add user message to UI
    addMessageToUI('user', message);
    
    // Add user message to current chat
    const currentChat = getCurrentChat();
    if (currentChat) {
        currentChat.messages.push({
            role: 'user',
            content: message,
            timestamp: Date.now()
        });
        saveChatsToStorage();
        updateChatList();
    }
    
    // Show thinking animation
    showThinkingAnimation();
    
    // Disable input
    state.isLoading = true;
    sendBtn.disabled = true;
    userInput.disabled = true;
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Remove thinking animation
        removeThinkingAnimation();
        
        // Add assistant message to UI
        addMessageToUI('assistant', data.content, data.tool_calls);
        
        // Add assistant message to current chat
        if (currentChat) {
            currentChat.messages.push({
                role: 'assistant',
                content: data.content,
                tool_calls: data.tool_calls,
                timestamp: Date.now()
            });
            
            // Update chat title if this is the first message
            if (currentChat.messages.length === 2) {
                currentChat.title = message.substring(0, 50);
            }
            
            saveChatsToStorage();
            updateChatList();
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeThinkingAnimation();
        addMessageToUI('assistant', `❌ Error: ${error.message}. Please make sure the backend server is running.`);
    } finally {
        // Re-enable input
        state.isLoading = false;
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

// UI Functions
function addMessageToUI(role, content, toolCalls = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const roleName = role === 'user' ? 'You' : 'Assistant';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${avatar}</div>
            <div class="message-role">${roleName}</div>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    // Add tool calls badge if present
    if (toolCalls && toolCalls.length > 0) {
        const toolBadge = document.createElement('div');
        toolBadge.className = 'tool-calls-badge';
        toolBadge.innerHTML = `
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            Used ${toolCalls.length} tool${toolCalls.length > 1 ? 's' : ''}
        `;
        messageDiv.appendChild(toolBadge);
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showThinkingAnimation() {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'thinking-message';
    thinkingDiv.id = 'thinking-animation';
    
    thinkingDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">🤖</div>
            <div class="message-role">Assistant</div>
        </div>
        <div class="thinking-content">
            <span>Thinking</span>
            <div class="thinking-dots">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(thinkingDiv);
    scrollToBottom();
}

function removeThinkingAnimation() {
    const thinkingDiv = document.getElementById('thinking-animation');
    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Chat Management
function createNewChat() {
    const newChat = {
        id: Date.now().toString(),
        title: 'New Chat',
        messages: [],
        createdAt: Date.now()
    };
    
    state.chats.unshift(newChat);
    saveChatsToStorage();
    updateChatList();
    switchToChat(newChat.id);
}

function switchToChat(chatId) {
    state.currentChatId = chatId;
    const chat = getCurrentChat();
    
    if (!chat) return;
    
    // Clear messages container
    messagesContainer.innerHTML = '';
    
    // Load messages
    if (chat.messages.length === 0) {
        // Show welcome message
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">👋</div>
                <h2>Welcome to AI Chat Assistant!</h2>
                <p>Ask me anything. I can search the web and read pages to help you.</p>
                <div class="example-prompts">
                    <button class="example-prompt" data-prompt="Who won the Super Bowl in 2025?">
                        🏈 Who won the Super Bowl in 2025?
                    </button>
                    <button class="example-prompt" data-prompt="What are the latest developments in AI?">
                        🤖 Latest AI developments
                    </button>
                    <button class="example-prompt" data-prompt="Explain quantum computing">
                        ⚛️ Explain quantum computing
                    </button>
                </div>
            </div>
        `;
        
        // Re-attach event listeners to example prompts
        document.querySelectorAll('.example-prompt').forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.getAttribute('data-prompt');
                userInput.value = prompt;
                chatForm.dispatchEvent(new Event('submit'));
            });
        });
    } else {
        chat.messages.forEach(msg => {
            addMessageToUI(msg.role, msg.content, msg.tool_calls);
        });
    }
    
    // Update chat list active state
    updateChatList();
    
    // Focus input
    userInput.focus();
}

function getCurrentChat() {
    return state.chats.find(chat => chat.id === state.currentChatId);
}

function updateChatList() {
    chatList.innerHTML = '';
    
    state.chats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = `chat-item ${chat.id === state.currentChatId ? 'active' : ''}`;
        
        const preview = chat.messages.length > 0 
            ? chat.messages[0].content.substring(0, 50) 
            : 'No messages yet';
        
        chatItem.innerHTML = `
            <div class="chat-item-title">${escapeHtml(chat.title)}</div>
            <div class="chat-item-preview">${escapeHtml(preview)}</div>
        `;
        
        chatItem.addEventListener('click', () => {
            switchToChat(chat.id);
        });
        
        chatList.appendChild(chatItem);
    });
}

// Local Storage
function saveChatsToStorage() {
    try {
        localStorage.setItem('chats', JSON.stringify(state.chats));
    } catch (error) {
        console.error('Failed to save chats:', error);
    }
}

function loadChatsFromStorage() {
    try {
        const stored = localStorage.getItem('chats');
        if (stored) {
            state.chats = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Failed to load chats:', error);
        state.chats = [];
    }
}

