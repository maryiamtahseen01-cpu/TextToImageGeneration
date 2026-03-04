        // Function to update the history sidebar with a new item
        function updateHistorySidebar(newItem) {
            try {
                const historyList = document.getElementById('promptHistoryList');
                const sidebar = document.getElementById('promptSidebar');
                
                // Only update if sidebar is open and element exists
                if (!historyList || !sidebar || !sidebar.classList.contains('open')) {
                    return; // Don't update if sidebar is not open
                }
                
                // Create the history item element
                const date = new Date(newItem.timestamp);
                const timeString = date.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                });
                const dateString = date.toLocaleDateString();
                
                const historyItem = document.createElement('div');
                historyItem.className = 'prompt-history-item';
                historyItem.innerHTML = `
                    <div class="history-text">
                        <div class="prompt-text">${newItem.prompt || 'No prompt'}</div>
                        <div class="prompt-meta">
                            <div class="prompt-date">
                                <i class="bi bi-calendar"></i>
                                <span>${dateString} • ${timeString}</span>
                            </div>
                            <div class="prompt-actions">
                                <button class="prompt-action-btn" onclick="usePrompt('${(newItem.prompt || '').replace(/'/g, "\\'")}')" title="Use this prompt">
                                    <i class="bi bi-arrow-return-left"></i>
                                </button>
                                <button class="prompt-action-btn" onclick="deleteHistoryItem('${newItem.id || newItem._id || historyList.children.length}', 'all'); event.stopPropagation();" title="Delete">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Add the new item at the beginning of the list
                if (historyList.firstChild) {
                    historyList.insertBefore(historyItem, historyList.firstChild);
                } else {
                    historyList.appendChild(historyItem);
                }
                
                // Limit the number of items displayed (keep only first 20 to avoid UI clutter)
                if (historyList.children.length > 20) {
                    historyList.removeChild(historyList.lastChild);
                }
                
            } catch (error) {
                console.error('Error updating history sidebar:', error);
            }
        }