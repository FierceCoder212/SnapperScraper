from pydantic import BaseModel
from Models.Part import Part


class Parts(BaseModel):
    section: str
    section_diagram_url: str
    section_diagram: str
    parts: list[Part]
