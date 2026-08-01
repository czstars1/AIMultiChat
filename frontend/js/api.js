// 网络请求层

// ---------- 认证处理 ----------
function handleAuthError(status) {
    if (status === 403) {
        alert('登录已过期或无权访问，请重新登录');
        localStorage.removeItem('chat_token');
        localStorage.removeItem('chat_username');
        CONFIG.token = null;
        const overlay = document.getElementById('loginOverlay');
        if (overlay) overlay.classList.remove('hidden');
        return false;
    }
    return true;
}

// ---------- 加载会话 ----------
async function loadSessions() {
    try {
        const response = await fetch('/sessions', {
            headers: { 'Authorization': `Bearer ${CONFIG.token}` }
        });
        if (!handleAuthError(response.status)) return;
        if (!response.ok) throw new Error('获取会话列表失败');
        const data = await response.json();
        // 如果后端没有返回 mode，默认为 'chat'
        sessions = data.map(s => ({ ...s, mode: s.mode || 'chat' }));
        renderSessionList();
        // 如果有当前会话，更新模式指示
        if (currentSessionId) {
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
        }
    } catch (error) {
        console.error('加载会话出错:', error);
        alert('无法加载会话列表，请检查后端服务');
    }
}

// ---------- 加载消息 ----------
async function loadMessages(sessionId) {
    try {
        const response = await fetch(`/chat/${sessionId}/messages`, {
            headers: { 'Authorization': `Bearer ${CONFIG.token}` }
        });
        if (!handleAuthError(response.status)) return;
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        if (!Array.isArray(data)) {
            console.error('[loadMessages] 数据不是数组，内容:', data);
            return;
        }
        data.forEach((msg) => {
            addMessage(msg.content, msg.role);
        });
        messages.scrollTop = messages.scrollHeight;
    } catch (error) {
        console.error('[loadMessages] 异常:', error);
        addMessage('⚠️ 加载历史消息失败: ' + error.message, 'assistant');
    }
}

// ---------- 创建会话（带模式选择） ----------
document.getElementById('newSessionBtn').addEventListener('click', () => {
    // 显示模式选择弹窗
    document.getElementById('modeModal').classList.remove('hidden');
});

// 模式选择按钮事件
document.querySelectorAll('.mode-option').forEach(btn => {
    btn.addEventListener('click', async (e) => {
        const mode = e.target.dataset.mode;
        document.getElementById('modeModal').classList.add('hidden');
        // 弹出命名对话框
        const name = prompt('请输入会话名称', mode === 'rag' ? '知识库问答' : '新对话');
        if (name === null) return;
        try {
            const response = await fetch('/sessions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${CONFIG.token}`
                },
                body: JSON.stringify({ name: name || '未命名会话' })
            });
            if (!handleAuthError(response.status)) return;
            if (!response.ok) throw new Error('会话创建失败');
            const newSession = await response.json();
            // 存储模式到前端（后端未存，这里暂存）
            newSession.mode = mode;
            sessions.push(newSession);
            renderSessionList();
            currentSessionId = newSession.id;
            highlightSession(currentSessionId);
            messages.innerHTML = '';
            // 更新模式指示
            const ragToggle = document.getElementById('ragToggle');
            const modeIndicator = document.getElementById('modeIndicator');
            if (ragToggle) ragToggle.checked = (mode === 'rag');
            if (modeIndicator) {
                modeIndicator.textContent = mode === 'rag' ? '模式: RAG 知识库' : '模式: 正常对话';
                modeIndicator.style.color = mode === 'rag' ? '#2563eb' : '#64748b';
            }
            console.log('新建会话成功：', newSession);
        } catch (error) {
            alert('创建会话失败：' + error.message);
        }
    });
});

document.getElementById('modalCancelBtn').addEventListener('click', () => {
    document.getElementById('modeModal').classList.add('hidden');
});

// ---------- 删除会话 ----------
async function deleteSession(sessionId) {
    try {
        const response = await fetch(`/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${CONFIG.token}` }
        });
        if (!handleAuthError(response.status)) return;
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`删除失败 (${response.status}): ${errorText}`);
        }
        // 从本地 sessions 中移除
        sessions = sessions.filter(s => s.id !== sessionId);
        renderSessionList();
        if (currentSessionId === sessionId) {
            currentSessionId = null;
            messages.innerHTML = '';
        }
        if (sessions.length > 0) {
            currentSessionId = sessions[0].id;
            highlightSession(currentSessionId);
            // 自动加载消息并更新模式
            loadMessages(currentSessionId);
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
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}

// ---------- 登录 ----------
document.getElementById('loginBtn').addEventListener('click', async () => {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value.trim();
    const loginError = document.getElementById('loginError');

    if (!username || !password) {
        loginError.textContent = '⚠️ 账号和密码不能为空';
        return;
    }

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: username, password })
        });

        if (!response.ok) {
            const err = await response.json();
            let errorMsg = '登录失败';
            if (err.detail) {
                if (Array.isArray(err.detail)) {
                    errorMsg = err.detail.map(item => item.msg).join('；');
                } else if (typeof err.detail === 'string') {
                    errorMsg = err.detail;
                } else {
                    errorMsg = JSON.stringify(err.detail);
                }
            }
            loginError.textContent = '❌ ' + errorMsg;
            return;
        }

        const data = await response.json();
        const token = data.token;
        CONFIG.token = token;
        localStorage.setItem('chat_token', token);
        localStorage.setItem('chat_username', username);

        document.getElementById('loginOverlay').classList.add('hidden');
        document.getElementById('profileUsername').textContent = username;
        await loadSessions();
        if (sessions.length > 0) {
            currentSessionId = sessions[0].id;
            highlightSession(currentSessionId);
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
        }
        // 加载文档列表（如果存在）
        loadDocList();
    } catch (error) {
        document.getElementById('loginError').textContent = '⚠️ 网络请求失败，请检查后端';
    }
});

// ---------- 上传文件 ----------
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch('/rag/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${CONFIG.token}` },
            body: formData
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            loadDocList();
        } else {
            alert('上传失败: ' + data.detail);
        }
    } catch (err) {
        alert('网络错误: ' + err.message);
    }
    e.target.value = '';
});

// ---------- 加载文档列表 ----------
async function loadDocList() {
    const docListSpan = document.getElementById('docList');
    if (!docListSpan) return;
    try {
        const res = await fetch('/rag/docs', {
            headers: { 'Authorization': `Bearer ${CONFIG.token}` }
        });
        if (res.ok) {
            const data = await res.json();
            if (data.length > 0) {
                docListSpan.textContent = '📄 ' + data.map(d => d.filename).join(', ');
            } else {
                docListSpan.textContent = '📄 暂无文档';
            }
        } else {
            docListSpan.textContent = '📄 已上传文档（可刷新）';
        }
    } catch {
        docListSpan.textContent = '📄 已上传文档（可刷新）';
    }
}