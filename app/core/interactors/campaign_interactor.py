from dataclasses import dataclass
from typing import List

from app.core.models import NO_ID
from app.core.models.campaign import (
    BuyNGetNCampaign,
    Campaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.product import NumProduct
from app.core.models.receipt import ProductForReceipt
from app.core.services.campaign_service import CampaignService
from app.core.services.product_service import ProductService


@dataclass
class CampaignInteractor:
    campaign_service: CampaignService
    product_service: ProductService

    def execute_get_one(self, campaign_id: str) -> Campaign:
        return self.campaign_service.get_one_campaign(campaign_id=campaign_id)

    def execute_get_all(self) -> List[Campaign]:
        return self.campaign_service.get_all_campaigns()

    def execute_delete(self, campaign_id: str) -> None:
        self.campaign_service.delete_campaign(campaign_id=campaign_id)

    def execute_create_discount(self, discount: int) -> DiscountCampaign:
        discount_campaign = DiscountCampaign(
            id=NO_ID,
            campaign_type=CampaignType.DISCOUNT,
            discount=discount,
            products=[])
        return self.campaign_service.create_discount(
            discount_campaign=discount_campaign)

    def execute_create_combo(self, discount: float) -> ComboCampaign:
        combo_campaign = ComboCampaign(
            id=NO_ID,
            campaign_type=CampaignType.COMBO,
            discount=discount,
            products=[])
        return self.campaign_service.create_combo(
            combo_campaign=combo_campaign)

    def execute_create_receipt_discount(self,
                                        discount: int,
                                        amount: int) -> ReceiptCampaign:
        receipt_campaign = ReceiptCampaign(
            id=NO_ID,
            campaign_type=CampaignType.RECEIPT_DISCOUNT,
            total=amount,
            discount=discount)
        return self.campaign_service.create_receipt_discount(
            receipt_campaign=receipt_campaign)

    def execute_create_buy_n_get_n(self,
                buy_product: NumProduct,
                gift_product: NumProduct) -> BuyNGetNCampaign:
        product = self.product_service.get_one_product(
            product_id=buy_product.product_id)
        curr_buy_product = ProductForReceipt(
            id=buy_product.product_id,
            quantity=buy_product.num,
            price=product.get_price(),
            total=product.get_price() * buy_product.num)
        product = self.product_service.get_one_product(
            product_id=gift_product.product_id)
        curr_gift_product = ProductForReceipt(
            id=gift_product.product_id,
            quantity=gift_product.num,
            price=product.get_price(),
            total=product.get_price() * gift_product.num,
            discount_total=0)
        buy_n_get_n_campaign = BuyNGetNCampaign(
            id=NO_ID,
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=curr_buy_product,
            gift_product=curr_gift_product)
        return self.campaign_service.create_buy_n_get_n(
            buy_n_get_n_campaign=buy_n_get_n_campaign)

    def execute_adding_in_combo(self,
                                campaign_id: str,
                                product_id: str,
                                quantity: int) -> ComboCampaign:
        campaign = self.campaign_service.get_one_campaign(
            campaign_id=campaign_id)
        product = self.product_service.get_one_product(
            product_id=product_id)
        return self.campaign_service.add_product_in_combo(
            product=product,
            quantity=quantity,
            campaign_id=campaign.id)

    def execute_adding_in_discount(self,
                                   campaign_id: str,
                                   product_id: str) -> DiscountCampaign:
        campaign = self.campaign_service.get_one_campaign(
            campaign_id=campaign_id)
        return self.campaign_service.add_product_in_discount(
            product_id=product_id,
            campaign_id=campaign.id)

    def execute_delete_from_discount(self,
                                     campaign_id: str,
                                     product_id: str) -> None:
        campaign = self.campaign_service.get_one_campaign(
            campaign_id=campaign_id)
        self.campaign_service.execute_delete_from_discount(
            campaign_id=campaign.id,
            product_id=product_id)

