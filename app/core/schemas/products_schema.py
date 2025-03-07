from typing import List, Optional

from pydantic import BaseModel

from app.core.models.product import Product


class CreateProductRequest(BaseModel):
    name: str
    barcode: str
    price: float



class CreateProductResponse(BaseModel):
    product: Product


class GetAllProductResponse(BaseModel):
    products: List[Product]


class GetOneProductResponse(BaseModel):
    id: str
    name: str
    barcode: str
    price: float
    discount: Optional[float] = None


class UpdateProductPriceRequest(BaseModel):
    price: float