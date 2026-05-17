// Cyber Buddy Frontend Application

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const navButtons = document.querySelectorAll('.nav-btn');
const contentSections = document.querySelectorAll('.content-section');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const urlInput = document.getElementById('urlInput');
const checkUrlBtn = document.getElementById('checkUrlBtn');
const urlResult = document.getElementById('urlResult');
const locationInput = document.getElementById('locationInput');
const findOfficeBtn = document.getElementById('findOfficeBtn');
const officeResult = document.getElementById('officeResult');
const refreshNewsBtn = document.getElementById('refreshNewsBtn');
const newsGrid = document.getElementById('newsGrid');
const lastUpdated = document.getElementById('lastUpdated');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeNavigation();
        initializeChatBot();
        initializeRiskChecker();
        initializeReport();
        initializeNews();

        // Load news on startup
        loadCybersecurityNews();
    } catch (error) {
        console.error('Error initializing application:', error);
    }
});

// Navigation System
function initializeNavigation() {
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetSection = button.getAttribute('data-section');
            switchSection(targetSection);
            
            // Update active button
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        });
    });
}

function switchSection(sectionName) {
    contentSections.forEach(section => {
        section.classList.remove('active');
    });
    
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
    }
}

// Chat Bot Functionality
function initializeChatBot() {
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

async function sendMessage() {
    if (!chatInput) return;
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE_URL}/bot/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_history: []
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (response.ok) {
            addMessageToChat(data.response, 'bot');
            
            // If there's cyber law information, display it specially
            if (data.cyber_law_info) {
                addCyberLawInfo(data.cyber_law_info);
            }
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'bot');
        console.error('Chat error:', error);
    }
}

function addMessageToChat(message, sender) {
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-shield-alt';

    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="${icon}"></i>
            <div class="text">${formatMessage(message)}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addCyberLawInfo(lawInfo) {
    const lawDiv = document.createElement('div');
    lawDiv.className = 'message bot-message';
    
    lawDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-gavel"></i>
            <div class="text">
                <h4>📚 Cyber Law Information: ${lawInfo.attack_name}</h4>
                <p><strong>Definition:</strong> ${lawInfo.definition}</p>
                <p><strong>Applicable Law:</strong> ${lawInfo.indian_cyber_law}</p>
                <p><strong>Penalty:</strong> ${lawInfo.penalty}</p>
                <p><strong>Safety Tips:</strong></p>
                <ul>
                    ${lawInfo.safety_tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(lawDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(message) {
    // Convert markdown-like formatting to HTML
    return message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

function showTypingIndicator() {
    if (typingIndicator) {
        typingIndicator.style.display = 'flex';
    }
}

function hideTypingIndicator() {
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
    }
}

// Risk Checker Functionality
function initializeRiskChecker() {
    if (checkUrlBtn) {
        checkUrlBtn.addEventListener('click', checkUrlSafety);
    }
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                checkUrlSafety();
            }
        });
    }
}

async function checkUrlSafety() {
    const url = urlInput.value.trim();
    if (!url) {
        alert('Please enter a URL to check');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/risk-checker/check-url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (response.ok) {
            displayUrlResult(data);
        } else {
            alert('Error checking URL: ' + data.detail);
        }
    } catch (error) {
        hideLoading();
        alert('Error checking URL. Please try again.');
        console.error('URL check error:', error);
    }
}

function displayUrlResult(result) {
    const statusIndicator = document.getElementById('statusIndicator');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const checkedUrl = document.getElementById('checkedUrl');
    const threatInfo = document.getElementById('threatInfo');
    const threatList = document.getElementById('threatList');
    
    // Set status indicator
    statusIndicator.className = 'status-indicator';
    if (result.is_safe) {
        statusIndicator.classList.add('safe');
        statusIndicator.innerHTML = '✅';
        resultTitle.textContent = 'SAFE';
    } else if (result.status === 'RISKY') {
        statusIndicator.classList.add('risky');
        statusIndicator.innerHTML = '❌';
        resultTitle.textContent = 'RISKY';
    } else {
        statusIndicator.classList.add('unknown');
        statusIndicator.innerHTML = '⚠️';
        resultTitle.textContent = 'UNKNOWN';
    }
    
    resultMessage.textContent = result.message;
    checkedUrl.textContent = result.url;
    
    // Show threat information if available
    if (result.threat_types && result.threat_types.length > 0) {
        threatList.innerHTML = result.threat_types.map(threat => `<li>${threat}</li>`).join('');
        threatInfo.style.display = 'block';
    } else {
        threatInfo.style.display = 'none';
    }
    
    urlResult.style.display = 'block';
}

// Report Functionality
function initializeReport() {
    findOfficeBtn.addEventListener('click', findCybercrimeOffice);
    locationInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            findCybercrimeOffice();
        }
    });
}

async function findCybercrimeOffice() {
    const location = locationInput.value.trim();
    if (!location) {
        alert('Please enter a state or city name');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/report/offices/${encodeURIComponent(location)}`);
        const data = await response.json();
        
        hideLoading();
        
        if (response.ok) {
            displayOfficeResult(data);
        } else {
            alert('Error finding office: ' + data.detail);
        }
    } catch (error) {
        hideLoading();
        alert('Error finding office. Please try again.');
        console.error('Office search error:', error);
    }
}

function displayOfficeResult(result) {
    const officeLocation = document.getElementById('officeLocation');
    const officeAddress = document.getElementById('officeAddress');
    const officeHelpline = document.getElementById('officeHelpline');
    const officeWebsite = document.getElementById('officeWebsite');
    
    officeLocation.textContent = `Cybercrime Office - ${result.location}`;
    
    if (result.office_info) {
        officeAddress.textContent = result.office_info.address;
        officeHelpline.textContent = result.office_info.helpline;
        officeWebsite.textContent = result.office_info.website;
        officeWebsite.href = result.office_info.website;
    } else {
        officeAddress.textContent = 'Specific office information not available for this location.';
        officeHelpline.textContent = result.national_helpline;
        officeWebsite.textContent = result.national_website;
        officeWebsite.href = result.national_website;
    }
    
    officeResult.style.display = 'block';
}

// News Functionality
function initializeNews() {
    refreshNewsBtn.addEventListener('click', loadCybersecurityNews);
}

async function loadCybersecurityNews() {
    showNewsLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/news/cybersecurity`);
        const data = await response.json();
        
        if (response.ok) {
            displayNews(data);
            updateLastUpdated(data.last_updated);
        } else {
            showNewsError();
        }
    } catch (error) {
        showNewsError();
        console.error('News loading error:', error);
    }
}

function displayNews(newsData) {
    newsGrid.innerHTML = '';
    
    newsData.articles.forEach(article => {
        const articleDiv = document.createElement('div');
        articleDiv.className = 'news-article';
        
        const publishedDate = new Date(article.published_at).toLocaleDateString();
        
        articleDiv.innerHTML = `
            <h3>${article.title}</h3>
            <div class="news-meta">
                <span class="news-source">${article.source}</span>
                <span>${publishedDate}</span>
            </div>
            <p class="news-summary">${article.summary}</p>
        `;
        
        newsGrid.appendChild(articleDiv);
    });
}

function showNewsLoading() {
    newsGrid.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading latest cybersecurity news...</p>
        </div>
    `;
}

function showNewsError() {
    newsGrid.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-exclamation-triangle"></i>
            <p>Unable to load news. Please try again later.</p>
        </div>
    `;
}

function updateLastUpdated(timestamp) {
    const date = new Date(timestamp);
    lastUpdated.textContent = `Last updated: ${date.toLocaleString()}`;
}

// Utility Functions
function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Additional Functions for Footer Links
function showPrivacyInfo() {
    alert('Privacy Policy: Cyber Buddy respects your privacy. We do not store personal conversations or data. All communications are processed securely.');
}

function showAboutInfo() {
    alert('About Cyber Buddy: A comprehensive cybersecurity platform designed to help users stay safe online. Features include AI-powered cybersecurity assistance, URL safety checking, cybercrime reporting, and latest security news.');
}
