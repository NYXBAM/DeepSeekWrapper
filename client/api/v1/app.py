from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from client.api.v1.tasks import deepseek_request_task, deepseek_web_request_task
from celery.result import AsyncResult

app = FastAPI()

class QueryRequest(BaseModel):
    prompt: str


@app.post("/query", status_code=status.HTTP_201_CREATED)
def create_query(prompt: QueryRequest):
    try:
        task = deepseek_request_task.delay(prompt.prompt)
        return {"task_id": task.id, "status": "Queued"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail="Worker service unavailable")

@app.post("/web/query", status_code=status.HTTP_201_CREATED)
def create_web_query(prompt: QueryRequest):
    try:
        task = deepseek_web_request_task.delay(prompt.prompt)
        return {"task_id": task.id, "status": "Queued"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=503, detail="Worker service unavailable")

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.state,
        "result": result.result if result.ready() else None
    }