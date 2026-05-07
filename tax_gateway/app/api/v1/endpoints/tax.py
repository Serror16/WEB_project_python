from fastapi import APIRouter, HTTPException, Query, status

from tax_gateway.app.schemas.tax import TaxReportRequest, TaxReportResponse
# это позже тут должно быть раскомментировано
# from app.services.tax_service import tax_service

router = APIRouter(tags=["Tax Reports"])

@router.post("/report", response_model=TaxReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_tax_report(
        request_data: TaxReportRequest,
        country: str = Query(..., description="Юрисдикция")
):
    """Эндпоинт для подачи отчета: POST /api/v1/tax/report?country=..."""

    # страна добавляется в общие данные
    request_data.country = country

    try:
        # тут должно быть что-то такое:
        # result = await tax_service.send_report(request_data.model_dump())
        # (бизнес-логика+выбор адаптера)

        # имитация ответа!!!!!
        result = {"status": "success", "external_id": "12345"}
        import uuid

        return TaxReportResponse(
            status="accepted",
            report_id=str(uuid.uuid4()),
            adapter_details=result
        )
    except Exception as e:
        # единый формат ошибки
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error_code": "EXTERNAL_SERVICE_ERROR",
                "message": str(e),
                "details": {}
            }
        )


@router.get("/status/{report_id}")
async def check_tax_status(
        report_id: str,
        country: str = Query("russia", description="Юрисдикция")
):
    """Проверка статуса: GET /api/v1/tax/status/{report_id}?country=..."""
    try:
        # status_data = await tax_service.get_status(country, report_id)
        # имитация ответа!!!!!
        return {"status": "processing", "report_id": report_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "NOT_FOUND",
                "message": f"Отчет {report_id} не найден или сервис недоступен",
                "details": {"error": str(e)}
            }
        )


@router.post("/validate")
async def validate_tax_data(
        request_data: TaxReportRequest,
        country: str = Query(..., description="Юрисдикция")
):
    """Эндпоинт для предварительной проверки данных: POST /api/v1/tax/validate"""
    request_data.country = country

    # если запрос дошел сюда, то все провалидировано и все ок,
    # иначе ошибка 422

    try:
        # validation_result = await tax_service.validate(request_data.model_dump())
        # имитация ответа!!!!!
        return {"is_valid": True, "message": "Ошибок не найдено"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "is_valid": False,
                "error_code": "VALIDATION_ERROR",
                "errors": {"detail": str(e)}
            }
        )