import unittest
from dataclasses import dataclass
from typing import List, Optional, cast

from app.core.exceptions.receipt_exceptions import (
    ItemNotFoundInReceiptError,
    ReceiptClosedErrorMessage,
)
from app.core.models.models import ICalculatePrice
from app.core.models.receipt import ProductForReceipt, Receipt
from app.core.state.receipt_state import (
    ClosedReceiptState,
    OpenReceiptState,
    ReceiptState,
)


# Create mock class that properly extends Receipt
@dataclass(kw_only=True)
class MockReceipt(Receipt):
    id: str
    items: List[ICalculatePrice]
    total: float = 0.0
    discount_total: Optional[float] = None
    shift_id: str = "mock-shift"
    status: bool = True

    def get_state(self) -> ReceiptState:
        if self.status:
            return OpenReceiptState()
        else:
            return ClosedReceiptState()


    def get_state(self) -> ReceiptState:
        if self.status:
            return OpenReceiptState()
        else:
            return ClosedReceiptState()


# Create mock item that properly implements ICalculatePrice with all needed attributes
@dataclass
class MockItem(ProductForReceipt):
    id: str
    quantity: int
    total: float
    price: float = 0.0
    discount_price: Optional[float] = None
    discount_total: Optional[float] = None

    def __post_init__(self) -> None:
        # Ensure price is calculated based on quantity if not provided
        if self.price == 0.0 and self.quantity > 0:
            self.price = self.total / self.quantity


class TestReceiptState(unittest.TestCase):
    def setUp(self) -> None:
        self.item1 = MockItem(id="i1", quantity=2, total=100.0, discount_total=80.0)
        self.item2 = MockItem(id="i2", quantity=1, total=50.0)

        self.open_receipt = MockReceipt(id="r1", items=[self.item1], status=True)
        self.closed_receipt = MockReceipt(id="r2", items=[self.item1], status=False)

    def test_open_receipt_add_item(self) -> None:
        new_item = MockItem(id="i3", quantity=1, total=30.0)

        # Use get_state() to get the state object
        receipt_state = self.open_receipt.get_state()
        updated_receipt = receipt_state.add_item(receipt=self.open_receipt,
                                                 item_for_receipt=new_item)

        self.assertEqual(len(updated_receipt.items), 2)
        self.assertEqual(updated_receipt.items[-1].id, "i3")

    def test_open_receipt_add_existing_item(self) -> None:
        existing_item = MockItem(id="i1", quantity=1, total=50.0)

        # Use get_state() to get the state object
        receipt_state = self.open_receipt.get_state()
        updated_receipt = receipt_state.add_item(receipt=self.open_receipt,
                                                 item_for_receipt=existing_item)

        # Safely access attributes by using concrete types that have these attributes
        item = cast(MockItem, updated_receipt.items[0])
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.total, 150.0)

    def test_open_receipt_delete_item(self) -> None:
        # Safely access attributes by using concrete types that have these attributes
        initial_item = cast(MockItem, self.open_receipt.items[0])
        self.assertEqual(initial_item.quantity, 2)

        # Use get_state() to get the state object
        receipt_state = self.open_receipt.get_state()
        updated_receipt = receipt_state.delete_item(receipt=self.open_receipt,
                                                    item_id="i1")

        # Safely access attributes by using concrete types that have these attributes
        updated_item = cast(MockItem, updated_receipt.items[0])
        self.assertEqual(updated_item.quantity, 1)
        self.assertEqual(len(updated_receipt.items), 1)

        # Get state from the updated receipt
        updated_state = updated_receipt.get_state()
        updated_receipt2 = updated_state.delete_item(receipt=updated_receipt,
                                                     item_id="i1")
        self.assertEqual(len(updated_receipt2.items), 0)

    def test_open_receipt_delete_item_not_found(self) -> None:
        # Use get_state() to get the state object
        receipt_state = self.open_receipt.get_state()
        with self.assertRaises(ItemNotFoundInReceiptError):
            receipt_state.delete_item(receipt=self.open_receipt, item_id="i99")

    def test_open_receipt_close(self) -> None:
        # Use get_state() to get the state object
        receipt_state = self.open_receipt.get_state()
        updated_receipt = receipt_state.close_receipt(receipt=self.open_receipt)

        # Check that the receipt's status has been updated
        self.assertFalse(updated_receipt.status)

        # The state should now be a ClosedReceiptState
        updated_state = updated_receipt.get_state()
        self.assertIsInstance(updated_state, ClosedReceiptState)

    def test_closed_receipt_add_item(self) -> None:
        new_item = MockItem(id="i3", quantity=1, total=30.0)

        # Use get_state() to get the state object
        receipt_state = self.closed_receipt.get_state()
        with self.assertRaises(ReceiptClosedErrorMessage):
            receipt_state.add_item(receipt=self.closed_receipt,
                                   item_for_receipt=new_item)

    def test_closed_receipt_delete_item(self) -> None:
        # Use get_state() to get the state object
        receipt_state = self.closed_receipt.get_state()
        with self.assertRaises(ReceiptClosedErrorMessage):
            receipt_state.delete_item(receipt=self.closed_receipt, item_id="i1")

    def test_closed_receipt_close(self) -> None:
        # Use get_state() to get the state object
        receipt_state = self.closed_receipt.get_state()
        with self.assertRaises(ReceiptClosedErrorMessage):
            receipt_state.close_receipt(receipt=self.closed_receipt)


if __name__ == "__main__":
    unittest.main()
