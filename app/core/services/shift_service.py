from dataclasses import dataclass
from typing import List

from app.core.exceptions.shift_exceptions import GetShiftErrorMessage
from app.core.models.receipt import Receipt
from app.core.models.shift import Shift
from app.core.repositories.shift_repository import IShiftRepository


@dataclass
class ShiftService:
    shift_repository: IShiftRepository

    def create_shift(self, shift: Shift) -> Shift:
        return self.shift_repository.create(shift=shift)

    def get_one_shift(self, shift_id: str) -> Shift:
        shift = self.shift_repository.get_one(shift_id=shift_id)
        if not shift:
            raise GetShiftErrorMessage(shift_id=shift_id)

        return shift

    def get_all_shifts(self) -> List[Shift]:
        return self.shift_repository.get_all()

    def update_status(self, shift: Shift, status: bool) -> None:
        shift.state.change_status(shift)
        self.shift_repository.update(shift_id=shift.id, status=status)

    def add_receipt(self, shift: Shift, receipt: Receipt) -> Shift:
        shift.state.add_item(shift=shift, receipt=receipt)
        return self.shift_repository.add_receipt(shift=shift)