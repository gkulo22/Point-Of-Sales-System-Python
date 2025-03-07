from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.models.shift import Shift


@dataclass
class IShiftRepository(Protocol):
    def create(self, shift: Shift) -> Shift:
        pass

    def get_one(self, shift_id: str) -> Optional[Shift]:
        pass

    def get_all(self) -> List[Shift]:
        pass

    def delete(self, shift_id: str) -> None:
        pass

    def update(self, shift_id: str, status: bool) -> None:
        pass

    def add_receipt(self, shift: Shift) -> Shift:
        pass