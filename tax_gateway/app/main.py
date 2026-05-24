from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tax_gateway.app.utils.logger import setup_logging
from tax_gateway.app.api.v1.router import router as api_v1_router
from tax_gateway.app.core.exceptions import TaxGatewayException, ExternalServiceError, BadRequestError

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
async def tax_gateway_exception_handler(request: Request, e: TaxGatewayException):
    return JSONResponse(
        status_code=e.status_code,
        content={
            "error_code": e.error_code,
            "message": e.message,
            "details": e.details
        }
    )

@app.exception_handler(ExternalServiceError)
async def external_service_exception_handler(request: Request, e: ExternalServiceError):
    return JSONResponse(
        status_code=e.status_code,
        content={
            "error_code": e.error_code,
            "message": e.message,
            "details": e.details
        }
    )

@app.exception_handler(BadRequestError)
async def bad_request_exception_handler(request: Request, e: BadRequestError):
    return JSONResponse(
        status_code=e.status_code,
        content={
            "error_code": e.status_code,
            "message": e.message,
            "time": e.time
        }
    )
