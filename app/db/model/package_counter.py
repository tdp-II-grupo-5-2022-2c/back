from pydantic.main import BaseModel
from pydantic import Field


class PackageCounterModel(BaseModel):
    counter: int = Field(...)

    def __getitem__(self, item):
        return getattr(self, item)
