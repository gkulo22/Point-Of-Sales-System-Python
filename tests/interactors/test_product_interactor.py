import unittest
from unittest.mock import MagicMock

from app.core.interactors.product_interactor import ProductInteractor
from app.core.models import NO_ID
from app.core.models.product import Product, ProductDecorator


class TestProductInteractor(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_product_service = MagicMock()
        self.mock_campaign_service = MagicMock()
        self.interactor = ProductInteractor(
            product_service=self.mock_product_service,
            campaign_service=self.mock_campaign_service
        )

    def test_execute_create(self) -> None:
        name = "Test Product"
        barcode = "1234567890123"
        price = 9.99
        expected_product = Product(id=NO_ID, name=name, barcode=barcode, price=price)
        created_product = Product(id="1", name=name, barcode=barcode, price=price)
        self.mock_product_service.create_product.return_value = created_product

        result = self.interactor.execute_create(name, barcode, price)

        self.mock_product_service.create_product.assert_called_once()
        actual_product = self.mock_product_service.create_product.call_args[1]['product']
        self.assertEqual(vars(actual_product), vars(expected_product))
        self.assertEqual(result, created_product)

    def test_execute_update(self) -> None:
        product_id = "1"
        new_price = 19.99
        product = Product(id=product_id, name="Test", barcode="123", price=9.99)
        self.mock_product_service.get_one_product.return_value = product

        self.interactor.execute_update(product_id, new_price)

        self.mock_product_service.get_one_product.assert_called_once_with(product_id=product_id)
        self.mock_product_service.update_product.assert_called_once_with(product=product, price=new_price)

    def test_execute_get_one(self) -> None:
        product_id = "1"
        product = Product(id=product_id, name="Test", barcode="123", price=9.99)
        decorated_product = ProductDecorator(inner_product=product)
        self.mock_product_service.get_one_product.return_value = product
        self.mock_campaign_service.get_campaign_product.return_value = decorated_product

        result = self.interactor.execute_get_one(product_id)

        self.mock_product_service.get_one_product.assert_called_once_with(product_id=product_id)
        self.mock_campaign_service.get_campaign_product.assert_called_once_with(product=product)
        self.assertEqual(result, decorated_product)

    def test_execute_get_all(self) -> None:
        product_list = [
            Product(id="1", name="Product 1", barcode="111", price=9.99),
            Product(id="2", name="Product 2", barcode="222", price=19.99)
        ]
        self.mock_product_service.get_all_products.return_value = product_list

        result = self.interactor.execute_get_all()

        self.mock_product_service.get_all_products.assert_called_once()
        self.assertEqual(result, product_list)


if __name__ == "__main__":
    unittest.main()