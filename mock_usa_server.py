from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="Mock USA Tax Service (IRS)")

@app.post("/mock-usa/submit")
async def submit(request: Request):
    # В отличие от РФ, здесь мы ожидаем и парсим JSON
    body = await request.json()
    
    print(f"--- [MOCK USA] НОВЫЙ ОТЧЕТ ---")
    print(f"SSN: {body.get('ssn')}")
    print(f"Income: ${body.get('income_usd')}")
    print(f"Year: {body.get('tax_year')}")
    print(f"Request ID: {body.get('request_id')}")
    print("------------------------------")
    
    # Адаптеру США достаточно просто получить код 200 (успех)
    return {"message": "Tax return accepted by mock IRS"}

@app.get("/mock-usa/status/{report_id}")
async def get_status(report_id: str):
    print(f"[MOCK USA] Запрошен статус для Request ID: {report_id}")
    
    # Наш UsaTaxAdapter ожидает поле "state" со значением "COMPLETED"
    return {
        "state": "COMPLETED", 
        "report_id": report_id,
        "processing_time_ms": 142
    }

@app.post("/mock-usa/validate")
async def validate(request: Request):
    body = await request.json()
    print(f"[MOCK USA] Валидация данных для SSN: {body.get('ssn')}")
    
    # Наш UsaTaxAdapter ожидает булево поле "valid"
    return {
        "valid": True,
        "warnings": []
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)