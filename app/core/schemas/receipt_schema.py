from typing import List, Optional

from pydantic import BaseModel

from app.core.models import ReceiptItem
from app.core.models.receipt import Receipt


class CreateReceiptRequest(BaseModel):
    shift_id: str


class CreateReceiptResponse(BaseModel):
    id: str
    status: str
    items: List[ReceiptItem]
    total: float


class AddProductInReceiptRequest(BaseModel):
    product_id: str
    quantity: int



class AddComboInReceiptRequest(BaseModel):
    combo_id: str
    quantity: int



class AddGiftInReceiptRequest(BaseModel):
    gift_campaign_id: str
    quantity: int



class AddItemInReceiptResponse(BaseModel):
    id: str
    status: str
    items: List[ReceiptItem]
    total: float
    discounted_total: Optional[float] = None



class GetOneReceiptResponse(BaseModel):
    id: str
    status: str
    items: List[ReceiptItem]
    total: float
    discounted_total: Optional[float] = None



class GetAllReceiptResponse(BaseModel):
    receipts: List[Receipt]


