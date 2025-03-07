from dataclasses import dataclass
from typing import List

from app.core.exceptions.products_exceptions import (
    GetProductError,
    ProductCreationError,
)
from app.core.models.product import Product
from app.core.repositories.product_repository import IProductRepository


@dataclass
class ProductService:
    product_repository: IProductRepository

    def create_product(self, product: Product) -> Product:
        if self.product_repository.has_barcode(product.barcode):
            raise ProductCreationError(barcode=product.barcode)

        product = self.product_repository.create(product)
        return product

    def get_one_product(self, product_id: str) -> Product:
        product = self.product_repository.get_one(product_id=product_id)
        if not product:
            raise GetProductError(product_id=product_id)

        return product

    def get_all_products(self) -> List[Product]:
        return self.product_repository.get_all()

    def update_product(self, product: Product, price: float) -> None:
        self.product_repository.update(product_id=product.id, price=price)