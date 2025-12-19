// Focus Catcher - Popup Script

const API_BASE_URL = 'http://127.0.0.1:8000';

// 加载统计数据
async function loadStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/focus/sessions`);
    const data = await response.json();
    
    // 计算今日数据
    const today = new Date().toDateString();
    const todaySessions = data.sessions.filter(session => {
      const sessionDate = new Date(session.start_time).toDateString();
      return sessionDate === today;
    });
    
    const todayCaptures = todaySessions.reduce((sum, session) => sum + session.capture_count, 0);
    
    document.getElementById('todayCaptures').textContent = todayCaptures;
    document.getElementById('todaySessions').textContent = todaySessions.length;
  } catch (error) {
    console.error('[Focus Catcher] Failed to load stats:', error);
    document.getElementById('todayCaptures').textContent = '?';
    document.getElementById('todaySessions').textContent = '?';
  }
}

// 查看历史记录
document.getElementById('viewHistory').addEventListener('click', () => {
  chrome.tabs.create({ url: `${API_BASE_URL}/test_capture.html` });
});

// 打开设置页面
document.getElementById('openSettings').addEventListener('click', () => {
  chrome.tabs.create({ url: chrome.runtime.getURL('settings.html') });
});

// 页面加载时获取统计数据
loadStats();

