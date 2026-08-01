// 全局状态
let currentSessionId = null;
let sessions = [];              // 每个元素: { id, name, mode: 'chat'|'rag' }
let isDragging = false;
let startX = 0;
let startWidth = 0;