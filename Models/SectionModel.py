from typing import Optional
from pydantic import BaseModel

from Models.SectionDataModel import SectionData


class Section(BaseModel):
    data: str
    attr: SectionData
    state: Optional[str]
