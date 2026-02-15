/**
 * Popup script for AI Image Detector extension.
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Check backend health
  await checkHealth();

  // Load stats
  await loadStats();

  // Load recent detections
  await loadRecentDetections();

  // Set up event listeners
  document.getElementById('rescanBtn').addEventListener('click', rescanPage);
  document.getElementById('optionsBtn').addEventListener('click', openOptions);
});

async function checkHealth() {
  const statusDot = document.querySelector('.status-dot');
  const statusText = document.querySelector('.status-text');

  try {
    const health = await chrome.runtime.sendMessage({ action: 'checkHealth' });

    if (health.status === 'healthy') {
      statusDot.classList.add('online');
      statusDot.classList.remove('offline');
      statusText.textContent = `Online (${health.device})`;
    } else if (health.status === 'offline') {
      statusDot.classList.add('offline');
      statusDot.classList.remove('online');
      statusText.textContent = 'Offline';
    } else {
      statusDot.classList.remove('online', 'offline');
      statusText.textContent = health.status;
    }
  } catch (error) {
    statusDot.classList.add('offline');
    statusText.textContent = 'Error';
    console.error('Health check failed:', error);
  }
}

async function loadStats() {
  try {
    const stats = await chrome.runtime.sendMessage({ action: 'getStats' });

    document.getElementById('totalAnalyses').textContent = stats.total_analyses || 0;
    document.getElementById('aiDetections').textContent = stats.ai_detections || 0;
    document.getElementById('cacheHitRate').textContent =
      (stats.cache_hit_rate || 0).toFixed(1) + '%';
  } catch (error) {
    console.error('Failed to load stats:', error);
  }
}

async function loadRecentDetections() {
  const container = document.getElementById('recentDetections');

  try {
    const response = await chrome.runtime.sendMessage({ action: 'getRecentDetections' });
    const detections = response.detections || [];

    if (detections.length === 0) {
      container.innerHTML = '<p class="empty-message">No recent detections</p>';
      return;
    }

    container.innerHTML = detections.slice(0, 10).map(detection => {
      const result = detection.result;
      let indicatorClass, indicator;

      if (result.is_ai) {
        indicatorClass = 'ai';
        indicator = '\u2717';
      } else if (result.verdict === 'Uncertain') {
        indicatorClass = 'uncertain';
        indicator = '?';
      } else {
        indicatorClass = 'real';
        indicator = '\u2713';
      }

      const url = detection.imageUrl || 'Unknown';
      const shortUrl = url.length > 40 ? url.substring(0, 37) + '...' : url;

      return `
        <div class="recent-item">
          <div class="recent-item-indicator ${indicatorClass}">${indicator}</div>
          <div class="recent-item-info">
            <div class="recent-item-url" title="${url}">${shortUrl}</div>
            <div class="recent-item-verdict">${result.verdict} (${(result.confidence * 100).toFixed(0)}%)</div>
          </div>
        </div>
      `;
    }).join('');
  } catch (error) {
    console.error('Failed to load recent detections:', error);
    container.innerHTML = '<p class="empty-message">Failed to load detections</p>';
  }
}

async function rescanPage() {
  const btn = document.getElementById('rescanBtn');
  btn.disabled = true;
  btn.textContent = 'Scanning...';

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (tab) {
      await chrome.tabs.sendMessage(tab.id, { action: 'rescan' });
    }

    // Reload detections after a short delay
    setTimeout(async () => {
      await loadRecentDetections();
      btn.disabled = false;
      btn.textContent = 'Rescan Page';
    }, 2000);
  } catch (error) {
    console.error('Rescan failed:', error);
    btn.disabled = false;
    btn.textContent = 'Rescan Page';
  }
}

function openOptions() {
  chrome.runtime.openOptionsPage();
}
