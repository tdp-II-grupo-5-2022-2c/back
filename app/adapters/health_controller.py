from fastapi import APIRouter, status
from app.adapters.dtos.health import HealthStatusResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_description="Get API Status",
    response_model=HealthStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def health():
    return HealthStatusResponse(status="UP")
