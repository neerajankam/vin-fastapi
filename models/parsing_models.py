from pydantic import BaseModel


class VinRequest(BaseModel):
    vin: str

class VinResponse(BaseModel):
    vin: str
    make: str
    model: str
    year: str
    body_class: str
    cached_response: bool