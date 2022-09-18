from pydantic.main import BaseModel


class UserIdModel(BaseModel):
    user_id: str

    def __getitem__(self, item):
        return getattr(self, item)


