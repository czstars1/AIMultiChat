// 网络请求层（fetch 封装）



// 0. 检验token
function handleAuthError(status){
    if(status===403){
        alert('登录已过期或无权访问，请重新登录');
        //跳转登陆界面
        return false;
    }
    return true;
}

// 1. 加载会话列表
async function loadSessions(){
    try{
        const response = await fetch('/sessions',{
            headers:{
                'Authorization':`Bearer ${token}`
            }
        })
        if(!handleAuthError(response.status))return;

        if(!response.ok) throw new Error('获取会话列表失败');

        const data=await response.json();
        sessions=data;
        renderSessionList();
    }catch(error){
        console.error('加载会话出错:',error);
        alert('无法加载会话列表，请检查后端服务');
    }
}


//2.加载历史消息
async function loadMessages(sessionId) {
    try {
        const response = await fetch(`/chat/${sessionId}/messages`, {
            headers: { 'Authorization': `Bearer ${token}` }
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
        data.reverse();
        // 不反转，直接按顺序显示（假设后端已排序）
        data.forEach((msg, index) => {
            addMessage(msg.content, msg.role);
        });
        // 滚动到底部
        messages.scrollTop = messages.scrollHeight;
    } catch (error) {
        console.error('[loadMessages] 异常:', error);

        addMessage('⚠️ 加载历史消息失败: ' + error.message, 'assistant');
    }
}


// 3.创建会话
document.getElementById('newSessionBtn').addEventListener('click',async ()=>{
    try{
        const name=prompt('请输入新会话名称（或取消）','新会话');
        if(name === null) return;
        const response=await fetch('/sessions',{
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'Authorization':`Bearer ${token}`
            },
            body: JSON.stringify({name: name||'未命名会话'})
        });
        if(!handleAuthError(response.status))return;

        if(!response.ok) throw new Error('会话创建失败');

        const newSession = await response.json();
        await loadSessions();
        currentSessionId = newSession.id;
        highlightSession(currentSessionId);
        document.getElementById('messages').innerHTML = '';
        console.log('新建会话成功：',newSession);
    }catch(error){
        alert('创建会话失败：'+error.message);
    }
})

// 4.删除会话
async function deleteSession(sessionId) {
    try {
        const response = await fetch(`/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!handleAuthError(response.status)) return;
        if (!response.ok){
            const errorText = await response.text();
            throw new Error(`删除失败 (${response.status}): ${errorText}`);
        }

        await loadSessions();

        if (currentSessionId === sessionId) {
            currentSessionId = null;
            messages.innerHTML = '';
        }

        if (sessions.length > 0) {
            currentSessionId = sessions[0].id;
            highlightSession(currentSessionId);
        }
    } catch (error) {
        alert('删除失败: ' + error.message);
    }
}