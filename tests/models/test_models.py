import unittest
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class ICalculatePrice(Protocol):
    id: str

    def get_price(self) -> float:
        pass

    def get_discounted_price(self) -> Optional[float]:
        pass

@dataclass
class DummyProduct(ICalculatePrice):
    id: str
    price: float
    discounted_price: Optional[float]

    def get_price(self) -> float:
        return self.price

    def get_discounted_price(self) -> Optional[float]:
        return self.discounted_price


class TestICalculatePrice(unittest.TestCase):
    def setUp(self) -> None:
        self.product = DummyProduct(id="p1", price=100.0,
                                    discounted_price=80.0)
        self.no_discount_product = DummyProduct(id="p2", price=100.0,
                                                discounted_price=None)
        self.zero_discount_product = DummyProduct(id="p3", price=100.0,
                                                  discounted_price=100.0)
        self.high_discount_product = DummyProduct(id="p4", price=100.0,
                                                  discounted_price=50.0)

    def test_get_price(self) -> None:
        self.assertEqual(self.product.get_price(), 100.0)
        self.assertEqual(self.no_discount_product.get_price(), 100.0)
        self.assertEqual(self.zero_discount_product.get_price(), 100.0)
        self.assertEqual(self.high_discount_product.get_price(), 100.0)

    def test_get_discounted_price(self) -> None:
        self.assertEqual(self.product.get_discounted_price(), 80.0)
        self.assertIsNone(self.no_discount_product.get_discounted_price())
        self.assertEqual(self.zero_discount_product.get_discounted_price(), 100.0)
        self.assertEqual(self.high_discount_product.get_discounted_price(), 50.0)

    def test_no_discount_product(self) -> None:
        self.assertIsNone(self.no_discount_product.get_discounted_price())
        self.assertEqual(self.no_discount_product.get_price(), 100.0)

    def test_zero_discount(self) -> None:
        self.assertEqual(self.zero_discount_product.get_discounted_price(), 100.0)
        self.assertEqual(self.zero_discount_product.get_price(), 100.0)

    def test_high_discount(self) -> None:
        self.assertEqual(self.high_discount_product.get_discounted_price(), 50.0)
        self.assertEqual(self.high_discount_product.get_price(), 100.0)

    def test_invalid_id(self) -> None:
        empty_id_product = DummyProduct(id="", price=100.0, discounted_price=50.0)
        self.assertEqual(empty_id_product.get_price(), 100.0)
        self.assertEqual(empty_id_product.get_discounted_price(), 50.0)


if __name__ == "__main__":
    unittest.main()