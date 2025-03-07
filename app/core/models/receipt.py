from dataclasses import dataclass
from typing import List, Optional

from app.core.models.models import ICalculatePrice
from app.core.state.receipt_state import (
    ClosedReceiptState,
    OpenReceiptState,
    ReceiptState,
)


@dataclass
class ProductForReceipt(ICalculatePrice):
    id: str
    quantity: int
    price: float
    total: float = 0.0
    discount_price: Optional[float] = None
    discount_total: Optional[float] = None

    def get_price(self) -> float:
        return self.price * self.quantity

    def get_discounted_price(self) -> Optional[float]:
        if self.discount_price is not None:
            return self.discount_price * self.quantity

        return None


@dataclass
class ComboForReceipt(ICalculatePrice):
    id: str
    products: List[ProductForReceipt]
    quantity: int
    price: float
    total: float = 0.0
    discount_price: Optional[float] = None
    discount_total: Optional[float] = None

    def get_price(self) -> float:
        return self.price * self.quantity

    def get_discounted_price(self) -> Optional[float]:
        if self.discount_price is not None:
            return self.discount_price * self.quantity

        return None


@dataclass
class GiftForReceipt(ICalculatePrice):
    id: str
    buy_product: ProductForReceipt
    gift_product: ProductForReceipt
    quantity: int
    price: float
    total: float = 0.0
    discount_price: Optional[float] = None
    discount_total: Optional[float] = None

    def get_price(self) -> float:
        return (self.buy_product.get_price() +
                self.gift_product.get_price()) * self.quantity

    def get_discounted_price(self) -> float:
        return (self.buy_product.get_price()) * self.quantity


@dataclass
class Receipt(ICalculatePrice):
    id: str
    shift_id: str
    items: List[ICalculatePrice]  # List of items implementing ICalculatePrice
    total: float
    discount_total: Optional[float] = None
    status: bool = True

    def get_price(self) -> float:
        return sum(item.get_price() for item in self.items)

    def get_discounted_price(self) -> Optional[float]:
        discounted = sum(
            item.get_discounted_price() or item.get_price() for item in
            self.items)

        if discounted < sum(item.get_price() for item in self.items):
            return discounted

        return None

    def get_state(self) -> ReceiptState:
        if self.status:
            return OpenReceiptState()
        else:
            return ClosedReceiptState()
