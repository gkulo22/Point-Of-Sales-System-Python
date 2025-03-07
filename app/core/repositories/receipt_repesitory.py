from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.models.receipt import Receipt


@dataclass
class IReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> Receipt:
        pass

    def get_one(self, receipt_id: str) -> Optional[Receipt]:
        pass

    def get_all(self) -> List[Receipt]:
        pass

    def delete(self, receipt_id: str) -> None:
        pass

    def update(self, receipt_id: str, status: bool) -> None:
        pass

    def add_product(self, receipt: Receipt) -> Receipt:
        pass

    def delete_item(self, receipt: Receipt) -> None:
        pass

