from dataclasses import dataclass, field
from typing import List, Protocol

from app.core.exceptions.campaign_exceptions import GetCampaignErrorMessage
from app.core.models.campaign import (
    BuyNGetNCampaign,
    Campaign,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.product import DiscountedProduct, Product, ProductDecorator
from app.core.models.receipt import ProductForReceipt, Receipt
from app.core.repositories.campaign_repository import (
    IBuyNGetNCampaignRepository,
    IComboCampaignRepository,
    IProductDiscountCampaignRepository,
    IReceiptDiscountCampaignRepository,
)


@dataclass
class ICampaignChain(Protocol):
    def get_campaign_product(self, product: Product) -> ProductDecorator:
        pass

    def get_campaign(self, campaign_id: str) -> Campaign:
        pass

    def delete_campaign(self, campaign_id: str) -> None:
        pass


class NoCampaignChain(ICampaignChain):
    def get_campaign_product(self, product: Product) -> ProductDecorator:
        return ProductDecorator(inner_product=product)

    def get_campaign(self, campaign_id: str) -> Campaign:
        raise GetCampaignErrorMessage(campaign_id=campaign_id)

    def delete_campaign(self, campaign_id: str) -> None:
        raise GetCampaignErrorMessage(campaign_id=campaign_id)


@dataclass
class ReceiptCampaignChain(ICampaignChain):
    repository: IReceiptDiscountCampaignRepository

    next_campaign: ICampaignChain = field(default_factory=NoCampaignChain)

    def get_campaign_product(self, product: Product) -> ProductDecorator:
        return self.next_campaign.get_campaign_product(product=product)

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            return self.next_campaign.get_campaign(campaign_id=campaign_id)
        return campaign

    def delete_campaign(self, campaign_id: str) -> None:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            self.next_campaign.delete_campaign(campaign_id=campaign_id)
            return

        self.repository.delete_campaign(campaign_id=campaign_id)


@dataclass
class DiscountCampaignChain(ICampaignChain):
    repository: IProductDiscountCampaignRepository
    next_campaign: ICampaignChain = field(default_factory=NoCampaignChain)

    def get_campaign_product(self, product: Product) -> ProductDecorator:
        given_campaign = self.repository.get_campaign_with_product(
            product_id=product.id)
        if not given_campaign:
            return self.next_campaign.get_campaign_product(product=product)

        discounted_product = DiscountedProduct(inner_product=product,
                                    discount=given_campaign.discount)
        return discounted_product

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            return self.next_campaign.get_campaign(campaign_id=campaign_id)

        return campaign

    def delete_campaign(self, campaign_id: str) -> None:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            self.next_campaign.delete_campaign(campaign_id=campaign_id)
            return

        self.repository.delete_campaign(campaign_id=campaign_id)


@dataclass
class ComboCampaignChain(ICampaignChain):
    repository: IComboCampaignRepository
    next_campaign: ICampaignChain = field(default_factory=NoCampaignChain)

    def get_campaign_product(self, product: Product) -> ProductDecorator:
        return self.next_campaign.get_campaign_product(product=product)

    def delete_campaign(self, campaign_id: str) -> None:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            self.next_campaign.delete_campaign(campaign_id=campaign_id)
            return

        self.repository.delete_campaign(campaign_id=campaign_id)

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            return self.next_campaign.get_campaign(campaign_id=campaign_id)
        return campaign


@dataclass
class BuyNGetNCampaignChain(ICampaignChain):
    repository: IBuyNGetNCampaignRepository
    next_campaign: ICampaignChain = field(default_factory=NoCampaignChain)

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            return self.next_campaign.get_campaign(campaign_id=campaign_id)

        return campaign

    def delete_campaign(self, campaign_id: str) -> None:
        campaign = self.repository.get_one_campaign(campaign_id=campaign_id)
        if not campaign:
            self.next_campaign.delete_campaign(campaign_id=campaign_id)
            return

        self.repository.delete_campaign(campaign_id=campaign_id)

    def get_campaign_product(self, product: Product) -> ProductDecorator:
        return self.next_campaign.get_campaign_product(product=product)

@dataclass
class CampaignService:
    product_discount_repo: IProductDiscountCampaignRepository
    receipt_discount_repo: IReceiptDiscountCampaignRepository
    combo_campaign_repo: IComboCampaignRepository
    buy_get_gift_repo: IBuyNGetNCampaignRepository

    def _build_chain(self) -> ICampaignChain:
        return BuyNGetNCampaignChain(
            repository=self.buy_get_gift_repo,
                    next_campaign=ComboCampaignChain(
                        repository=self.combo_campaign_repo,
                        next_campaign=DiscountCampaignChain(
                            repository=self.product_discount_repo,
                            next_campaign=ReceiptCampaignChain(
                                repository=self.receipt_discount_repo
                            )
                        )
                    )
                )


    def get_campaign_product(self, product: Product) -> ProductDecorator:
        start_chain = self._build_chain()
        return start_chain.get_campaign_product(product=product)

    def get_campaign_receipt(self, receipt: Receipt) -> Receipt:
        total = receipt.total
        if receipt.discount_total is not None:
            total = receipt.discount_total

        campaign = self.receipt_discount_repo.get_discount_on_amount(
            amount=total)
        if campaign is not None:
            total -= campaign.discount
            receipt.discount_total = total

        return receipt

    def get_one_campaign(self, campaign_id: str) -> Campaign:
        start_chain = self._build_chain()
        return start_chain.get_campaign(campaign_id=campaign_id)

    def get_all_campaigns(self) -> List[Campaign]:
        return (self.product_discount_repo.get_all() +
                self.receipt_discount_repo.get_all() +
                self.combo_campaign_repo.get_all() +
                self.buy_get_gift_repo.get_all())

    def delete_campaign(self, campaign_id: str) -> None:
        start_chain = self._build_chain()
        return start_chain.delete_campaign(campaign_id=campaign_id)

    def create_discount(self,
                discount_campaign: DiscountCampaign) -> DiscountCampaign:
        return self.product_discount_repo.create(
            discount_campaign=discount_campaign)

    def create_combo(self,
            combo_campaign: ComboCampaign) -> ComboCampaign:
        return self.combo_campaign_repo.create(
            combo_campaign=combo_campaign)

    def create_receipt_discount(self,
            receipt_campaign: ReceiptCampaign) -> ReceiptCampaign:
        return self.receipt_discount_repo.create(
            receipt_campaign=receipt_campaign)

    def create_buy_n_get_n(self,
            buy_n_get_n_campaign: BuyNGetNCampaign) -> BuyNGetNCampaign:
        return self.buy_get_gift_repo.create(
            buy_n_get_n_campaign=buy_n_get_n_campaign)

    def add_product_in_combo(self,
                        product: Product,
                        quantity: int,
                        campaign_id: str) -> ComboCampaign | None:
        product_for_combo = ProductForReceipt(
            id=product.id,
            quantity=quantity,
            price=product.price)
        product_for_combo.total = product.price * quantity
        return self.combo_campaign_repo.add_product(
            product=product_for_combo,
            campaign_id=campaign_id)

    def add_product_in_discount(self, product_id: str,
                campaign_id: str) -> DiscountCampaign:
        return self.product_discount_repo.add_product(
            product_id=product_id,
            campaign_id=campaign_id)

    def execute_delete_from_discount(self,
                    campaign_id: str,
                    product_id: str) -> None:
        self.product_discount_repo.delete_product(
            product_id=product_id,
            campaign_id=campaign_id)
