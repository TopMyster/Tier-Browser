let currentEngine = "Bing";
let searchUrl = "https://www.bing.com/search?q=";
let browserSettings = {
searchEngine: "Bing",
theme: "light",
homepage: "home.html",
chatbot: "default",
version: "1.0.0"
};

function loadUserSettings() {
try {
const savedSettings = localStorage.getItem('browserSettings');
if (savedSettings) {
browserSettings = { ...browserSettings, ...JSON.parse(savedSettings) };
} else {
fetch('settings.json')
.then(response => response.json())
.then(data => {
browserSettings = { ...browserSettings, ...data };
applyUserSettings();
})
.catch(() => applyUserSettings());
}
applyUserSettings();
} catch (error) {
applyUserSettings();
}
}

function saveUserSettings() {
localStorage.setItem('browserSettings', JSON.stringify(browserSettings));
}

function applyUserSettings() {
currentEngine = browserSettings.searchEngine;
updateSearchEngine();
switchTheme(browserSettings.theme);
applyChatbotSettings();
}

function switchTheme(theme) {
const body = document.body;

if (theme === 'dark') {
// Add dark theme class to body
body.classList.add('dark-theme');
body.classList.remove('light-theme');
} else {
// Add light theme class to body (or remove dark theme class)
body.classList.remove('dark-theme');
body.classList.add('light-theme');
}

// Handle special case for search bar placeholder and chat command color
const searchbar = document.getElementById('searchbar');
if (searchbar) {
const currentValue = searchbar.value;
if (currentValue.includes('/ch')) {
// Keep the special chat command color override
if (theme === 'dark') {
searchbar.style.color = 'rgba(0, 200, 120, 1)';
} else {
searchbar.style.color = 'rgba(0, 124, 82, 1)';
}
} else {
// Remove any inline color to let CSS variables take over
searchbar.style.color = '';
}
}
}

function updateSearchEngine() {
const engines = {
"Google": "https://www.google.com/search?q=",
"Perplexity": "https://www.perplexity.ai/search?q=",
"Bing": "https://www.bing.com/search?q=",
"Brave": "https://search.brave.com/search?q=",
"Yahoo": "https://search.yahoo.com/search?p=",
"Duckduckgo": "https://duckduckgo.com/?q="
};
searchUrl = engines[currentEngine] || engines["Bing"];
}

function changeSearchEngine(engineName) {
browserSettings.searchEngine = engineName;
currentEngine = engineName;
updateSearchEngine();
saveUserSettings();
}

function changeTheme(theme) {
browserSettings.theme = theme;
switchTheme(theme);
saveUserSettings();
}

function setupEngineSelector() {
const engineSelect = document.getElementById('engineSelect');
if (engineSelect) {
engineSelect.value = currentEngine;
engineSelect.addEventListener('change', function() {
changeSearchEngine(this.value);
});
}
}

function setupThemeSelector() {
const themeSelect = document.getElementById('themeSelect');
if (themeSelect) {
themeSelect.value = browserSettings.theme;
themeSelect.addEventListener('change', function() {
changeTheme(this.value);
});
}
}

function changeChatbot(chatbotType) {
browserSettings.chatbot = chatbotType;
applyChatbotSettings();
saveUserSettings();
}

function applyChatbotSettings() {
const chatContainer = document.getElementById('chatContainer');
if (!chatContainer) return;

chatContainer.innerHTML = '';

const chatWebview = document.createElement('webview');
chatWebview.style.width = '100%';
chatWebview.style.height = '100%';
chatWebview.style.border = 'none';

if (browserSettings.chatbot === 'chatgpt') {

chatWebview.src = 'https://chatgpt.com';
} else if (browserSettings.chatbot === 'gemini') {

chatWebview.src = 'https://gemini.google.com';
} else if (browserSettings.chatbot === 'perplexity') {

chatWebview.src = 'https://www.perplexity.ai';
} else {

chatWebview.src = 'https://cdn.botpress.cloud/webchat/v3.2/shareable.html?configUrl=https://files.bpcontent.cloud/2025/07/21/19/20250721195356-NX7X7607.json';
}

chatContainer.appendChild(chatWebview);
}

function setupChatbotSelector() {
const chatbotSelect = document.getElementById('chatbotSelect');
if (chatbotSelect) {
chatbotSelect.value = browserSettings.chatbot;
chatbotSelect.addEventListener('change', function() {
changeChatbot(this.value);
});
}
}

let tabs = [];
let activeTabIndex = 0;
let tabCounter = 0;

function initTabs() {
createNewTab('home.html', 'Home');
}

function createNewTab(url = 'home.html', title = 'New Tab') {
const tabId = `tab-${++tabCounter}`;
const tab = {
id: tabId,
url: url,
title: title,
history: [url]
};

tabs.push(tab);
activeTabIndex = tabs.length - 1;

updateTabsUI();
loadTabContent(activeTabIndex);
return tab;
}

function closeTab(index) {
if (tabs.length <= 1) return;

tabs.splice(index, 1);

if (activeTabIndex >= tabs.length) {
activeTabIndex = tabs.length - 1;
} else if (activeTabIndex > index) {
activeTabIndex--;
}

updateTabsUI();
loadTabContent(activeTabIndex);
}

function switchToTab(index) {
if (index >= 0 && index < tabs.length) {
activeTabIndex = index;
loadTabContent(activeTabIndex);
updateTabsUI();
hidTabs();
}
}

function loadTabContent(index) {
if (tabs[index]) {
const webview = document.getElementById('Browser');
webview.loadURL(tabs[index].url);
document.getElementById('searchbar').value = tabs[index].url === 'home.html' ? '' : tabs[index].url;
}
}

function updateTabsUI() {
    const tabsContainer = document.getElementById('tabs');
    
    // Clear existing tabs
    while (tabsContainer.firstChild) {
        tabsContainer.removeChild(tabsContainer.firstChild);
    }

    // Render the current tabs
    tabs.forEach((tab, index) => {
        const tabElement = document.createElement('div');
        tabElement.className = 'tab-item';
        tabElement.innerHTML = `
            <div class="tab-content" onclick="switchToTab(${index})">
                <span class="tab-title">${tab.title}</span>
                <span class="tab-url">${tab.url}</span>
            </div>
            <button class="tab-close" onclick="closeTab(${index})" ${tabs.length <= 1 ? 'disabled' : ''}>×</button>
        `;

        if (index === activeTabIndex) {
            tabElement.classList.add('active-tab');
        }

        tabsContainer.appendChild(tabElement);
    });
}

function updateCurrentTabUrl(url) {
if (tabs[activeTabIndex]) {
tabs[activeTabIndex].url = url;
tabs[activeTabIndex].title = getPageTitle(url);
updateTabsUI();
}
}

function getPageTitle(url) {
if (url === 'home.html') return 'Home';
if (url.includes('google.com')) return 'Google';
if (url.includes('bing.com')) return 'Bing';
if (url.includes('chatgpt.com')) return 'ChatGPT';

try {
const urlObj = new URL(url.startsWith('http') ? url : 'https://' + url);
return urlObj.hostname;
} catch {
return 'New Tab';
}
}

document.getElementById('searchbar').addEventListener('input', function(){
let search = document.getElementById('searchbar').value;
const isDark = document.body.classList.contains('dark-theme');

if (search.includes('/ch')) {
// Special color for chat command
if (isDark) {
document.getElementById('searchbar').style.color = 'rgba(0, 200, 120, 1)';
} else {
document.getElementById('searchbar').style.color = 'rgba(0, 124, 82, 1)';
}
} else {
// Remove inline style to let CSS variables take over
document.getElementById('searchbar').style.color = '';
}
});


function back() {
document.getElementById('Browser').goBack();
}
function forward() {
document.getElementById('Browser').goForward();
}

function openlink() {
const searchQuery = document.getElementById('searchbar').value.trim();
let url;
let engine = searchUrl;

if (searchQuery.startsWith('/ch')) {
engine = 'https://chatgpt.com/?q=';
const query = searchQuery.slice(3).trim();
url = engine + encodeURIComponent(query);
} else if (searchQuery.includes('.')) {
url = searchQuery.startsWith('http') ? searchQuery : 'https://' + searchQuery;
} else {
url = engine + encodeURIComponent(searchQuery);
}

document.getElementById('Browser').loadURL(url);
updateCurrentTabUrl(url);
}


function showTabs() {
document.getElementById('tabs').style.display = 'block';
updateTabsUI();
}

function hidTabs() {
document.getElementById('tabs').style.display = 'none';
}

function toggleTabs() {
const tabsElement = document.getElementById('tabs');
if (tabsElement.style.display === 'none' || tabsElement.style.display === '') {
showTabs();
} else {
hidTabs();
}
}

document.getElementById('searchbar').addEventListener('keydown', function(event) {
if (event.key === 'Enter') {
openlink();
}
});

function showSettings(){
document.getElementById('settings').style.display = 'block';
}
function hidSettings(){
document.getElementById('settings').style.display = 'none';
}

function newtab() {
const url = browserSettings.homepage || 'home.html';
createNewTab(url, 'New Tab');
document.getElementById('searchbar').value = '';
}

document.addEventListener('keydown', function(event) {
const isCmd = event.metaKey || event.ctrlKey;

if (isCmd && event.key === 't') {
event.preventDefault();
newtab();
}

if (isCmd && event.key === 'w' && tabs.length > 1) {
event.preventDefault();
closeTab(activeTabIndex);
}

if (isCmd && event.shiftKey && event.key === 'T') {
event.preventDefault();
toggleTabs();
}

if (isCmd && event.key >= '1' && event.key <= '9') {
event.preventDefault();
const tabIndex = parseInt(event.key) - 1;
if (tabIndex < tabs.length) switchToTab(tabIndex);
}

// Add F5 and Cmd+R for webview reload
if (event.key === 'F5' || (isCmd && event.key === 'r')) {
event.preventDefault();
reloadWebview();
}

// Add Cmd+, to go to home
if (isCmd && event.key === ',') {
event.preventDefault();
goToHome();
}

// Add Cmd+Shift+C to test context menu
if (isCmd && event.shiftKey && event.key === 'C') {
event.preventDefault();
showSimpleContextMenu(window.innerWidth / 2, window.innerHeight / 2);
}

if (event.key === 'Escape') hidTabs();
});

let lastSettings = JSON.stringify(browserSettings);
setInterval(function() {
const saved = localStorage.getItem('browserSettings');
if (saved && saved !== lastSettings) {
try {
const newSettings = JSON.parse(saved);
if (newSettings.searchEngine !== browserSettings.searchEngine) {
changeSearchEngine(newSettings.searchEngine);
}
if (newSettings.theme !== browserSettings.theme) {
changeTheme(newSettings.theme);
}
if (newSettings.chatbot !== browserSettings.chatbot) {
changeChatbot(newSettings.chatbot);
}
lastSettings = saved;
} catch (error) {
console.log('Settings sync error:', error);
}
}
}, 1000);

window.addEventListener('message', function(event) {
if (event.data?.type === 'ENGINE_CHANGED') {
changeSearchEngine(event.data.engine);
}
if (event.data?.type === 'THEME_CHANGED') {
changeTheme(event.data.theme);
}
if (event.data?.type === 'CHATBOT_CHANGED') {
changeChatbot(event.data.chatbot);
}
// Handle context menu actions from webview
if (event.data?.type === 'CONTEXT_MENU_ACTION') {
    const { action, url } = event.data;
    switch (action) {
        case 'new-tab':
            if (url) {
                createNewTab(url, getPageTitle(url));
            }
            break;
        case 'new-window':
            if (url && window.electronAPI?.openNewWindow) {
                window.electronAPI.openNewWindow(url);
            } else if (url) {
                // Fallback: open in new tab if new window API not available
                createNewTab(url, getPageTitle(url));
            }
            break;
        case 'inspect':
            // Open dev tools for the webview
            const webview = document.getElementById('Browser');
            if (webview && webview.openDevTools) {
                webview.openDevTools();
            }
            break;
        case 'save-as':
            if (url) {
                // Create a temporary link to trigger download
                const a = document.createElement('a');
                a.href = url;
                a.download = url.split('/').pop() || 'download';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
            break;
    }
}
});

window.addEventListener('DOMContentLoaded', function() {
loadUserSettings();

// Load saved session or create initial tab
setTimeout(() => {
    loadBrowserSession();
    // If no session was loaded, create initial tab
    if (tabs.length === 0) {
        initTabs();
    }
}, 100);

setupEngineSelector();
setupThemeSelector();
setupChatbotSelector();

const webview = document.getElementById('Browser');
webview.addEventListener('did-navigate', (event) => {
    updateCurrentTabUrl(event.url);
    // Re-setup context menu after navigation
    setTimeout(() => setupWebviewContextMenu(), 1000);
});
webview.addEventListener('did-navigate-in-page', (event) => {
    updateCurrentTabUrl(event.url);
    // Re-setup context menu after in-page navigation
    setTimeout(() => setupWebviewContextMenu(), 1000);
});

webview.addEventListener('dom-ready', function() {
setTimeout(() => {
setupEngineSelector();
setupWebviewContextMenu(); // Setup context menu when DOM is ready
}, 500);
});

// Setup context menu for webview
setupWebviewContextMenu();

document.addEventListener('click', function(event) {
const tabsElement = document.getElementById('tabs');
const tabButton = document.getElementById('tabbutton');

if (!tabsElement.contains(event.target) && !tabButton.contains(event.target)) {
if (tabsElement.style.display === 'block') {
hidTabs();
}
}
});

// Add global right-click listener
document.addEventListener('contextmenu', function(event) {
    console.log('Global right-click detected at:', event.clientX, event.clientY);
    // Check if the right-click is on the webview or inside the browser area
    const webview = document.getElementById('Browser');
    const browserContainer = document.getElementById('browserContainer');
    
    if (webview && (event.target === webview || browserContainer.contains(event.target))) {
        event.preventDefault();
        console.log('Showing context menu for webview area at:', event.clientX, event.clientY);
        
        // Use the exact mouse position
        showWorkingContextMenu(event.clientX, event.clientY, webview);
    }
});
});

document.getElementById('bmbtn').addEventListener('click', function() {
    var bookmark = document.getElementById('bookmarks');
    if (bookmark.style.display === 'none' || bookmark.style.display === '') {
        bookmark.style.display = 'block';
    } else {
        bookmark.style.display = 'none';
    }
});
function addbm() {

if (!document.getElementById('bmlink') || !document.getElementById('bmtext')) {
    alert('Please enter both a name and a URL for the bookmark.');
}
const bmText = document.getElementById('bmtext').value;
const bmLink = document.getElementById('bmlink').value;
const url = 'https://' + bmLink;
let newEl = document.createElement('a');
let btnText = document.createTextNode("   " + bmText + "   ");
newEl.appendChild(btnText);
let bmlink = document.createAttribute('href');
bmlink.value = url;
newEl.setAttributeNode(bmlink);
newEl.onclick = function(e) {
    e.preventDefault();
    document.getElementById('Browser').src = url;
};
document.getElementById('bookmarks').appendChild(newEl);

}

document.getElementById('chatbtn').addEventListener('click', function() {
    toggleChatPanel();
});

function toggleChatPanel() {
    var chatContainer = document.getElementById('chatContainer');
    var webview = document.getElementById('Browser');
    
    if (chatContainer.classList.contains('show')) {
        // Close chat panel
        chatContainer.classList.remove('show');
        webview.style.width = '100%';
    } else {
        // Open chat panel
        chatContainer.classList.add('show');
        webview.style.width = 'calc(100% - 400px)';
    }
}

// Handle IPC messages from the main process for global keyboard shortcuts
const { ipcRenderer } = require('electron');

ipcRenderer.on('toggle-chat-panel', () => {
    console.log('Chat panel toggled via global shortcut');
    toggleChatPanel();
});

ipcRenderer.on('toggle-tabbar', () => {
    const tabbar = document.getElementById('tabbar');

    if (tabbar) {
        if (tabbar.style.display === 'none' || tabbar.style.display === '') {
            tabbar.style.display = 'block';
            console.log('Tabbar shown via global shortcut');
        } else {
            tabbar.style.display = 'none';
            console.log('Tabbar hidden via global shortcut');
        }
    }
});

// Context menu functionality
ipcRenderer.on('context-menu-action', (event, data) => {
    if (data.action === 'new-tab' && data.url) {
        createNewTab(data.url, getPageTitle(data.url));
    }
});

ipcRenderer.on('navigate-to-url', (event, url) => {
    if (url) {
        createNewTab(url, getPageTitle(url));
    }
});

// Webview reload functionality
ipcRenderer.on('reload-webview-response', () => {
    const webview = document.getElementById('Browser');
    if (webview) {
        webview.reload();
        console.log('Webview reloaded');
    }
});

// Function to reload only the webview
function reloadWebview() {
    const webview = document.getElementById('Browser');
    if (webview) {
        webview.reload();
        console.log('Webview reloaded manually');
    }
}

// Function to go to home page
function goToHome() {
    const webview = document.getElementById('Browser');
    if (webview) {
        webview.loadURL('home.html');
        updateCurrentTabUrl('home.html');
        document.getElementById('searchbar').value = '';
        console.log('Navigated to home');
    }
}

// Session persistence functions
function saveBrowserSession() {
    const sessionData = {
        tabs: tabs,
        activeTabIndex: activeTabIndex,
        settings: browserSettings,
        timestamp: Date.now()
    };
    
    if (window.electronAPI && window.electronAPI.saveBrowserState) {
        window.electronAPI.saveBrowserState(sessionData);
    } else {
        localStorage.setItem('browserSession', JSON.stringify(sessionData));
    }
}

function loadBrowserSession() {
    if (window.electronAPI && window.electronAPI.loadBrowserState) {
        window.electronAPI.loadBrowserState().then(result => {
            if (result.success && result.data) {
                restoreSession(result.data);
            } else {
                // Fallback to localStorage
                loadFromLocalStorage();
            }
        });
    } else {
        loadFromLocalStorage();
    }
}

function loadFromLocalStorage() {
    try {
        const sessionData = localStorage.getItem('browserSession');
        if (sessionData) {
            const parsedData = JSON.parse(sessionData);
            restoreSession(parsedData);
        }
    } catch (error) {
        console.log('Failed to load session from localStorage:', error);
    }
}

function restoreSession(sessionData) {
    if (sessionData.tabs && sessionData.tabs.length > 0) {
        tabs = sessionData.tabs;
        activeTabIndex = sessionData.activeTabIndex || 0;
        tabCounter = Math.max(...tabs.map(tab => parseInt(tab.id.split('-')[1])));
        
        if (sessionData.settings) {
            browserSettings = { ...browserSettings, ...sessionData.settings };
            applyUserSettings();
        }
        
        updateTabsUI();
        loadTabContent(activeTabIndex);
        console.log('Session restored with', tabs.length, 'tabs');
    }
}

// Context menu setup for webview
function setupWebviewContextMenu() {
    const webview = document.getElementById('Browser');
    if (webview) {
        // Remove all existing event listeners
        webview.removeEventListener('contextmenu', handleWebviewContextMenu);
        webview.removeEventListener('context-menu', handleWebviewContextMenu);
        
        // Add context menu event listener for webview
        webview.addEventListener('context-menu', (e) => {
            e.preventDefault();
            console.log('Context menu event detected:', e);
            showSimpleContextMenu(e.x || e.clientX || 100, e.y || e.clientY || 100);
        });
        
        // Add regular right-click listener as backup
        webview.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            console.log('Regular contextmenu event:', e);
            showSimpleContextMenu(e.clientX || 100, e.clientY || 100);
        });
        
        // Add mouseup listener for right clicks as another fallback
        webview.addEventListener('mouseup', function(e) {
            if (e.button === 2) { // Right click
                e.preventDefault();
                console.log('Right click detected via mouseup');
                showSimpleContextMenu(e.clientX, e.clientY);
            }
        });
        
        // Disable the default context menu
        webview.addEventListener('contextmenu', (e) => e.preventDefault());
    }
}

function handleWebviewContextMenu(e) {
    e.preventDefault();
    
    // Create a simple HTML context menu
    const existingMenu = document.getElementById('custom-context-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const menu = document.createElement('div');
    menu.id = 'custom-context-menu';
    menu.style.cssText = `
        position: fixed;
        z-index: 10000;
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: 6px;
        box-shadow: var(--shadow-medium);
        padding: 4px 0;
        min-width: 180px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 13px;
        color: var(--text-primary);
        left: ${e.clientX}px;
        top: ${e.clientY}px;
        backdrop-filter: blur(10px);
    `;
    
    const menuItems = [];
    
    // Get context info from the event
    const params = e.params || {};
    const linkURL = params.linkURL || '';
    const srcURL = params.srcURL || '';
    const selectionText = params.selectionText || '';
    const isEditable = params.isEditable || false;
    
    // Add link-specific options
    if (linkURL) {
        menuItems.push({
            label: 'Open Link in New Tab',
            action: () => {
                createNewTab(linkURL, getPageTitle(linkURL));
            }
        });
        
        menuItems.push({
            label: 'Open Link in New Window',
            action: () => {
                // For now, open in new tab (can be enhanced later)
                createNewTab(linkURL, getPageTitle(linkURL));
            }
        });
        
        menuItems.push({ type: 'separator' });
    }
    
    // Add copy option if text is selected
    if (selectionText) {
        menuItems.push({
            label: 'Copy',
            action: () => {
                const { clipboard } = require('electron');
                clipboard.writeText(selectionText);
            }
        });
    } else {
        // Always show copy option
        menuItems.push({
            label: 'Copy',
            action: () => {
                const webview = document.getElementById('Browser');
                if (webview) {
                    webview.copy();
                }
            }
        });
    }
    
    // Add paste option
    menuItems.push({
        label: 'Paste',
        action: () => {
            const webview = document.getElementById('Browser');
            if (webview) {
                webview.paste();
            }
        }
    });
    
    menuItems.push({ type: 'separator' });
    
    // Add inspect element
    menuItems.push({
        label: 'Inspect Element',
        action: () => {
            const webview = document.getElementById('Browser');
            if (webview) {
                webview.openDevTools();
            }
        }
    });
    
    // Add save image option for images
    if (srcURL) {
        menuItems.push({
            label: 'Save Image As',
            action: () => {
                // Create a temporary link to download the image
                const link = document.createElement('a');
                link.href = srcURL;
                link.download = srcURL.split('/').pop() || 'image';
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        });
    }
    
    // Build the menu
    menuItems.forEach(item => {
        if (item.type === 'separator') {
            const separator = document.createElement('div');
            separator.style.cssText = 'height: 1px; background: var(--border-light); margin: 4px 8px;';
            menu.appendChild(separator);
        } else {
            const menuItem = document.createElement('div');
            menuItem.textContent = item.label;
            menuItem.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                transition: background-color 0.1s ease;
            `;
            
            menuItem.addEventListener('mouseenter', () => {
                menuItem.style.backgroundColor = 'var(--bg-button-hover)';
            });
            
            menuItem.addEventListener('mouseleave', () => {
                menuItem.style.backgroundColor = 'transparent';
            });
            
            menuItem.addEventListener('click', () => {
                item.action();
                menu.remove();
            });
            
            menu.appendChild(menuItem);
        }
    });
    
    document.body.appendChild(menu);
    
    // Position the menu to stay within viewport
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
        menu.style.left = (e.clientX - rect.width) + 'px';
    }
    if (rect.bottom > window.innerHeight) {
        menu.style.top = (e.clientY - rect.height) + 'px';
    }
    
    // Remove menu on click elsewhere
    const removeMenu = (event) => {
        if (!menu.contains(event.target)) {
            menu.remove();
            document.removeEventListener('click', removeMenu);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    
    const escapeHandler = (event) => {
        if (event.key === 'Escape') {
            menu.remove();
            document.removeEventListener('click', removeMenu);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    
    // Add event listeners after a short delay to prevent immediate closure
    setTimeout(() => {
        document.addEventListener('click', removeMenu);
        document.addEventListener('keydown', escapeHandler);
    }, 10);
}

// Simple context menu that always appears on right-click
function showSimpleContextMenu(x, y) {
    // Remove existing menu
    const existingMenu = document.getElementById('simple-context-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const menu = document.createElement('div');
    menu.id = 'simple-context-menu';
    menu.style.cssText = `
        position: fixed;
        z-index: 10000;
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: 6px;
        box-shadow: var(--shadow-medium);
        padding: 4px 0;
        min-width: 180px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 13px;
        color: var(--text-primary);
        left: ${x}px;
        top: ${y}px;
        backdrop-filter: blur(10px);
    `;
    
    const menuItems = [
        {
            label: 'Copy',
            action: () => {
                const webview = document.getElementById('Browser');
                if (webview) {
                    webview.copy();
                }
            }
        },
        {
            label: 'Paste',
            action: () => {
                const webview = document.getElementById('Browser');
                if (webview) {
                    webview.paste();
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Reload Page',
            action: () => {
                reloadWebview();
            }
        },
        {
            label: 'Go to Home',
            action: () => {
                goToHome();
            }
        },
        { type: 'separator' },
        {
            label: 'Inspect Element',
            action: () => {
                const webview = document.getElementById('Browser');
                if (webview) {
                    webview.openDevTools();
                }
            }
        }
    ];
    
    // Build the menu
    menuItems.forEach(item => {
        if (item.type === 'separator') {
            const separator = document.createElement('div');
            separator.style.cssText = 'height: 1px; background: var(--border-light); margin: 4px 8px;';
            menu.appendChild(separator);
        } else {
            const menuItem = document.createElement('div');
            menuItem.textContent = item.label;
            menuItem.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                transition: background-color 0.1s ease;
            `;
            
            menuItem.addEventListener('mouseenter', () => {
                menuItem.style.backgroundColor = 'var(--bg-button-hover)';
            });
            
            menuItem.addEventListener('mouseleave', () => {
                menuItem.style.backgroundColor = 'transparent';
            });
            
            menuItem.addEventListener('click', () => {
                item.action();
                menu.remove();
            });
            
            menu.appendChild(menuItem);
        }
    });
    
    document.body.appendChild(menu);
    
    // Position the menu to stay within viewport
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
        menu.style.left = (x - rect.width) + 'px';
    }
    if (rect.bottom > window.innerHeight) {
        menu.style.top = (y - rect.height) + 'px';
    }
    
    // Remove menu on click elsewhere or escape
    const removeMenu = (event) => {
        if (!menu.contains(event.target)) {
            menu.remove();
            document.removeEventListener('click', removeMenu);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    
    const escapeHandler = (event) => {
        if (event.key === 'Escape') {
            menu.remove();
            document.removeEventListener('click', removeMenu);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    
    // Add event listeners after a short delay
    setTimeout(() => {
        document.addEventListener('click', removeMenu);
        document.addEventListener('keydown', escapeHandler);
    }, 10);
}

// Auto-save session periodically
setInterval(saveBrowserSession, 30000); // Save every 30 seconds

// Advanced context menu that detects links and handles different contexts
function showAdvancedContextMenu(x, y, webview) {
    // Remove existing menu
    const existingMenu = document.getElementById('advanced-context-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const menu = document.createElement('div');
    menu.id = 'advanced-context-menu';
    menu.style.cssText = `
        position: fixed;
        z-index: 10000;
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: 6px;
        box-shadow: var(--shadow-medium);
        padding: 4px 0;
        min-width: 200px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 13px;
        color: var(--text-primary);
        left: ${x}px;
        top: ${y}px;
        backdrop-filter: blur(10px);
    `;
    
    // Get the webview's position to check if we can get context info
    const webviewRect = webview.getBoundingClientRect();
    const relativeX = x - webviewRect.left;
    const relativeY = y - webviewRect.top;
    
    // Try to get selection text or other context from the webview
    let hasSelection = false;
    let currentUrl = '';
    
    try {
        // Get current URL
        currentUrl = webview.getURL() || '';
        
        // Check if there's selected text (simplified detection)
        webview.executeJavaScript(`
            (function() {
                const selection = window.getSelection();
                const selectedText = selection.toString().trim();
                const targetElement = document.elementFromPoint(${relativeX}, ${relativeY});
                let linkUrl = '';
                let imageUrl = '';
                
                // Check if clicked element or its parent is a link
                let element = targetElement;
                while (element && element !== document.body) {
                    if (element.tagName === 'A' && element.href) {
                        linkUrl = element.href;
                        break;
                    }
                    element = element.parentElement;
                }
                
                // Check if clicked element is an image
                if (targetElement && targetElement.tagName === 'IMG' && targetElement.src) {
                    imageUrl = targetElement.src;
                }
                
                return {
                    selectedText: selectedText,
                    linkUrl: linkUrl,
                    imageUrl: imageUrl,
                    hasSelection: selectedText.length > 0
                };
            })()
        `).then(result => {
            // Update menu with context info
            updateContextMenuWithInfo(menu, result, webview);
        }).catch(() => {
            // Fallback: show basic menu
            buildBasicContextMenu(menu, webview);
        });
    } catch (error) {
        console.log('Error getting webview context:', error);
        buildBasicContextMenu(menu, webview);
    }
    
    // Initially show basic menu, will be updated if we get context info
    buildBasicContextMenu(menu, webview);
    
    document.body.appendChild(menu);
    
    // Position the menu to stay within viewport
    const rect = menu.getBoundingClientRect();
    let finalX = x;
    let finalY = y;
    
    if (rect.right > window.innerWidth) {
        finalX = x - rect.width;
    }
    if (rect.bottom > window.innerHeight) {
        finalY = y - rect.height;
    }
    
    menu.style.left = finalX + 'px';
    menu.style.top = finalY + 'px';
    
    // Remove menu on click elsewhere or escape
    const removeMenu = (event) => {
        if (!menu.contains(event.target)) {
            menu.remove();
            document.removeEventListener('click', removeMenu);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    
    const escapeHandler = (event) => {
        if (event.key === 'Escape') {
            menu.remove();
            document.removeEventListener('click', removeMenu);
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    
    // Add event listeners after a short delay
    setTimeout(() => {
        document.addEventListener('click', removeMenu);
        document.addEventListener('keydown', escapeHandler);
    }, 10);
}

function updateContextMenuWithInfo(menu, contextInfo, webview) {
    // Clear existing menu items
    while (menu.firstChild) {
        menu.removeChild(menu.firstChild);
    }
    
    const menuItems = [];
    
    // Add link-specific options if there's a link
    if (contextInfo.linkUrl) {
        menuItems.push({
            label: 'Open Link in New Tab',
            action: () => {
                createNewTab(contextInfo.linkUrl, getPageTitle(contextInfo.linkUrl));
            }
        });
        
        menuItems.push({
            label: 'Open Link in New Window',
            action: () => {
                if (window.electronAPI && window.electronAPI.openNewWindow) {
                    window.electronAPI.openNewWindow(contextInfo.linkUrl);
                } else {
                    // Fallback: open in new tab
                    createNewTab(contextInfo.linkUrl, getPageTitle(contextInfo.linkUrl));
                }
            }
        });
        
        menuItems.push({
            label: 'Copy Link Address',
            action: () => {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(contextInfo.linkUrl);
                } else {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = contextInfo.linkUrl;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                }
            }
        });
        
        menuItems.push({ type: 'separator' });
    }
    
    // Add copy option based on selection
    if (contextInfo.hasSelection && contextInfo.selectedText) {
        menuItems.push({
            label: 'Copy',
            action: () => {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(contextInfo.selectedText);
                } else {
                    webview.copy();
                }
            }
        });
    } else {
        menuItems.push({
            label: 'Copy',
            action: () => {
                webview.copy();
            }
        });
    }
    
    // Add paste option
    menuItems.push({
        label: 'Paste',
        action: () => {
            webview.paste();
        }
    });
    
    menuItems.push({ type: 'separator' });
    
    // Add image-specific options if there's an image
    if (contextInfo.imageUrl) {
        menuItems.push({
            label: 'Save Image As',
            action: () => {
                // Create a temporary link to download the image
                const link = document.createElement('a');
                link.href = contextInfo.imageUrl;
                link.download = contextInfo.imageUrl.split('/').pop() || 'image';
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        });
        
        menuItems.push({
            label: 'Copy Image Address',
            action: () => {
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(contextInfo.imageUrl);
                } else {
                    // Fallback
                    const textArea = document.createElement('textarea');
                    textArea.value = contextInfo.imageUrl;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                }
            }
        });
        
        menuItems.push({ type: 'separator' });
    }
    
    // Add common options
    menuItems.push({
        label: 'Reload Page',
        action: () => {
            reloadWebview();
        }
    });
    
    menuItems.push({
        label: 'Go to Home',
        action: () => {
            goToHome();
        }
    });
    
    menuItems.push({ type: 'separator' });
    
    menuItems.push({
        label: 'Inspect Element',
        action: () => {
            webview.openDevTools();
        }
    });
    
    // Build the menu
    buildMenuItems(menu, menuItems);
}

function buildBasicContextMenu(menu, webview) {
    // Clear existing menu items
    while (menu.firstChild) {
        menu.removeChild(menu.firstChild);
    }
    
    const menuItems = [
        {
            label: 'Copy',
            action: () => {
                webview.copy();
            }
        },
        {
            label: 'Paste',
            action: () => {
                webview.paste();
            }
        },
        { type: 'separator' },
        {
            label: 'Reload Page',
            action: () => {
                reloadWebview();
            }
        },
        {
            label: 'Go to Home',
            action: () => {
                goToHome();
            }
        },
        { type: 'separator' },
        {
            label: 'Inspect Element',
            action: () => {
                webview.openDevTools();
            }
        }
    ];
    
    buildMenuItems(menu, menuItems);
}

function buildMenuItems(menu, menuItems) {
    menuItems.forEach(item => {
        if (item.type === 'separator') {
            const separator = document.createElement('div');
            separator.style.cssText = 'height: 1px; background: var(--border-light); margin: 4px 8px;';
            menu.appendChild(separator);
        } else {
            const menuItem = document.createElement('div');
            menuItem.textContent = item.label;
            menuItem.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                transition: background-color 0.1s ease;
                user-select: none;
            `;
            
            menuItem.addEventListener('mouseenter', () => {
                menuItem.style.backgroundColor = 'var(--bg-button-hover)';
            });
            
            menuItem.addEventListener('mouseleave', () => {
                menuItem.style.backgroundColor = 'transparent';
            });
            
            menuItem.addEventListener('click', () => {
                item.action();
                menu.remove();
            });
            
            menu.appendChild(menuItem);
        }
    });
}

// Working context menu with proper clipboard functionality
function showWorkingContextMenu(x, y, webview) {
    console.log('Creating working context menu at:', x, y);
    
    // Remove any existing context menus
    const existingMenus = document.querySelectorAll('[id*="context-menu"]');
    existingMenus.forEach(menu => menu.remove());
    
    const menu = document.createElement('div');
    menu.id = 'working-context-menu';
    menu.style.cssText = `
        position: fixed;
        left: ${x}px;
        top: ${y}px;
        z-index: 999999;
        background: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        padding: 4px 0;
        min-width: 200px;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 13px;
        color: #333333;
        user-select: none;
    `;
    
    // Check if we're in dark mode and adjust colors
    if (document.body.classList.contains('dark-theme')) {
        menu.style.background = '#2d2d2d';
        menu.style.color = '#ffffff';
        menu.style.borderColor = '#555555';
    }
    
    // Get context information from webview
    const webviewRect = webview.getBoundingClientRect();
    const relativeX = x - webviewRect.left;
    const relativeY = y - webviewRect.top;
    
    // First, create basic menu items
    const menuItems = [
        {
            label: 'Copy',
            action: async () => {
                try {
                    // Try to get selected text from webview
                    const selectedText = await webview.executeJavaScript('window.getSelection().toString()');
                    if (selectedText && selectedText.trim()) {
const { clipboard } = require('electron');
                        clipboard.writeText(selectedText);
                        console.log('Copied selected text:', selectedText);
                    } else {
                        // Use webview's built-in copy if no selection
                        webview.copy();
                        console.log('Used webview copy');
                    }
                } catch (error) {
                    console.log('Copy error:', error);
                    // Fallback to webview copy
                    webview.copy();
                }
            }
        },
        {
            label: 'Paste',
            action: async () => {
                try {
                    const { clipboard } = require('electron');
                    const clipboardText = clipboard.readText();
                    if (clipboardText) {
                        // Try inserting text at current cursor position in webview
                        await webview.executeJavaScript(`
                            document.execCommand('insertText', false, ${JSON.stringify(clipboardText)})
                        `);
                        console.log('Pasted text:', clipboardText);
                    }
                } catch (error) {
                    console.log('Paste error:', error);
                    // Fallback to webview paste
                    webview.paste();
                }
            }
        },
        { type: 'separator' },
        {
            label: 'Reload Page',
            action: () => {
                reloadWebview();
            }
        },
        {
            label: 'Go to Home',
            action: () => {
                goToHome();
            }
        },
        { type: 'separator' },
        {
            label: 'Inspect Element',
            action: () => {
                webview.openDevTools();
            }
        }
    ];
    
    // Try to get more context (links, images) asynchronously
    webview.executeJavaScript(`
        (function() {
            try {
                const targetElement = document.elementFromPoint(${relativeX}, ${relativeY});
                let linkUrl = '';
                let imageUrl = '';
                let selectedText = window.getSelection().toString().trim();
                
                // Check for link
                let element = targetElement;
                while (element && element !== document.body) {
                    if (element.tagName === 'A' && element.href) {
                        linkUrl = element.href;
                        break;
                    }
                    element = element.parentElement;
                }
                
                // Check for image
                if (targetElement && targetElement.tagName === 'IMG' && targetElement.src) {
                    imageUrl = targetElement.src;
                }
                
                return {
                    linkUrl: linkUrl,
                    imageUrl: imageUrl,
                    selectedText: selectedText,
                    hasSelection: selectedText.length > 0
                };
            } catch (e) {
                console.error('Error getting context:', e);
                return { linkUrl: '', imageUrl: '', selectedText: '', hasSelection: false };
            }
        })()
    `).then(contextInfo => {
        // Update menu with context-specific options
        updateMenuWithContext(menu, contextInfo, menuItems, webview);
    }).catch(() => {
        // Just build the basic menu
        buildMenuFromItems(menu, menuItems);
    });
    
    // Build basic menu initially
    buildMenuFromItems(menu, menuItems);
    
    document.body.appendChild(menu);
    
    // Position menu properly within viewport
    const rect = menu.getBoundingClientRect();
    let adjustedX = x;
    let adjustedY = y;
    
    if (rect.right > window.innerWidth) {
        adjustedX = x - rect.width;
    }
    if (rect.bottom > window.innerHeight) {
        adjustedY = y - rect.height;
    }
    
    menu.style.left = adjustedX + 'px';
    menu.style.top = adjustedY + 'px';
    
    // Add click-outside listener to close menu
    const closeMenu = (event) => {
        if (!menu.contains(event.target)) {
            menu.remove();
            document.removeEventListener('click', closeMenu);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    
    const handleEscape = (event) => {
        if (event.key === 'Escape') {
            menu.remove();
            document.removeEventListener('click', closeMenu);
            document.removeEventListener('keydown', handleEscape);
        }
    };
    
    // Add listeners after a brief delay to prevent immediate closure
    setTimeout(() => {
        document.addEventListener('click', closeMenu);
        document.addEventListener('keydown', handleEscape);
    }, 50);
}

function updateMenuWithContext(menu, contextInfo, basicItems, webview) {
    // Clear existing items
    while (menu.firstChild) {
        menu.removeChild(menu.firstChild);
    }
    
    const menuItems = [];
    
    // Add link-specific options
    if (contextInfo.linkUrl) {
        menuItems.push({
            label: 'Open Link in New Tab',
            action: () => {
                createNewTab(contextInfo.linkUrl, getPageTitle(contextInfo.linkUrl));
            }
        });
        
        menuItems.push({
            label: 'Open Link in New Window',
            action: () => {
                if (window.electronAPI && window.electronAPI.openNewWindow) {
                    window.electronAPI.openNewWindow(contextInfo.linkUrl);
                } else {
                    createNewTab(contextInfo.linkUrl, getPageTitle(contextInfo.linkUrl));
                }
            }
        });
        
        menuItems.push({
            label: 'Copy Link Address',
            action: async () => {
                try {
                    await navigator.clipboard.writeText(contextInfo.linkUrl);
                    console.log('Copied link:', contextInfo.linkUrl);
                } catch (error) {
                    console.log('Failed to copy link:', error);
                }
            }
        });
        
        menuItems.push({ type: 'separator' });
    }
    
    // Add enhanced copy option
    if (contextInfo.hasSelection && contextInfo.selectedText) {
        menuItems.push({
            label: `Copy "${contextInfo.selectedText.substring(0, 30)}${contextInfo.selectedText.length > 30 ? '...' : ''}"`,
            action: async () => {
                try {
                    await navigator.clipboard.writeText(contextInfo.selectedText);
                    console.log('Copied selected text:', contextInfo.selectedText);
                } catch (error) {
                    console.log('Failed to copy selection:', error);
                }
            }
        });
    } else {
        menuItems.push(basicItems[0]); // Regular copy
    }
    
    // Add paste
    menuItems.push(basicItems[1]);
    
    // Add image options
    if (contextInfo.imageUrl) {
        menuItems.push({ type: 'separator' });
        menuItems.push({
            label: 'Save Image As',
            action: () => {
                const link = document.createElement('a');
                link.href = contextInfo.imageUrl;
                link.download = contextInfo.imageUrl.split('/').pop() || 'image';
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        });
        
        menuItems.push({
            label: 'Copy Image Address',
            action: async () => {
                try {
                    await navigator.clipboard.writeText(contextInfo.imageUrl);
                    console.log('Copied image URL:', contextInfo.imageUrl);
                } catch (error) {
                    console.log('Failed to copy image URL:', error);
                }
            }
        });
    }
    
    // Add remaining basic items
    menuItems.push({ type: 'separator' });
    menuItems.push(basicItems[3]); // Reload
    menuItems.push(basicItems[4]); // Home
    menuItems.push({ type: 'separator' });
    menuItems.push(basicItems[6]); // Inspect
    
    buildMenuFromItems(menu, menuItems);
}

function buildMenuFromItems(menu, items) {
    items.forEach(item => {
        if (item.type === 'separator') {
            const separator = document.createElement('div');
            separator.style.cssText = `
                height: 1px;
                background: ${document.body.classList.contains('dark-theme') ? '#555555' : '#e0e0e0'};
                margin: 4px 8px;
            `;
            menu.appendChild(separator);
        } else {
            const menuItem = document.createElement('div');
            menuItem.textContent = item.label;
            menuItem.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                transition: background-color 0.1s ease;
                user-select: none;
            `;
            
            const isDark = document.body.classList.contains('dark-theme');
            
            menuItem.addEventListener('mouseenter', () => {
                menuItem.style.backgroundColor = isDark ? '#444444' : '#f0f0f0';
            });
            
            menuItem.addEventListener('mouseleave', () => {
                menuItem.style.backgroundColor = 'transparent';
            });
            
            menuItem.addEventListener('click', (e) => {
                e.stopPropagation();
                item.action();
                menu.remove();
            });
            
            menu.appendChild(menuItem);
        }
    });
}

// Save session before closing
window.addEventListener('beforeunload', () => {
    saveBrowserSession();
});



