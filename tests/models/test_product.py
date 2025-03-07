import unittest

from pydantic import ValidationError

from app.core.models.product import (
    DiscountedProduct,
    NumProduct,
    Product,
    ProductDecorator,
)


class TestProductModels(unittest.TestCase):
    def test_product_get_price_without_discount(self) -> None:
        p = Product(id="p1", name="Test Product", barcode="123456", price=100.0, discount=None)
        self.assertEqual(p.get_price(), 100.0)

    def test_product_get_price_with_discount_value(self) -> None:
        p = Product(id="p2", name="Test Product 2", barcode="654321", price=100.0, discount=80.0)
        self.assertEqual(p.get_price(), 100.0)

    def test_product_decorator_get_price(self) -> None:
        p = Product(id="p3", name="Test Product 3", barcode="111111", price=200.0, discount=None)
        decorator = ProductDecorator(inner_product=p)
        self.assertEqual(decorator.get_price(), 200.0)

    def test_discounted_product_get_price(self) -> None:
        p = Product(id="p4", name="Test Product 4", barcode="222222", price=100.0, discount=None)
        discounted = DiscountedProduct(inner_product=p, discount=10)
        self.assertAlmostEqual(discounted.get_price(), 90.0)

    def test_num_product_creation(self) -> None:
        num_product = NumProduct(product_id="p5", num=3)
        self.assertEqual(num_product.product_id, "p5")
        self.assertEqual(num_product.num, 3)

    def test_num_product_validation(self) -> None:
        with self.assertRaises(ValidationError):
            NumProduct(product_id="p6", num="not_an_int")


if __name__ == "__main__":
    unittest.main()