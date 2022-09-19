from pydantic.main import BaseModel


class UserIdModel(BaseModel):
    id: str

    def __getitem__(self, item):
        return getattr(self, item)
