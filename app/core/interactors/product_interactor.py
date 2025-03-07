from dataclasses import dataclass
from typing import List

from app.core.models import NO_ID
from app.core.models.product import Product, ProductDecorator
from app.core.services.campaign_service import CampaignService
from app.core.services.product_service import ProductService


@dataclass
class ProductInteractor:
    product_service: ProductService
    campaign_service: CampaignService

    def execute_create(self, name: str,
                       barcode: str,
                       price: float) -> Product:
        product = Product(
            id=NO_ID,
            name=name,
            barcode=barcode,
            price=price)
        return self.product_service.create_product(product=product)

    def execute_update(self,
                       product_id: str,
                       price: float) -> None:
        product = self.product_service.get_one_product(
            product_id=product_id)
        self.product_service.update_product(
            product=product, price=price)

    def execute_get_one(self, product_id: str) -> ProductDecorator:
        product = self.product_service.get_one_product(
            product_id=product_id)
        product_decorator = self.campaign_service.get_campaign_product(
            product=product)
        return product_decorator

    def execute_get_all(self) -> List[Product]:
        return self.product_service.get_all_products()