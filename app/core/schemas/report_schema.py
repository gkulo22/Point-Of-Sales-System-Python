from dataclasses import dataclass
from typing import List

from app.core.models.product import NumProduct


@dataclass
class ReportResponse:
    number_of_receipts: int
    revenue: dict[str, float]
    sold_product_count: List[NumProduct]
