from pydantic.main import BaseModel
from app.db.model.py_object_id import PyObjectId
from pydantic import Field
from bson import ObjectId


class StickerModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    image: str = Field(...)
    type: str = "normal"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "image": "image.png",
                "type": "normal",
            }
        }

    def __getitem__(self, item):
        return getattr(self, item)
