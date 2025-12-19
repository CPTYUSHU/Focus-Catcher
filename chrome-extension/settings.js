// Focus Catcher - Settings Script

// 默认设置
const DEFAULT_SETTINGS = {
  autoCapture: false,
  showToast: true,
  playSound: false,
  autoAnalyze: false,
  analyzeThreshold: 5
};

// 加载设置
async function loadSettings() {
  try {
    const result = await chrome.storage.sync.get('focusCatcherSettings');
    const settings = result.focusCatcherSettings || DEFAULT_SETTINGS;
    
    // 应用设置到界面
    document.getElementById('autoCapture').checked = settings.autoCapture;
    document.getElementById('showToast').checked = settings.showToast;
    document.getElementById('playSound').checked = settings.playSound;
    document.getElementById('autoAnalyze').checked = settings.autoAnalyze;
    document.getElementById('analyzeThreshold').value = settings.analyzeThreshold;
    
    // 获取当前快捷键（从 Chrome API）
    loadCurrentShortcut();
    
    console.log('[Settings] Loaded:', settings);
  } catch (error) {
    console.error('[Settings] Failed to load:', error);
  }
}

// 加载当前快捷键
async function loadCurrentShortcut() {
  try {
    const commands = await chrome.commands.getAll();
    const captureCommand = commands.find(cmd => cmd.name === 'capture-selection');
    
    if (captureCommand && captureCommand.shortcut) {
      document.getElementById('currentShortcut').textContent = captureCommand.shortcut;
    } else {
      document.getElementById('currentShortcut').textContent = '未设置（请点击下方按钮设置）';
    }
  } catch (error) {
    console.error('[Settings] Failed to load shortcut:', error);
    document.getElementById('currentShortcut').textContent = 'Cmd+Shift+C / Ctrl+Shift+C（默认）';
  }
}

// 保存设置
async function saveSettings() {
  const settings = {
    autoCapture: document.getElementById('autoCapture').checked,
    showToast: document.getElementById('showToast').checked,
    playSound: document.getElementById('playSound').checked,
    autoAnalyze: document.getElementById('autoAnalyze').checked,
    analyzeThreshold: parseInt(document.getElementById('analyzeThreshold').value)
  };
  
  try {
    await chrome.storage.sync.set({ focusCatcherSettings: settings });
    console.log('[Settings] Saved:', settings);
    
    // 通知 content script 更新设置
    chrome.tabs.query({}, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          action: 'settings-updated',
          settings: settings
        }).catch(() => {
          // 忽略无法发送消息的标签页
        });
      });
    });
    
    showToast('✅ 设置已保存');
  } catch (error) {
    console.error('[Settings] Failed to save:', error);
    showToast('❌ 保存失败');
  }
}

// 恢复默认设置
async function resetSettings() {
  if (confirm('确定要恢复默认设置吗？')) {
    await chrome.storage.sync.set({ focusCatcherSettings: DEFAULT_SETTINGS });
    await loadSettings();
    showToast('🔄 已恢复默认设置');
  }
}

// 修改快捷键按钮
document.getElementById('changeShortcutBtn').addEventListener('click', () => {
  chrome.tabs.create({ url: 'chrome://extensions/shortcuts' });
  showToast('💡 请在打开的页面中找到 "Focus Catcher" 并修改快捷键');
});

// 保存按钮
document.getElementById('saveBtn').addEventListener('click', saveSettings);

// 重置按钮
document.getElementById('resetBtn').addEventListener('click', resetSettings);

// 显示 Toast
function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// 页面加载时加载设置
loadSettings();

console.log('[Settings] Settings page loaded');

