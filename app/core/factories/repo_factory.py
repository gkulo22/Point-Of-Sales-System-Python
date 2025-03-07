from typing import Protocol

from app.core.repositories.campaign_repository import (
    IBuyNGetNCampaignRepository,
    IComboCampaignRepository,
    IProductDiscountCampaignRepository,
    IReceiptDiscountCampaignRepository,
)
from app.core.repositories.product_repository import IProductRepository
from app.core.repositories.receipt_repesitory import IReceiptRepository
from app.core.repositories.shift_repository import IShiftRepository


class RepoFactory(Protocol):
    def products(self) -> IProductRepository:
        pass

    def receipts(self) -> IReceiptRepository:
        pass

    def shifts(self) -> IShiftRepository:
        pass

    def discount_campaign(self) -> IProductDiscountCampaignRepository:
        pass

    def combo_campaign(self) -> IComboCampaignRepository:
        pass

    def receipt_discount_campaign(self) -> IReceiptDiscountCampaignRepository:
        pass

    def buy_n_get_n_campaign(self) -> IBuyNGetNCampaignRepository:
        pass