from fastapi import FastAPI, Request, Response
import uvicorn

app = FastAPI(title="Mock Russian Tax Service")

@app.post("/mock-russia/submit")
async def submit(request: Request):
    body = await request.body()
    print(f"[MOCK] Получен отчет (XML):\n{body.decode()}")
    return Response(content="<Response><Status>Success</Status></Response>", media_type="application/xml")

@app.get("/mock-russia/status/{report_id}")
async def get_status(report_id: str):
    print(f"[MOCK] Проверка статуса для ID: {report_id}")
    return {"status": "SUCCESS", "external_id": report_id}

@app.post("/mock-russia/validate")
async def validate(request: Request):
    print("[MOCK] Запрос на валидацию получен")
    return {"is_valid": True}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)