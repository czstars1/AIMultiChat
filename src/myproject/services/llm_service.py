import asyncio
import json
from pathlib import Path
import httpx
from src.myproject.config import OLLAMA_CHAT_API, MODEL_NAME

MAXTIMES=2
RETRY_INTERVAL=3

async def call_llm(message: list,stream: bool = False)-> str:
    payload ={
        "model": MODEL_NAME,
        "messages": message,
        "stream":False,
        "keep_alive": -1
    }
    async with httpx.AsyncClient(timeout=6000) as client:
        for attempt in range(MAXTIMES+1):
            try:
                response=await client.post(OLLAMA_CHAT_API,json=payload)
                response.raise_for_status()
                data= response.json()
                print("DEBUG 原始返回:", data)

                content=data.get("message",{}).get("content","")
                done_reason=data.get("done_reason","")

                if not content and done_reason == "load":
                    if attempt < MAXTIMES:
                        print(f"检测到 done_reason='load' 且内容为空，{RETRY_INTERVAL}秒后重试...")
                        await asyncio.sleep(RETRY_INTERVAL)
                        continue
                    else:
                        raise RuntimeError("重试多次后仍返回空内容且 done_reason='load'")
                return content

            except httpx.HTTPStatusError as e:
                if attempt < MAXTIMES:
                    print(f"请求异常 {e}，{RETRY_INTERVAL}秒后重试...")
                    await asyncio.sleep(RETRY_INTERVAL)
                else:
                    raise
            except Exception as e:
                if attempt < MAXTIMES:
                    print(f"发生异常 {e}，{RETRY_INTERVAL}秒后重试...")
                    await asyncio.sleep(RETRY_INTERVAL)
                else:
                    raise
        return ""


async def stream_llm(message:list):
    payload = {
        "model": MODEL_NAME,
        "messages": message,
        "stream": True,
        "keep_alive": -1
    }

    async with httpx.AsyncClient(timeout=6000) as client:
        async with client.stream("post",OLLAMA_CHAT_API,json=payload)as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue

                try:
                    data=json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
                    if data.get("done"):
                        break
                except json.JSONDecodeError:
                    continue

