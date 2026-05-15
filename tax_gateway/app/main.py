from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tax_gateway.app.utils.logger import setup_logging
from tax_gateway.app.api.v1.router import router as api_v1_router
from tax_gateway.app.core.exceptions import TaxGatewayException


setup_logging()

app = FastAPI(
    title="Tax Gateway API",
    description="Шлюз для интеграции с внешними налоговыми системами",
    version="1.0.0"
)

app.include_router(api_v1_router)

# === ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК ===
# Ловим любую кастомную ошибку (например, из адаптера) и превращаем её в красивый JSON по ТЗ
@app.exception_handler(TaxGatewayException)
async def custom_tax_exception_handler(request: Request, exc: TaxGatewayException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )