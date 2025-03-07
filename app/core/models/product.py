from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from app.core.models.models import ICalculatePrice


@dataclass
class Product(ICalculatePrice):
    id: str
    name: str
    barcode: str
    price: float
    discount: Optional[float] = None

    def get_price(self) -> float:
        return self.price

    def get_discounted_price(self) -> Optional[float]:
        if self.discount is not None:
            return self.discount
        return None

@dataclass
class ProductDecorator:
    inner_product: Product

    def get_price(self) -> float:
        return self.inner_product.get_price()


@dataclass
class DiscountedProduct(ProductDecorator):
    inner_product: Product
    discount: int

    def get_price(self) -> float:
        return (self.inner_product.get_price() -
                (self.discount/100 * self.inner_product.get_price()))



class NumProduct(BaseModel):
    product_id: str
    num: int