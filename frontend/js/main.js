// 主入口（事件绑定、初始化、流式处理）
console.log('=== main.js 已加载 ===');

// 获取 DOM 元素
const sendBtn = document.getElementById('sendBtn');
const userInput = document.getElementById('userInput');
const messages = document.getElementById('messages');
const resizer = document.getElementById('resizer');
const sidebar = document.getElementById('sidebar');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const loginOverlay = document.getElementById('loginOverlay');
const loginBtn = document.getElementById('loginBtn');
const loginUsername = document.getElementById('loginUsername');
const loginPassword = document.getElementById('loginPassword');
const loginError = document.getElementById('loginError');
const profileUsername = document.getElementById('profileUsername');
const sessionList = document.getElementById('sessionList');
const newSessionBtn = document.getElementById('newSessionBtn');
const ragToggle = document.getElementById('ragToggle');

// 发送按钮
if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
    console.log('✅ sendBtn 绑定');
}

// 输入框回车
if (userInput) {
    userInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
}

// 侧边栏拖拽
if (resizer && sidebar) {
    let isDragging = false;
    let startX = 0, startWidth = 0;
    resizer.addEventListener('mousedown', function (e) {
        isDragging = true;
        startX = e.clientX;
        startWidth = sidebar.getBoundingClientRect().width;
    });
    document.addEventListener('mousemove', function (e) {
        if (!isDragging) return;
        const delta = e.clientX - startX;
        let newWidth = startWidth + delta;
        if (newWidth < 180) newWidth = 180;
        if (newWidth > 400) newWidth = 400;
        sidebar.style.width = newWidth + 'px';
    });
    document.addEventListener('mouseup', function () {
        isDragging = false;
    });
}

// 登录遮罩回车
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && loginOverlay && !loginOverlay.classList.contains('hidden')) {
        if (loginBtn) loginBtn.click();
    }
});

// 用户菜单
const menuTrigger = document.querySelector('.menu-trigger');
const profile = document.querySelector('.user-profile');
if (menuTrigger && profile) {
    menuTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        profile.classList.toggle('active');
    });
    document.addEventListener('click', () => {
        profile.classList.remove('active');
    });
}

// 退出登录
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', function () {
        localStorage.removeItem('chat_token');
        localStorage.removeItem('chat_username');
        CONFIG.token = null;
        if (profileUsername) profileUsername.textContent = '用户名';
        if (messages) messages.innerHTML = '';
        if (sessionList) sessionList.innerHTML = '';
        currentSessionId = null;
        sessions = [];
        if (loginOverlay) loginOverlay.classList.remove('hidden');
        if (profile) profile.classList.remove('active');
        console.log('已退出登录');
    });
}

// 上传按钮（已在 api.js 中绑定，避免重复）

// 自动登录检查
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOMContentLoaded, token:', CONFIG.token);
    if (CONFIG.token) {
        if (loginOverlay) loginOverlay.classList.add('hidden');
        try {
            await loadSessions();
            if (sessions.length > 0) {
                currentSessionId = sessions[0].id;
                renderSessionList();
                await loadMessages(currentSessionId);
                // 更新模式指示
                const cur = sessions.find(s => s.id === currentSessionId);
                if (cur) {
                    const ragToggle = document.getElementById('ragToggle');
                    const modeIndicator = document.getElementById('modeIndicator');
                    if (ragToggle) ragToggle.checked = (cur.mode === 'rag');
                    if (modeIndicator) {
                        modeIndicator.textContent = cur.mode === 'rag' ? '模式: RAG 知识库' : '模式: 正常对话';
                        modeIndicator.style.color = cur.mode === 'rag' ? '#2563eb' : '#64748b';
                    }
                }
            } else {
                // 无会话，自动创建默认会话（模式为chat）
                console.warn('无会话，自动创建默认会话');
                await createDefaultSession();
            }
            const savedUsername = localStorage.getItem('chat_username');
            if (savedUsername && profileUsername) {
                profileUsername.textContent = savedUsername;
            }
            loadDocList().catch(e => console.warn('加载文档列表失败:', e));
        } catch (error) {
            console.error('自动登录失败:', error);
            localStorage.removeItem('chat_token');
            localStorage.removeItem('chat_username');
            if (loginOverlay) loginOverlay.classList.remove('hidden');
        }
    } else {
        console.log('无 token，显示登录');
    }
});

// 辅助：创建默认会话（chat模式）
async function createDefaultSession() {
    try {
        const response = await fetch('/sessions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${CONFIG.token}`
            },
            body: JSON.stringify({ name: '默认会话' })
        });
        if (!response.ok) throw new Error('创建默认会话失败');
        const newSession = await response.json();
        newSession.mode = 'chat';
        sessions.push(newSession);
        renderSessionList();
        currentSessionId = newSession.id;
        highlightSession(currentSessionId);
        // 更新模式指示
        const ragToggle = document.getElementById('ragToggle');
        const modeIndicator = document.getElementById('modeIndicator');
        if (ragToggle) ragToggle.checked = false;
        if (modeIndicator) {
            modeIndicator.textContent = '模式: 正常对话';
            modeIndicator.style.color = '#64748b';
        }
        console.log('默认会话创建成功');
    } catch (error) {
        console.error('创建默认会话出错:', error);
    }
}

// ===== 发送消息（流式） =====
async function sendMessage() {
    console.log('📤 sendMessage, currentSessionId:', currentSessionId);
    if (!currentSessionId) {
        alert('请先选择一个会话（点击左侧会话列表）');
        return;
    }

    // ============================================================
    // ✅ 改动点：直接从 sessions 数组中读取当前会话的模式
    // 不再依赖 checkbox 状态，避免不同步导致的 bug
    const currentSession = sessions.find(s => s.id === currentSessionId);
    if (!currentSession) {
        alert('当前会话不存在，请刷新重试');
        return;
    }
    // 根据会话存储的模式决定走哪条路
    const useRAG = (currentSession.mode === 'rag');
    // ============================================================

    const text = userInput ? userInput.value.trim() : '';
    if (!text) {
        alert('请输入消息！');
        return;
    }

    addMessage(text, 'user');
    if (userInput) userInput.value = '';

    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.textContent = '发送中...';
    }

    try {
        let endpoint, requestData;
        if (useRAG) {
            endpoint = '/rag/ask/stream';
            // 后端接收的是 RAGRequest，字段为 message
            requestData = { message: text };
        } else {
            endpoint = '/chat/stream';
            requestData = {
                session_id: currentSessionId,
                message: text
            };
        }
        console.log(`📡 路由到 ${endpoint}，数据:`, requestData);

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${CONFIG.token}`
            },
            body: JSON.stringify(requestData)
        };

        const response = await fetch(endpoint, options);
        if (!handleAuthError(response.status)) return;

        if (!response.ok) {
            const errorData = await response.json();
            alert('请求失败: ' + (errorData.detail || response.statusText));
            return;
        }

        const aiDiv = addMessage('', 'assistant');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const content = line.slice(6);
                    if (content === '[DONE]') {
                        console.log('流式传输结束');
                    } else if (content.startsWith('[ERROR]')) {
                        aiDiv.textContent += content;
                    } else if (content.startsWith('__SOURCES__:')) {
                        const sourcesStr = content.slice('__SOURCES__:'.length);
                        try {
                            const sources = JSON.parse(sourcesStr);
                            if (sources.length > 0) {
                                const sourceDiv = document.createElement('div');
                                sourceDiv.className = 'source-citation';
                                sourceDiv.textContent = '📚 参考来源: ' + sources.join(', ');
                                aiDiv.appendChild(sourceDiv);
                            }
                        } catch (e) { /* ignore */ }
                    } else {
                        aiDiv.textContent += content;
                    }
                    scrollToBottomIfNeeded();
                }
            }
        }
    } catch (error) {
        addMessage('⚠️ 出错了：' + error.message, 'assistant');
        console.error('发送失败:', error);
    } finally {
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
        }
    }
}