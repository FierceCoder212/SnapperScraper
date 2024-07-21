from pydantic import BaseModel


class Part(BaseModel):
    part_number: str
    item_number: str
    description: str
