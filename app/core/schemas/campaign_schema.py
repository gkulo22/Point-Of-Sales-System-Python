from typing import List

from pydantic import BaseModel

from app.core.models.campaign import Campaign
from app.core.models.product import NumProduct
from app.core.models.receipt import ProductForReceipt


class CreateComboRequest(BaseModel):
    discount: float


class CreateComboResponse(BaseModel):
    id: str
    campaign_type: str
    discount: float
    products: List[ProductForReceipt]


class CreateReceiptDiscountRequest(BaseModel):
    discount: int
    amount: int


class CreateReceiptDiscountResponse(BaseModel):
    id: str
    campaign_type: str
    discount: int
    amount: int


class CreateDiscountRequest(BaseModel):
    discount: int


class CreateDiscountResponse(BaseModel):
    id: str
    campaign_type: str
    discount: int
    products: List[str]


class CreateBuyNGetNProductRequest(BaseModel):
    product: NumProduct
    gift: NumProduct



class CreateBuyNGetNProductResponse(BaseModel):
    id: str
    campaign_type: str
    buy_product: ProductForReceipt
    gift_product: ProductForReceipt


class AddProductInComboRequest(BaseModel):
    product_id: str
    quantity: int


class AddProductInComboResponse(BaseModel):
    id: str
    campaign_type: str
    discount: float
    products: List[ProductForReceipt]


class AddProductInDiscountResponse(BaseModel):
    id: str
    campaign_type: str
    discount: int
    products: List[str]



class GetOneCampaignResponse(BaseModel):
    campaign: Campaign


class GetAllCampaignsResponse(BaseModel):
    campaigns: List[Campaign]



