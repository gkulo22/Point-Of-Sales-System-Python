from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.models.receipt import Receipt

from app.core.exceptions.receipt_exceptions import (
    ItemNotFoundInReceiptError,
    ReceiptClosedErrorMessage,
)
from app.core.models.models import ICalculatePrice


class ReceiptState(ABC):
    @abstractmethod
    def add_item(self, receipt: 'Receipt',
                 item_for_receipt: ICalculatePrice) -> 'Receipt':
        pass

    @abstractmethod
    def delete_item(self, receipt: 'Receipt', item_id: str) -> 'Receipt':
        pass

    @abstractmethod
    def close_receipt(self, receipt: 'Receipt') -> 'Receipt':
        pass


class ClosedReceiptState(ReceiptState):
    def add_item(self, receipt: 'Receipt',
                 item_for_receipt: ICalculatePrice) -> 'Receipt':
        raise ReceiptClosedErrorMessage(receipt_id=receipt.id)

    def delete_item(self, receipt: 'Receipt', item_id: str) -> 'Receipt':
        raise ReceiptClosedErrorMessage(receipt_id=receipt.id)

    def close_receipt(self, receipt: 'Receipt') -> 'Receipt':
        raise ReceiptClosedErrorMessage(receipt_id=receipt.id)


class OpenReceiptState(ReceiptState):
    def add_item(self, receipt: 'Receipt',
                 item_for_receipt: ICalculatePrice) -> 'Receipt':
        for item in receipt.items:
            if item.id == item_for_receipt.id:
                item.quantity += item_for_receipt.quantity
                item.total += item_for_receipt.total
                if (item.discount_total is not None
                        and item_for_receipt.discount_total is not None):
                    item.discount_total += item_for_receipt.discount_total

                receipt.total = receipt.get_price()
                receipt.discount_total = receipt.get_discounted_price()
                return receipt

        receipt.items.append(item_for_receipt)
        receipt.total = receipt.get_price()
        receipt.discount_total = receipt.get_discounted_price()
        return receipt

    def delete_item(self, receipt: 'Receipt', item_id: str) -> 'Receipt':
        for item in receipt.items:
            if item.id == item_id:
                item.quantity -= 1
                if item.quantity == 0:
                    receipt.items.remove(item)

                receipt.total = receipt.get_price()
                receipt.discount_total = receipt.get_discounted_price()
                return receipt

        raise ItemNotFoundInReceiptError(item_id=item_id)

    def close_receipt(self, receipt: 'Receipt') -> 'Receipt':
        receipt.status = False
        return receipt
