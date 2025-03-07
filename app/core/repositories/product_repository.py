from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.models.product import Product


@dataclass
class IProductRepository(Protocol):
    def create(self, product: Product) -> Product:
        pass

    def get_one(self, product_id: str) -> Optional[Product]:
        pass

    def get_all(self) -> List[Product]:
        pass

    def update(self, product_id: str, price: float) -> None:
        pass

    def has_barcode(self, barcode: str) -> bool:
        pass