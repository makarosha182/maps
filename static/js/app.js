// Sivas Tourism Advisor - Frontend JavaScript

class SivasAdvisor {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatForm = document.getElementById('chatForm');
        this.queryInput = document.getElementById('queryInput');
        this.submitBtn = document.getElementById('submitBtn');
        this.loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        
        this.initialize();
    }
    
    initialize() {
        // Bind event handlers
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Bind suggestion buttons
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleSuggestionClick(e));
        });
        
        // Auto-focus input
        this.queryInput.focus();
        
        // Handle Enter key
        this.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSubmit(e);
            }
        });
    }
    
    handleSuggestionClick(e) {
        const suggestion = e.target.dataset.suggestion;
        if (suggestion) {
            this.queryInput.value = suggestion;
            this.queryInput.focus();
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const query = this.queryInput.value.trim();
        if (!query) return;
        
        // Clear input and disable form
        this.queryInput.value = '';
        this.setLoading(true);
        
        // Remove welcome message if present
        this.removeWelcomeMessage();
        
        // Add user message
        this.addMessage(query, 'user');
        
        // Add typing indicator
        this.addTypingIndicator();
        
        try {
            // Send request to API
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    language: 'ru'
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add assistant response with images
            this.addMessage(data.response, 'assistant', data.sources, data.images);
            
        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator();
            this.addMessage(
                'Sorry, an error occurred while processing your request. Please try again.',
                'assistant'
            );
        } finally {
            this.setLoading(false);
        }
    }
    
    removeWelcomeMessage() {
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }
    
    addMessage(content, sender, sources = null, images = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Add message header
        const header = document.createElement('div');
        header.className = 'message-header';
        
        if (sender === 'user') {
            header.innerHTML = '<i class="fas fa-user"></i>You';
        } else {
            header.innerHTML = '<i class="fas fa-robot"></i>Sivas Advisor';
        }
        
        messageContent.appendChild(header);
        
        // Add message text
        const textDiv = document.createElement('div');
        textDiv.innerHTML = this.formatMessage(content);
        messageContent.appendChild(textDiv);
        
        // Add images if available
        if (images && images.length > 0) {
            const imagesDiv = document.createElement('div');
            imagesDiv.className = 'images-gallery';
            
            images.forEach(image => {
                const imageItem = document.createElement('div');
                imageItem.className = 'image-item';
                
                const photographerCredit = image.photographer ? 
                    `<small>Photo by <a href="${image.photographer_url}" target="_blank">${image.photographer}</a> on Unsplash</small>` : '';
                
                imageItem.innerHTML = `
                    <img src="${image.url}" alt="${image.alt}" title="${image.title}" loading="lazy" />
                    <div class="image-caption">
                        <div class="image-title">${image.title}</div>
                        ${photographerCredit}
                    </div>
                `;
                imagesDiv.appendChild(imageItem);
            });
            
            messageContent.appendChild(imagesDiv);
        }
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';
            sourcesDiv.innerHTML = '<small><strong><i class="fas fa-link me-1"></i>Sources:</strong></small>';
            
            sources.forEach(source => {
                if (source.title && source.title !== 'Untitled') {
                    const sourceItem = document.createElement('div');
                    sourceItem.className = 'source-item';
                    sourceItem.innerHTML = `
                        <i class="fas fa-external-link-alt"></i>
                        <a href="${source.url}" target="_blank" class="text-decoration-none">
                            ${source.title} (${source.page_type})
                        </a>
                    `;
                    sourcesDiv.appendChild(sourceItem);
                }
            });
            
            messageContent.appendChild(sourcesDiv);
        }
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator message assistant';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <i class="fas fa-robot"></i>Sivas Advisor
                </div>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    formatMessage(content) {
        // Simple formatting - convert line breaks to <br>
        return content
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    setLoading(isLoading) {
        if (isLoading) {
            this.submitBtn.disabled = true;
            this.queryInput.disabled = true;
            this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            this.submitBtn.disabled = false;
            this.queryInput.disabled = false;
            this.submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            this.queryInput.focus();
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SivasAdvisor();
});

// Service worker registration for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
