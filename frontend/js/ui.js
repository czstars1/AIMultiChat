// UI 渲染层

function renderSessionList() {
    const list = document.getElementById('sessionList');
    list.innerHTML = '';
    sessions.forEach(session => {
        const li = document.createElement('li');
        li.dataset.id = session.id;

        const nameSpan = document.createElement('span');
        nameSpan.className = 'session-name';
        nameSpan.textContent = session.name || `会话 ${session.id.slice(0, 6)}`;
        li.appendChild(nameSpan);

        // 模式标签
        const modeTag = document.createElement('span');
        modeTag.className = 'session-mode-tag';
        modeTag.textContent = session.mode === 'rag' ? 'RAG' : '对话';
        li.appendChild(modeTag);

        const delBtn = document.createElement('span');
        delBtn.className = 'delete-btn';
        delBtn.textContent = '×';
        delBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (confirm(`确定要删除“${session.name}”吗？`)) {
                await deleteSession(session.id);
            }
        });
        li.appendChild(delBtn);

        li.addEventListener('click', () => switchSession(session.id));

        if (session.id === currentSessionId) {
            li.classList.add('active');
        }
        list.appendChild(li);
    });
}

function addMessage(content, type) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    const icon = type === 'user' ? '👤 ' : '🤖 ';
    msgDiv.innerHTML = icon + content; // 允许包含HTML（来源引用等）
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
    return msgDiv;
}

function scrollToBottomIfNeeded() {
    const threshold = 30;
    const { scrollTop, scrollHeight, clientHeight } = messages;
    if (scrollHeight - scrollTop - clientHeight < threshold) {
        messages.scrollTop = scrollHeight;
    }
}

function highlightSession(sessionId) {
    const items = document.querySelectorAll('#sessionList li');
    items.forEach(li => {
        li.classList.toggle('active', li.dataset.id === sessionId);
    });
}

function switchSession(sessionId) {
    if (sessionId === currentSessionId) return;
    currentSessionId = sessionId;
    highlightSession(sessionId);
    messages.innerHTML = '';
    loadMessages(sessionId);

    // 根据会话模式更新 UI 指示
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
        const ragToggle = document.getElementById('ragToggle');
        const modeIndicator = document.getElementById('modeIndicator');

        if (ragToggle) ragToggle.checked = (session.mode === 'rag');
        if (modeIndicator) {
            if (session.mode === 'rag') {
                modeIndicator.textContent = '🟢 模式: RAG 知识库';
                modeIndicator.style.color = '#2563eb';
            } else {
                modeIndicator.textContent = '🔵 模式: 正常对话';
                modeIndicator.style.color = '#64748b';
            }
        }
        console.log(`切换到会话: ${sessionId}，模式: ${session.mode}`);
    }
}