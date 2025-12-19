// Focus Catcher - Content Script
// 在所有网页中运行，监听文字选中和快捷键

console.log('[Focus Catcher] Content script loaded');

// 当前设置
let settings = {
  autoCapture: false,
  showToast: true,
  playSound: false,
  autoAnalyze: false,
  analyzeThreshold: 5
};

// 加载设置
chrome.storage.sync.get('focusCatcherSettings', (result) => {
  if (result.focusCatcherSettings) {
    settings = { ...settings, ...result.focusCatcherSettings };
    console.log('[Focus Catcher] Settings loaded:', settings);
  }
});

// 监听来自 background 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'capture-selection') {
    captureSelectedText();
  } else if (request.action === 'settings-updated') {
    settings = { ...settings, ...request.settings };
    console.log('[Focus Catcher] Settings updated:', settings);
  } else if (request.action === 'show-toast') {
    // 从 background 接收到显示 Toast 的请求
    if (settings.showToast) {
      showToast(request.message, request.type);
    }
    if (settings.playSound && request.type === 'success') {
      playSuccessSound();
    }
  }
});

// 捕捉选中的文字
function captureSelectedText() {
  const selectedText = window.getSelection().toString().trim();
  
  if (!selectedText) {
    showToast('❌ 请先选中文字', 'error');
    return;
  }

  // 获取页面信息
  const pageInfo = {
    selected_text: selectedText,
    page_url: window.location.href,
    page_title: document.title
  };

  console.log('[Focus Catcher] Capturing:', pageInfo);

  // 发送到 background script
  chrome.runtime.sendMessage({
    action: 'send-to-backend',
    data: pageInfo
  }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('[Focus Catcher] Error:', chrome.runtime.lastError);
      showToast('❌ 捕捉失败', 'error');
      return;
    }

    if (response && response.success) {
      if (settings.showToast) {
        showToast('✅ 已捕捉', 'success');
      }
      if (settings.playSound) {
        playSuccessSound();
      }
      console.log('[Focus Catcher] Capture successful:', response);
    } else {
      if (settings.showToast) {
        showToast('❌ 捕捉失败', 'error');
      }
      console.error('[Focus Catcher] Capture failed:', response);
    }
  });
}

// 显示 Toast 提示
function showToast(message, type = 'info') {
  // 移除已存在的 toast
  const existingToast = document.getElementById('focus-catcher-toast');
  if (existingToast) {
    existingToast.remove();
  }

  // 创建 toast 元素
  const toast = document.createElement('div');
  toast.id = 'focus-catcher-toast';
  toast.className = `focus-catcher-toast focus-catcher-toast-${type}`;
  toast.textContent = message;

  // 添加到页面
  document.body.appendChild(toast);

  // 显示动画
  setTimeout(() => {
    toast.classList.add('focus-catcher-toast-show');
  }, 10);

  // 3 秒后隐藏
  setTimeout(() => {
    toast.classList.remove('focus-catcher-toast-show');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// 双击自动捕捉（如果启用）
document.addEventListener('dblclick', () => {
  if (settings.autoCapture) {
    const selectedText = window.getSelection().toString().trim();
    if (selectedText) {
      setTimeout(() => {
        captureSelectedText();
      }, 100); // 延迟一点，确保文字已选中
    }
  }
});

// 播放成功提示音
function playSuccessSound() {
  const audio = new Audio();
  audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIGGS57OihUBELTKXh8LJnHgU2jdXzzn0vBSl+zPDajz4KFF+16+qnVRQLRp/g8r5sIQUrgs/y2Ik2CBhkuezooVARCw==';
  audio.volume = 0.3;
  audio.play().catch(() => {
    // 忽略播放失败
  });
}

console.log('[Focus Catcher] Ready! Press Cmd+Shift+C to capture selected text.');

