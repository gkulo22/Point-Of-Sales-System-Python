from dataclasses import dataclass
from typing import List, Optional

from app.core.models.models import ICalculatePrice
from app.core.models.receipt import Receipt
from app.core.state.shift_state import OpenShiftState, ShiftState


@dataclass
class Shift(ICalculatePrice):
    id: str
    receipts: List[Receipt]
    state: ShiftState = OpenShiftState()

    def get_price(self) -> float:
        return sum(
            receipt.get_discounted_price() or receipt.get_price() for receipt in
            self.receipts)

    def get_discounted_price(self) -> Optional[float]:
        return sum(
            receipt.get_discounted_price() or receipt.get_price() for receipt in
            self.receipts)
