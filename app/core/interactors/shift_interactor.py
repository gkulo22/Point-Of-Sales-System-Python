from dataclasses import dataclass

from app.core.models import NO_ID
from app.core.models.shift import Shift
from app.core.services.shift_service import ShiftService


@dataclass
class ShiftInteractor:
    shift_service: ShiftService

    def execute_create(self) -> Shift:
        shift = Shift(id=NO_ID, receipts=[])
        return self.shift_service.create_shift(shift=shift)

    def execute_get_one(self, shift_id: str) -> Shift:
        return self.shift_service.get_one_shift(shift_id=shift_id)

    def execute_change_status(self, shift_id: str, status: bool) -> None:
        shift = self.shift_service.get_one_shift(shift_id=shift_id)
        self.shift_service.update_status(shift=shift, status=status)

