// 主入口（事件绑定、初始化、流式处理）

console.log('CONFIG 对象:', CONFIG);
const profile = document.querySelector('.user-profile');
const sendBtn=document.getElementById("sendBtn")
const userInput=document.getElementById("userInput")
const messages=document.getElementById("messages")
const newSessionBtn = document.getElementById('newSessionBtn');
const resizer=document.getElementById('resizer');
const sidebar=document.getElementById('sidebar');

const loginOverlay = document.getElementById('loginOverlay');
const loginBtn = document.getElementById('loginBtn');
const loginUsername = document.getElementById('loginUsername');
const loginPassword = document.getElementById('loginPassword');
const loginError = document.getElementById('loginError');

// ======================== 事件绑定 ========================
sendBtn.addEventListener('click',sendMessage)

userInput.addEventListener('keydown',function(event){
    if(event.key === 'Enter'&& !event.shiftKey){
        event.preventDefault();
        sendMessage();
    }
});

resizer.addEventListener('mousedown',function (e){
    isDragging=true;
    startX=e.clientX;
    startWidth=sidebar.getBoundingClientRect().width;
})

document.addEventListener('mousemove',function (e){
    if(!isDragging) return;
    const delta=e.clientX-startX;
    let newWidth=startWidth+delta;

    sidebar.style.width=newWidth+'px';
})

document.addEventListener('mouseup',function (){
    isDragging=false;
})


// 按下回车键触发登录
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !loginOverlay.classList.contains('hidden')) {
        loginBtn.click();
    }
});

document.querySelector('.menu-trigger').addEventListener('click', (e) => {
    e.stopPropagation();          // 防止冒泡导致点击外部关闭
    profile.classList.toggle('active');
});

// 点击页面其他地方关闭菜单
document.addEventListener('click', () => {
    profile.classList.remove('active');
});

document.getElementById('logoutBtn').addEventListener('click', function() {
    // 1. 清除本地存储
    localStorage.removeItem('chat_token');
    localStorage.removeItem('chat_username');

    // 2. 清除内存中的 token
    CONFIG.TOKEN = null;

    // 3. 重置界面元素
    document.getElementById('profileUsername').textContent = '用户名';   // 恢复默认
    document.getElementById('messages').innerHTML = '';               // 清空消息
    document.getElementById('sessionList').innerHTML = '';           // 清空会话列表

    // 4. 清空当前会话状态（如果有）
    // 如果你有 state 对象，也可以重置 currentSessionId 等
    // 例如：state.currentSessionId = null; state.sessions = [];

    // 5. 显示登录模态框
    document.getElementById('loginOverlay').classList.remove('hidden');

    // 6. （可选）关闭下拉菜单
    document.querySelector('.user-profile').classList.remove('active');

    console.log('已退出登录');
});

document.addEventListener('DOMContentLoaded', async () => {
    // 如果 token 存在，说明已登录，直接初始化聊天
    if (CONFIG.token) {
        // 隐藏登录框
        document.getElementById('loginOverlay').classList.add('hidden');

        // 加载会话（这里你可以复用登录成功后的初始化逻辑）
        try {
            await loadSessions();
            if (sessions.length > 0) {
                currentSessionId = sessions[0].id;
                renderSessionList();
                loadMessages(currentSessionId);
            }
            // 如果有用户信息（如用户名），也可以从 localStorage 取，但你登录时没有存用户名，可以额外存一个
            // 但最简单的做法是：把用户名也存入 localStorage
            const savedUsername = localStorage.getItem('chat_username');
            if (savedUsername) {
                document.getElementById('profileUsername').textContent = savedUsername;
            }
        } catch (error) {
            // 如果 token 过期（后端返回 403），清除本地存储并显示登录框
            console.error('自动登录失败:', error);
            localStorage.removeItem('chat_token');
            localStorage.removeItem('chat_username');
            document.getElementById('loginOverlay').classList.remove('hidden');
        }
    }
    // 如果 token 不存在，登录框保持显示，不加载任何会话
});



// 5. 发送消息（流式版）
async function sendMessage(){
    if(!currentSessionId){
        alert('请先选择一个会话');
        sendBtn.disabled = false;
        sendBtn.textContent='发送';
        return;
    }
    const text=userInput.value.trim();

    if (text===''){
        alert('请输入消息！');
        return;
    }

    addMessage(text,'user');
    userInput.value='';

    sendBtn.disabled=true;
    sendBtn.textContent='发送中...';

    try{
        const requestData={
            session_id:currentSessionId,
            message:text
        };

        const options={
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'Authorization':`Bearer ${CONFIG.token}`
            },
            body:JSON.stringify(requestData)
        };

        const response = await fetch('/chat/stream',options);
        if(!handleAuthError(response.status))return;

        if(!response.ok){
            const errorData=await response.json();
            alert('请求失败: '+(errorData.detail||response.statusText));
            return;
        }
        // ========================
        const aiDiv= addMessage('','assistant');

        const reader=response.body.getReader();
        const decoder=new TextDecoder();
        let buffer ='';

        while(true) {
            const {done, value} = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, {stream: true})

            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const content = line.slice(6);
                    if (content === '[DONE]') {
                        console.log('流式传输结束');
                    } else if (content.startsWith('[error]')) {
                        aiDiv.textContent += content;
                    } else {
                        aiDiv.textContent += content;
                    }
                    scrollToBottomIfNeeded();
                }
            }
        }
        // ==========================
        // const AIReply = await response.json();
        //
        // addMessage(AIReply,'assistant');
    }catch(error){
        addMessage('⚠️ 出错了：' + error.message, 'assistant');
        console.error('发送失败:', error);
    }finally{
        sendBtn.disabled = false;
        sendBtn.textContent = '发送';
    }
}