from pydantic import BaseModel


class ExcelFile(BaseModel):
    sgl_code: str
    manufacturer: str
    model: str
    unique_product_code: str
    year: str
    section: str
