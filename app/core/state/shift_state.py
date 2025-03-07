from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.models.receipt import Receipt
    from app.core.models.shift import Shift

from app.core.exceptions.shift_exceptions import ShiftClosedErrorMessage


class ShiftState(ABC):
    @abstractmethod
    def add_item(self, shift: 'Shift', receipt: 'Receipt') -> 'Shift':
        pass

    @abstractmethod
    def change_status(self, shift: 'Shift') -> 'Shift':
        pass


class OpenShiftState(ShiftState):
    def add_item(self, shift: 'Shift', receipt: 'Receipt') -> 'Shift':
        shift.receipts.append(receipt)
        return shift

    def change_status(self, shift: 'Shift') -> 'Shift':
        shift.state = ClosedShiftState()
        return shift


class ClosedShiftState(ShiftState):
    def add_item(self, shift: 'Shift', receipt: 'Receipt') -> 'Shift':
        raise ShiftClosedErrorMessage(shift_id=shift.id)

    def change_status(self, shift: 'Shift') -> 'Shift':
        raise ShiftClosedErrorMessage(shift_id=shift.id)
