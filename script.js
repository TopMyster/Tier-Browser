let currentEngine = "Bing";
let searchUrl = "https://www.bing.com/search?q=";
let browserSettings = {
searchEngine: "Bing",
theme: "light",
homepage: "home.html",
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
}

function switchTheme(theme) {
const elements = {
body: document.body,
tabbar: document.getElementById('tabbar'),
searchbar: document.getElementById('searchbar'),
tabs: document.getElementById('tabs')
};

if (theme === 'dark') {
elements.body.style.backgroundColor = 'rgba(30, 30, 30, 0.9)';
elements.body.style.color = 'white';
if (elements.tabbar) elements.tabbar.style.backgroundColor = 'rgba(40, 40, 40, 0.9)';
if (elements.searchbar) {
elements.searchbar.style.backgroundColor = 'rgba(50, 50, 50, 0.9)';
elements.searchbar.style.color = 'white';
}
if (elements.tabs) {
elements.tabs.style.backgroundColor = 'rgba(40, 40, 40, 0.9)';
elements.tabs.style.color = 'white';
}
} else {
elements.body.style.backgroundColor = 'rgba(255, 255, 255, 0.509)';
elements.body.style.color = 'black';
if (elements.tabbar) elements.tabbar.style.backgroundColor = 'rgba(255, 255, 255, 0.793)';
if (elements.searchbar) {
elements.searchbar.style.backgroundColor = 'rgba(255, 255, 255, 0.916)';
elements.searchbar.style.color = 'black';
}
if (elements.tabs) {
elements.tabs.style.backgroundColor = 'rgba(255, 255, 255, 0.793)';
elements.tabs.style.color = 'black';
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
tabsContainer.innerHTML = '<h2 style="margin-top: 10px;">Open Tabs</h2>';

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
if (search.includes('/ch')) {
document.getElementById('searchbar').style.color = 'rgba(0, 124, 82, 1)';
} else {
document.getElementById('searchbar').style.color = 'black';
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
});

window.addEventListener('DOMContentLoaded', function() {
loadUserSettings();
initTabs();
setupEngineSelector();
setupThemeSelector();

const webview = document.getElementById('Browser');
webview.addEventListener('did-navigate', (event) => updateCurrentTabUrl(event.url));
webview.addEventListener('did-navigate-in-page', (event) => updateCurrentTabUrl(event.url));

webview.addEventListener('dom-ready', function() {
setTimeout(() => {
setupEngineSelector();
}, 500);
});

document.addEventListener('click', function(event) {
const tabsElement = document.getElementById('tabs');
const tabButton = document.getElementById('tabbutton');

if (!tabsElement.contains(event.target) && !tabButton.contains(event.target)) {
if (tabsElement.style.display === 'block') {
hidTabs();
}
}
});
});

function openbookmarks() {
document.getElementById('bookmarks').style.display = 'block'
}

function closebookmarks() {
document.getElementById('bookmarks').style.display = 'none'
}

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
    var mainContent = document.getElementById('main-content');
    mainContent.classList.toggle('chat-open');
});
