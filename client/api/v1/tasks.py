import asyncio
from client.api.v1.worker_celery import celery_app
from client import DeepSeekClient, DeepSeekFlow
import re

def to_plain_text(md_text: str) -> str:
    text = re.sub(r'[*_]{1,3}(.*?)[*_]{1,3}', r'\1', md_text)
    text = re.sub(r'(^|\n)>\s?', r'\1', text)
    text = re.sub(r'#+\s?', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def to_plain_text_web(md_text: str) -> str:
    text = re.sub(r'\[-?\d+\]\(.*?\)', '', md_text)
    text = re.sub(r'\[-?\d+\]', '', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'\|', ' ', text)  
    text = re.sub(r'^[-\s|]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'[*_#`]', '', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r' +', ' ', text) 
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


async def _run_query(prompt: str):
    async with DeepSeekClient() as client:
        flow = DeepSeekFlow(client=client)
        response = await flow.run_query(prompt)
        return response

async def _run_web_query(prompt: str):
    """Using WebSearch: `use_search=True` flag"""
    async with DeepSeekClient(use_search=True) as client:
        flow = DeepSeekFlow(client=client)
        response = await flow.run_query(prompt)
        return response

@celery_app.task(name="deepseek_query_task",
                 bind=True,
                 max_retries=3,
                 default_retry_delay=5)

def deepseek_request_task(self, prompt: str):
    try:
        raw = asyncio.run(_run_query(prompt))
        plain = to_plain_text(raw)
        return {
            "raw": raw,
            "plain_text": plain
        }
        
    except Exception as e:
        raise self.retry(exc=e)
    
@celery_app.task(name="deepseek_web_query_task",
                 bind=True,
                 max_retries=3,
                 default_retry_delay=5)

def deepseek_web_request_task(self, prompt: str):
    try:
        raw = asyncio.run(_run_web_query(prompt))
        plain = to_plain_text_web(raw)
        return {
            "raw": raw,
            "plain_text": plain
        }
    except Exception as e:
        raise self.retry(exc=e)
    
    