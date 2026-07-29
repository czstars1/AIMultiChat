// UI 渲染层（操作 DOM）


 // 1. 渲染会话列表
function renderSessionList(){
    const list = document.getElementById('sessionList');
    list.innerHTML = '';
    sessions.forEach(session =>{
        const li = document.createElement('li');
        li.dataset.id=session.id;

        const nameSpan = document.createElement('span');
        nameSpan.textContent=session.name||`会话 ${session.id.slice(0.6)}`;
        li.appendChild(nameSpan);

        const delBtn = document.createElement('span');
        delBtn.textContent='×';
        delBtn.className='delete-btn';

        delBtn.addEventListener('click',async (e)=>{
            e.stopPropagation();
            if(confirm(`确定要删除“${session.name}”吗？`)){
                await deleteSession(session.id);
            }
        })

        li.appendChild(delBtn);

        li.addEventListener('click',()=> switchSession(session.id));

        if(session.id === currentSessionId){
            li.classList.add('active');
        }
        list.appendChild(li);
    })
}

 // 2. 添加消息到界面（返回 DOM 元素以便流式追加）
 function addMessage(content,type){
    const msgDiv=document.createElement('div');

    msgDiv.className='message '+type;

    const icon=type==='user' ? '👤' : '🤖 ';
    msgDiv.textContent=icon+content;

    messages.appendChild(msgDiv);
    messages.scrollTop=messages.scrollHeight;

    return msgDiv;
}

 //3.滚动优化
 function scrollToBottomIfNeeded(){
    const threshold = 30;
    const { scrollTop,scrollHeight,clientHeight }=messages;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < threshold;
    if(isNearBottom){
        messages.scrollTop=scrollHeight;
    }
}


// 4. 高亮当前会话
function highlightSession(sessionId){
    const items=document.querySelectorAll('#sessionList li');
    items.forEach(li =>{
        li.classList.toggle('active',li.dataset.id===sessionId);
    })
}

// 5. 切换会话
function switchSession(sessionId){
    if(sessionId === currentSessionId) return;
    currentSessionId = sessionId;
    highlightSession(sessionId);

    messages.innerHTML = '';
    loadMessages(sessionId);
    console.log(`切换到会话: ${sessionId}`);
}