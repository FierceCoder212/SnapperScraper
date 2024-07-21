from pydantic import BaseModel
from Models.SectionModel import Section


class Sections(BaseModel):
    json: list[Section]
