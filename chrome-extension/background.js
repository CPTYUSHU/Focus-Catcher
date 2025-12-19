// Focus Catcher - Background Service Worker
// 处理快捷键和与后端的通信

console.log('[Focus Catcher] Background service worker started');

// API 配置
const API_BASE_URL = 'http://127.0.0.1:8000';

// 创建右键菜单
chrome.runtime.onInstalled.addListener((details) => {
  // 创建右键菜单
  chrome.contextMenus.create({
    id: 'focus-catcher-capture',
    title: '🎯 Focus Catcher - 捕捉选中内容',
    contexts: ['selection']
  });
  console.log('[Focus Catcher] Context menu created');
  
  // 首次安装时的欢迎消息
  if (details.reason === 'install') {
    console.log('[Focus Catcher] Extension installed! 🎉');
    console.log('[Focus Catcher] 使用方法：');
    console.log('[Focus Catcher] 1. 选中文字 → 右键 → Focus Catcher');
    console.log('[Focus Catcher] 2. 或按快捷键（需在 chrome://extensions/shortcuts 设置）');
    
    // 打开设置页面
    chrome.tabs.create({ url: chrome.runtime.getURL('settings.html') });
  }
});

// 监听右键菜单点击
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'focus-catcher-capture') {
    console.log('[Focus Catcher] Context menu clicked');
    console.log('[Focus Catcher] Selected text:', info.selectionText);
    
    // 直接使用右键菜单提供的选中文字
    if (info.selectionText) {
      const captureData = {
        selected_text: info.selectionText,
        page_url: info.pageUrl || tab.url,
        page_title: tab.title
      };
      
      // 直接发送到后端
      sendToBackend(captureData)
        .then(response => {
          console.log('[Focus Catcher] Capture successful from context menu:', response);
          
          // 通知 content script 显示 Toast
          chrome.tabs.sendMessage(tab.id, {
            action: 'show-toast',
            message: '✅ 已捕捉',
            type: 'success'
          }).catch(err => {
            console.log('[Focus Catcher] Could not send toast message:', err);
          });
          
          // 检查是否需要自动触发 AI 分析
          checkAutoAnalyze(response);
        })
        .catch(error => {
          console.error('[Focus Catcher] Capture failed:', error);
          
          // 通知 content script 显示错误
          chrome.tabs.sendMessage(tab.id, {
            action: 'show-toast',
            message: '❌ 捕捉失败',
            type: 'error'
          }).catch(err => {
            console.log('[Focus Catcher] Could not send error toast:', err);
          });
        });
    } else {
      console.error('[Focus Catcher] No text selected');
    }
  }
});

// 监听快捷键命令
chrome.commands.onCommand.addListener((command) => {
  console.log('[Focus Catcher] Command received:', command);
  
  if (command === 'capture-selection') {
    // 向当前活动标签页发送消息
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'capture-selection'
        });
      }
    });
  }
});

// 监听来自 content script 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'send-to-backend') {
    // 发送到 FastAPI 后端
    sendToBackend(request.data)
      .then(response => {
        sendResponse({ success: true, data: response });
        
        // 检查是否需要自动触发 AI 分析
        checkAutoAnalyze(response);
      })
      .catch(error => {
        console.error('[Focus Catcher] Backend error:', error);
        sendResponse({ success: false, error: error.message });
      });
    
    // 返回 true 表示异步响应
    return true;
  }
});

// 发送数据到 FastAPI 后端
async function sendToBackend(data) {
  const url = `${API_BASE_URL}/api/focus/capture`;
  
  console.log('[Focus Catcher] Sending to backend:', url, data);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('[Focus Catcher] Backend response:', result);
    
    return result;
  } catch (error) {
    console.error('[Focus Catcher] Fetch error:', error);
    throw error;
  }
}

// 检查是否需要自动触发 AI 分析
async function checkAutoAnalyze(captureResponse) {
  try {
    // 获取设置
    const result = await chrome.storage.sync.get('focusCatcherSettings');
    const settings = result.focusCatcherSettings || {};
    
    if (!settings.autoAnalyze) {
      return; // 未启用自动分析
    }
    
    const threshold = settings.analyzeThreshold || 5;
    const sessionId = captureResponse.session_id;
    
    // 获取会话信息
    const sessionsResponse = await fetch(`${API_BASE_URL}/api/focus/sessions`);
    const sessionsData = await sessionsResponse.json();
    
    // 找到当前会话
    const currentSession = sessionsData.sessions.find(s => s.id === sessionId);
    
    if (currentSession && currentSession.capture_count >= threshold && currentSession.status !== 'analyzed') {
      console.log(`[Focus Catcher] Auto-triggering AI analysis for session ${sessionId} (${currentSession.capture_count} captures)`);
      
      // 触发 AI 分析
      const analysisResponse = await fetch(`${API_BASE_URL}/api/focus/analyze/${sessionId}`, {
        method: 'POST'
      });
      
      if (analysisResponse.ok) {
        console.log('[Focus Catcher] Auto-analysis completed successfully');
        
        // 显示通知
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon128.png',
          title: 'Focus Catcher',
          message: `✅ 已自动完成 AI 分析（${currentSession.capture_count} 条捕捉）`,
          priority: 1
        });
      }
    }
  } catch (error) {
    console.error('[Focus Catcher] Auto-analyze check failed:', error);
  }
}

// 插件安装/更新时的处理
// 注意：这个监听器已经在文件开头定义了，这里不需要重复

