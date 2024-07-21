from typing import Optional
from pydantic import BaseModel

from Models.SectionsModel import Sections


class CatalogResponse(BaseModel):
    html: str
    model: Optional[Sections]
