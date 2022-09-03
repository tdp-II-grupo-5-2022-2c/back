from pydantic.main import BaseModel


class HealthStatusResponse(BaseModel):
    status: str
