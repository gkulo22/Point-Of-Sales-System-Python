import unittest

from app.core.models.receipt import (
    ComboForReceipt,
    GiftForReceipt,
    ProductForReceipt,
    Receipt,
)
from app.core.state.receipt_state import ClosedReceiptState, OpenReceiptState


class TestProductForReceipt(unittest.TestCase):
    def test_get_price(self) -> None:
        product = ProductForReceipt(id="p1", quantity=3, price=10.0)
        self.assertEqual(product.get_price(), 30.0)

    def test_get_discounted_price_with_discount(self) -> None:
        product = ProductForReceipt(id="p1", quantity=3, price=10.0, discount_price=8.0)
        self.assertEqual(product.get_discounted_price(), 24.0)

    def test_get_discounted_price_none(self) -> None:
        product = ProductForReceipt(id="p1", quantity=3, price=10.0, discount_price=None)
        self.assertIsNone(product.get_discounted_price())


class TestComboForReceipt(unittest.TestCase):
    def test_get_price(self) -> None:
        combo = ComboForReceipt(id="c1", products=[], quantity=2, price=15.0, discount_price=12.0)
        self.assertEqual(combo.get_price(), 30.0)

    def test_get_discounted_price(self) -> None:
        combo = ComboForReceipt(id="c1", products=[], quantity=2, price=15.0, discount_price=12.0)
        self.assertEqual(combo.get_discounted_price(), 24.0)


class TestGiftForReceipt(unittest.TestCase):
    def test_get_price(self) -> None:
        buy_product = ProductForReceipt(id="p1", quantity=2, price=10.0)
        gift_product = ProductForReceipt(id="p2", quantity=2, price=5.0)
        gift_receipt = GiftForReceipt(id="g1", buy_product=buy_product, gift_product=gift_product, quantity=1, price=0)

        # Fix the float + None issue by ensuring both operands are float
        buy_price = buy_product.get_price() or 0.0
        gift_price = gift_product.get_price() or 0.0
        expected_price = (buy_price + gift_price) * 1

        self.assertEqual(gift_receipt.get_price(), expected_price)

    def test_get_discounted_price(self) -> None:
        buy_product = ProductForReceipt(id="p1", quantity=2, price=10.0)
        gift_product = ProductForReceipt(id="p2", quantity=2, price=5.0)
        gift_receipt = GiftForReceipt(id="g1", buy_product=buy_product, gift_product=gift_product, quantity=2, price=0)
        expected_discounted = buy_product.get_price() * 2
        self.assertEqual(gift_receipt.get_discounted_price(), expected_discounted)


class TestReceipt(unittest.TestCase):
    def test_get_price(self) -> None:
        product = ProductForReceipt(id="p1", quantity=2, price=10.0)
        combo = ComboForReceipt(id="c1", products=[], quantity=1, price=15.0, discount_price=12.0)
        gift = GiftForReceipt(id="g1", buy_product=product, gift_product=product, quantity=1, price=0)
        items = [product, combo, gift]
        receipt = Receipt(id="r1", shift_id="s1", items=items, total=0)
        expected_total = product.get_price() + combo.get_price() + gift.get_price()
        self.assertEqual(receipt.get_price(), expected_total)

    def test_get_discounted_price_effective(self) -> None:
        product = ProductForReceipt(id="p1", quantity=2, price=10.0, discount_price=8.0)
        combo = ComboForReceipt(id="c1", products=[], quantity=1, price=15.0, discount_price=12.0)
        items = [product, combo]
        receipt = Receipt(id="r1", shift_id="s1", items=items, total=0)

        # Fix the error by handling possible None values
        product_discounted = product.get_discounted_price() or product.get_price()
        combo_discounted = combo.get_discounted_price() or combo.get_price()
        discounted_total = product_discounted + combo_discounted

        self.assertEqual(receipt.get_discounted_price(), discounted_total)

    def test_get_discounted_price_none(self) -> None:
        product = ProductForReceipt(id="p1", quantity=2, price=10.0)
        combo = ComboForReceipt(id="c1", products=[], quantity=1, price=15.0, discount_price=15.0)
        items = [product, combo]
        receipt = Receipt(id="r1", shift_id="s1", items=items, total=0)
        self.assertIsNone(receipt.get_discounted_price())

    def test_get_state_open(self) -> None:
        product = ProductForReceipt(id="p1", quantity=1, price=10.0)
        receipt = Receipt(id="r1", shift_id="s1", items=[product], total=10, status=True)
        state = receipt.get_state()
        self.assertIsInstance(state, OpenReceiptState)

    def test_get_state_closed(self) -> None:
        product = ProductForReceipt(id="p1", quantity=1, price=10.0)
        receipt = Receipt(id="r1", shift_id="s1", items=[product], total=10, status=False)
        state = receipt.get_state()
        self.assertIsInstance(state, ClosedReceiptState)


if __name__ == "__main__":
    unittest.main()