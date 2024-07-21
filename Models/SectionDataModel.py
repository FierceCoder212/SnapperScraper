from pydantic import BaseModel


class SectionData(BaseModel):
    aria: str
    arib: str
    rel: str
    slug: str
    src: str
