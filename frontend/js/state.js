// 全局状态（会话列表、当前ID）


let currentSessionId = null;
let sessions = [];
let isDragging = false;      // 1. 是否正在拖拽
let startX = 0;             // 2. 鼠标按下的位置
let startWidth = 0;         // 3. 左侧面板按下的宽度