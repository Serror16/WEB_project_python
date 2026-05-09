from fastapi import APIRouter, Depends, Query, status

from tax_gateway.app.schemas.tax import TaxReportRequest, TaxReportResponse
from tax_gateway.app.services.tax_service import TaxService


router = APIRouter(tags=["Tax Reports"])


def get_tax_service() -> TaxService:
    return TaxService()

@router.post("/report", response_model=TaxReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_tax_report(
        request_data: TaxReportRequest,
        country: str = Query(..., description="Юрисдикция"),
        tax_service: TaxService = Depends(get_tax_service)
):
    """Эндпоинт для подачи отчета: POST /api/v1/tax/report?country=..."""

    request_data.country = country

    result = await tax_service.send_report(request_data)

    return TaxReportResponse(
        status=result.status.name,
        report_id=str(result.external_id), 
        adapter_details={"message": "Отправлено через шлюз"}
    )


@router.get("/status/{report_id}")
async def check_tax_status(
        report_id: str,
        country: str = Query("RU", description="Юрисдикция"),
        tax_service: TaxService = Depends(get_tax_service)
):
    """Проверка статуса: GET /api/v1/tax/status/{report_id}?country=..."""

    result = await tax_service.get_status(country, report_id)
    
    return {
        "status": result.status.name,
        "report_id": str(result.report_id)
    }


@router.post("/validate")
async def validate_tax_data(
        request_data: TaxReportRequest,
        country: str = Query(..., description="Юрисдикция"),
        tax_service: TaxService = Depends(get_tax_service)
):
    """Эндпоинт для предварительной проверки данных: POST /api/v1/tax/validate"""
    
    request_data.country = country

    result = await tax_service.validate(request_data)
    
    return {
        "is_valid": result.is_valid,
        "message": "Ошибок не найдено" if result.is_valid else "Данные отклонены налоговой"
    }