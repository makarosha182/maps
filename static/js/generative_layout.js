// Generative Layout Extension for Sivas Tourism Advisor
// Add methods to existing SivasAdvisor class

if (typeof SivasAdvisor !== 'undefined') {
    
    SivasAdvisor.prototype.addGenerativeMessage = function(query, layout) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant generative';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Add message header
        const header = document.createElement('div');
        header.className = 'message-header';
        header.innerHTML = '<i class="fas fa-magic"></i>Sivas Advisor (Generative Layout)';
        messageContent.appendChild(header);
        
        // Process layout elements
        const layoutContainer = document.createElement('div');
        layoutContainer.className = 'generative-layout';
        
        layout.forEach((element, index) => {
            if (element.type === 'text') {
                const textElement = document.createElement('div');
                textElement.className = 'layout-text';
                textElement.id = element.id || `text_${index}`;
                textElement.innerHTML = this.formatMessage(element.content);
                layoutContainer.appendChild(textElement);
                
            } else if (element.type === 'image') {
                const imageElement = this.createLayoutImage(element);
                layoutContainer.appendChild(imageElement);
            }
        });
        
        messageContent.appendChild(layoutContainer);
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    };
    
    SivasAdvisor.prototype.createLayoutImage = function(imageElement) {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'layout-image';
        
        if (imageElement.image_data) {
            const img = imageElement.image_data;
            
            imageContainer.innerHTML = `
                <div class="image-item">
                    <img src="${img.url}" alt="${img.alt}" title="${img.title}" loading="lazy" />
                    <div class="image-caption">
                        <div class="image-title">${imageElement.description || img.title}</div>
                        <small>Photo by <a href="${img.photographer_url}" target="_blank">${img.photographer}</a> on Unsplash</small>
                        <div class="search-info">🔍 Found with: "${imageElement.search_query}"</div>
                    </div>
                </div>
            `;
        } else {
            imageContainer.innerHTML = `
                <div class="image-placeholder">
                    <div class="placeholder-text">🚫 Image not found for: "${imageElement.search_query}"</div>
                </div>
            `;
        }
        
        return imageContainer;
    };
    
    console.log('✅ Generative Layout extension loaded!');
}
