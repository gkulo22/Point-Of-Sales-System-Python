from dataclasses import dataclass
from typing import cast

from app.core.exceptions.shift_exceptions import ShiftClosedErrorMessage
from app.core.models import NO_ID
from app.core.models.campaign import BuyNGetNCampaign, ComboCampaign
from app.core.models.product import DiscountedProduct
from app.core.models.receipt import Receipt
from app.core.services.campaign_service import CampaignService
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.core.services.shift_service import ShiftService
from app.core.state.shift_state import ClosedShiftState


@dataclass
class ReceiptInteractor:
    receipt_service: ReceiptService
    product_service: ProductService
    shift_service: ShiftService
    campaign_service: CampaignService

    def execute_create(self, shift_id: str) -> Receipt:
        receipt = Receipt(id=NO_ID, shift_id=shift_id, items=[], total=0.0)
        shift = self.shift_service.get_one_shift(shift_id=receipt.shift_id)
        if isinstance(shift.state, ClosedShiftState):
            raise ShiftClosedErrorMessage(shift_id=shift.id)

        return self.receipt_service.create_receipt(receipt=receipt)

    def execute_get_one(self, receipt_id: str) -> Receipt:
        receipt = self.receipt_service.get_one_receipt(receipt_id=receipt_id)
        return self.campaign_service.get_campaign_receipt(receipt=receipt)

    def execute_delete(self, receipt_id: str) -> None:
        receipt = self.receipt_service.get_one_receipt(receipt_id=receipt_id)
        self.receipt_service.delete_receipt(receipt=receipt)

    def execute_addition_product(self, receipt_id: str,
                                 product_id: str,
                                 quantity: int) -> Receipt:
        product = self.product_service.get_one_product(
            product_id=product_id)
        product_decorator = self.campaign_service.get_campaign_product(
            product=product)
        receipt = self.receipt_service.get_one_receipt(
            receipt_id=receipt_id)
        inner_product = product_decorator.inner_product
        product = inner_product

        if isinstance(product_decorator, DiscountedProduct):
            product.discount = product_decorator.get_price()

        receipt = self.receipt_service.add_product(
            receipt=receipt,
            product=product,
            quantity=quantity)
        return self.campaign_service.get_campaign_receipt(receipt=receipt)

    def execute_addition_combo(self,
                               receipt_id: str,
                               combo_id: str,
                               quantity: int) -> Receipt:
        combo = cast(ComboCampaign, self.campaign_service.get_one_campaign(
            campaign_id=combo_id))
        receipt = self.receipt_service.get_one_receipt(receipt_id=receipt_id)
        receipt = self.receipt_service.add_combo_product(
            receipt=receipt,
            combo=combo,
            quantity=quantity)
        return self.campaign_service.get_campaign_receipt(receipt=receipt)

    def execute_addition_gift(self,
                              receipt_id: str,
                              gift_id: str,
                              quantity: int) -> Receipt:
        gift = cast(BuyNGetNCampaign, self.campaign_service.get_one_campaign(
            campaign_id=gift_id))
        receipt = self.receipt_service.get_one_receipt(receipt_id=receipt_id)
        receipt = self.receipt_service.add_gift_product(
            receipt=receipt,
            gift=gift,
            quantity=quantity)
        return self.campaign_service.get_campaign_receipt(receipt=receipt)

    def execute_delete_item(self, receipt_id: str, item_id: str) -> None:
        receipt = self.receipt_service.get_one_receipt(receipt_id=receipt_id)
        self.receipt_service.delete_item(receipt=receipt, item_id=item_id)

