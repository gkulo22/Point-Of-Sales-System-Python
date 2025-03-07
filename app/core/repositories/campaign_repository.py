from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.models.campaign import (
    BuyNGetNCampaign,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.receipt import ProductForReceipt


@dataclass
class IProductDiscountCampaignRepository(Protocol):
    def create(self,
               discount_campaign: DiscountCampaign) -> DiscountCampaign:
        pass

    def get_all(self) -> List[DiscountCampaign]:
        pass

    def get_one_campaign(self,
                campaign_id: str) -> Optional[DiscountCampaign]:
        pass

    def add_product(self, product_id: str,
                    campaign_id: str) -> Optional[DiscountCampaign]:
        pass

    def delete_campaign(self, campaign_id: str) -> None:
        pass

    def get_campaign_with_product(self,
                    product_id: str) -> Optional[DiscountCampaign]:
        pass

    def delete_product(self, product_id: str,
                       campaign_id: str) -> None:
        pass


@dataclass
class IComboCampaignRepository(Protocol):
    def create(self,
               combo_campaign: ComboCampaign) -> ComboCampaign:
        pass

    def get_all(self) -> List[ComboCampaign]:
        pass

    def get_one_campaign(self, campaign_id: str) -> Optional[ComboCampaign]:
        pass

    def add_product(self, product: ProductForReceipt,
                    campaign_id: str) -> Optional[ComboCampaign]:
        pass

    def delete_campaign(self, campaign_id: str) -> None:
        pass


@dataclass
class IBuyNGetNCampaignRepository(Protocol):
    def create(self,
        buy_n_get_n_campaign: BuyNGetNCampaign) -> BuyNGetNCampaign:
        pass

    def get_all(self) -> List[BuyNGetNCampaign]:
        pass

    def get_one_campaign(self, campaign_id: str) -> Optional[BuyNGetNCampaign]:
        pass

    def delete_campaign(self, campaign_id: str) -> None:
        pass


@dataclass
class IReceiptDiscountCampaignRepository(Protocol):
    def create(self,
        receipt_campaign: ReceiptCampaign) -> ReceiptCampaign:
        pass

    def get_all(self) -> List[ReceiptCampaign]:
        pass

    def get_one_campaign(self, campaign_id: str) -> Optional[ReceiptCampaign]:
        pass

    def delete_campaign(self, campaign_id: str) -> None:
        pass

    def get_discount_on_amount(self, amount: float) -> Optional[ReceiptCampaign]:
        pass

