from pydantic import BaseModel

from Models.Parts import Parts


class Catalog(BaseModel):
    catalog: str
    sgl_code: str
    sections: list[Parts]
