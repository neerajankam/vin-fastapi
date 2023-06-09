from pydantic import BaseModel


class VinResponse(BaseModel):
    input_vin_requested: str
    make: str
    model: str
    year: str
    body_class: str
    cached_response: bool
