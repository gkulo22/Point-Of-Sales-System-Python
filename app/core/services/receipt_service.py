from dataclasses import dataclass
from typing import List

from app.core.exceptions.receipt_exceptions import (
    GetReceiptErrorMessage,
    ReceiptClosedErrorMessage,
)
from app.core.models.campaign import BuyNGetNCampaign, ComboCampaign
from app.core.models.product import Product
from app.core.models.receipt import (
    ComboForReceipt,
    GiftForReceipt,
    ProductForReceipt,
    Receipt,
)
from app.core.repositories.receipt_repesitory import IReceiptRepository


@dataclass
class ReceiptService:
    receipt_repository: IReceiptRepository

    def create_receipt(self, receipt: Receipt) -> Receipt:
        return self.receipt_repository.create(receipt=receipt)

    def get_one_receipt(self, receipt_id: str) -> Receipt:
        receipt = self.receipt_repository.get_one(receipt_id=receipt_id)
        if not receipt:
            raise GetReceiptErrorMessage(receipt_id=receipt_id)

        return receipt

    def get_all_receipts(self) -> List[Receipt]:
        return self.receipt_repository.get_all()

    def delete_receipt(self, receipt: Receipt) -> None:
        if not receipt.status:
            raise ReceiptClosedErrorMessage(receipt_id=receipt.id)
        self.receipt_repository.delete(receipt_id=receipt.id)

    def update_status(self, receipt: Receipt, status: bool) -> None:
        receipt.get_state().close_receipt(receipt=receipt)
        self.receipt_repository.update(receipt_id=receipt.id, status=status)

    def add_product(self, receipt: Receipt, product: Product,
                    quantity: int) -> Receipt:
        product_for_receipt = ProductForReceipt(
            id=product.id,
            quantity=quantity,
            price=product.price,
            discount_price=product.discount)
        product_for_receipt.total = product_for_receipt.get_price()
        product_for_receipt.discount_total = product_for_receipt.get_discounted_price()

        receipt = receipt.get_state().add_item(
            receipt=receipt, item_for_receipt=product_for_receipt)
        return self.receipt_repository.add_product(receipt=receipt)

    def add_combo_product(self, receipt: Receipt,
                          combo: ComboCampaign,
                          quantity: int) -> Receipt:
        combo_for_receipt = ComboForReceipt(
            id=combo.id,
            products=combo.products,
            quantity=quantity,
            price=combo.get_price(),
            discount_price=combo.real_price())
        combo_for_receipt.total = combo_for_receipt.get_price()
        combo_for_receipt.discount_total = combo_for_receipt.get_discounted_price()
        receipt = receipt.get_state().add_item(
            receipt=receipt,
            item_for_receipt=combo_for_receipt)
        return self.receipt_repository.add_product(receipt=receipt)

    def add_gift_product(self, receipt: Receipt,
                         gift: BuyNGetNCampaign,
                         quantity: int) -> Receipt:
        gift_for_receipt = GiftForReceipt(
            id=gift.id,
            buy_product=gift.buy_product,
            gift_product=gift.gift_product,
            quantity=quantity,
            price=gift.get_price(),
            discount_price=gift.real_price())
        gift_for_receipt.total = gift_for_receipt.get_price()
        gift_for_receipt.discount_total = gift_for_receipt.get_discounted_price()
        receipt = receipt.get_state().add_item(
            receipt=receipt,
            item_for_receipt=gift_for_receipt)
        return self.receipt_repository.add_product(receipt=receipt)

    def delete_item(self, receipt: Receipt, item_id: str) -> None:
        receipt.get_state().delete_item(receipt=receipt, item_id=item_id)
        return self.receipt_repository.delete_item(receipt=receipt)