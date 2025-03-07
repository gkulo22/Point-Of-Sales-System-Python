from typing import List

from pydantic import BaseModel

from app.core.models.receipt import Receipt


class CreateShiftResponse(BaseModel):
    id: str
    receipts: List[Receipt]
    state: str


class GetOneShiftResponse(BaseModel):
    id: str
    receipts: List[Receipt]
    state: str
    total: float


class UpdateShiftStateRequest(BaseModel):
    status: bool