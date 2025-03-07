from dataclasses import dataclass
from enum import Enum
from typing import List

from app.core.models.receipt import ProductForReceipt


class CampaignType(str, Enum):
    BUY_N_GET_N = "buy_n_get_n"
    RECEIPT_DISCOUNT = "receipt_discount"
    DISCOUNT = "discount"
    COMBO = "combo"

@dataclass
class Campaign:
    id: str
    campaign_type: CampaignType


@dataclass
class ComboCampaign(Campaign):
    discount: float
    products: List[ProductForReceipt]

    def get_price(self) -> float:
        total_price = 0.0
        for product in self.products:
            total_price += product.get_price()

        return total_price

    def real_price(self) -> float:
        return self.get_price() - self.discount


@dataclass
class DiscountCampaign(Campaign):
    discount: int
    products: List[str]


@dataclass
class BuyNGetNCampaign(Campaign):
    buy_product: ProductForReceipt
    gift_product: ProductForReceipt

    def get_price(self) -> float:
        return self.buy_product.get_price() + self.gift_product.get_price()

    def real_price(self) -> float:
        return self.buy_product.get_price()


@dataclass
class ReceiptCampaign(Campaign):
    total: int
    discount: int








