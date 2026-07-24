// 主入口（事件绑定、初始化、流式处理）


const sendBtn=document.getElementById("sendBtn")
const userInput=document.getElementById("userInput")
const messages=document.getElementById("messages")
const sessionListEl = document.getElementById('sessionList');
const newSessionBtn = document.getElementById('newSessionBtn');
const resizer=document.getElementById('resizer');
const sidebar=document.getElementById('sidebar');

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

document.addEventListener('DOMContentLoaded',async ()=>{
    await loadSessions();
    if (sessions.length>0){
        currentSessionId = sessions[0].id;
        highlightSession(currentSessionId);
    }
})

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
                'Authorization':`Bearer ${token}`
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