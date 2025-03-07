import unittest
from unittest.mock import MagicMock

from app.core.exceptions.products_exceptions import (
    GetProductError,
    ProductCreationError,
)
from app.core.models.product import Product
from app.core.repositories.product_repository import IProductRepository
from app.core.services.product_service import ProductService


class TestProductService(unittest.TestCase):

    def test_create_product(self) -> None:
        product_repository = MagicMock(spec=IProductRepository)
        service = ProductService(product_repository=product_repository)

        mock_product = Product(id="prod-1", name="Test Product",
                               barcode="12345", price=10.0, discount=0.0)

        product_repository.has_barcode.return_value = False
        product_repository.create.return_value = mock_product

        result = service.create_product(mock_product)

        product_repository.has_barcode.assert_called_once_with("12345")
        product_repository.create.assert_called_once_with(mock_product)

        self.assertEqual(result, mock_product)

    def test_create_product_existing_barcode(self) -> None:
        product_repository = MagicMock(spec=IProductRepository)
        service = ProductService(product_repository=product_repository)

        mock_product = Product(id="prod-1", name="Test Product",
                               barcode="12345", price=10.0, discount=0.0)

        product_repository.has_barcode.return_value = True

        with self.assertRaises(ProductCreationError):
            service.create_product(mock_product)

        product_repository.has_barcode.assert_called_once_with("12345")

    def test_get_one_product(self) -> None:
        product_repository = MagicMock(spec=IProductRepository)
        service = ProductService(product_repository=product_repository)

        mock_product = Product(id="prod-1", name="Test Product",
                               barcode="12345", price=10.0, discount=0.0)

        product_repository.get_one.return_value = mock_product

        result = service.get_one_product("prod-1")

        product_repository.get_one.assert_called_once_with(product_id="prod-1")
        self.assertEqual(result, mock_product)

    def test_get_one_product_not_found(self) -> None:
        product_repository = MagicMock(spec=IProductRepository)
        service = ProductService(product_repository=product_repository)

        product_repository.get_one.return_value = None

        with self.assertRaises(GetProductError):
            service.get_one_product("prod-1")

        product_repository.get_one.assert_called_once_with(product_id="prod-1")

    def test_get_all_products(self) -> None:
        product_repository = MagicMock(spec=IProductRepository)
        service = ProductService(product_repository=product_repository)

        mock_products = [
            Product(id="prod-1", name="Product 1", barcode="12345",
                    price=10.0, discount=0.0),
            Product(id="prod-2", name="Product 2", barcode="67890",
                    price=15.0, discount=0.0)
        ]

        product_repository.get_all.return_value = mock_products

        result = service.get_all_products()

        product_repository.get_all.assert_called_once()
        self.assertEqual(result, mock_products)

    def test_update_product(self) -> None:
        product_repository = MagicMock(spec=IProductRepository)
        service = ProductService(product_repository=product_repository)

        mock_product = Product(id="prod-1", name="Test Product",
                               barcode="12345", price=10.0, discount=0.0)

        service.update_product(mock_product, 20.0)

        product_repository.update.assert_called_once_with(product_id="prod-1",
                                                          price=20.0)


if __name__ == "__main__":
    unittest.main()