import unittest
from unittest.mock import MagicMock, Mock

from app.core.exceptions.shift_exceptions import GetShiftErrorMessage
from app.core.models.receipt import Receipt
from app.core.models.shift import Shift
from app.core.repositories.shift_repository import IShiftRepository
from app.core.services.shift_service import ShiftService


# Instead of implementing a mock class, use MagicMock with spec
class TestShiftService(unittest.TestCase):
    def setUp(self) -> None:
        # Use MagicMock with spec to ensure type compatibility
        self.shift_repository = MagicMock(spec=IShiftRepository)
        self.shift_service = ShiftService(shift_repository=self.shift_repository)

    def test_create_shift(self) -> None:
        shift = Shift(id="s1", state=Mock(), receipts=[])
        self.shift_repository.create.return_value = shift

        result = self.shift_service.create_shift(shift=shift)
        self.assertEqual(result, shift)
        self.shift_repository.create.assert_called_once_with(shift=shift)

    def test_get_one_shift_found(self) -> None:
        shift = Shift(id="s1", state=Mock(), receipts=[])
        self.shift_repository.get_one.return_value = shift

        result = self.shift_service.get_one_shift(shift_id="s1")
        self.assertEqual(result, shift)
        self.shift_repository.get_one.assert_called_once_with(shift_id="s1")

    def test_get_one_shift_not_found(self) -> None:
        self.shift_repository.get_one.return_value = None

        with self.assertRaises(GetShiftErrorMessage):
            self.shift_service.get_one_shift(shift_id="s1")

        self.shift_repository.get_one.assert_called_once_with(shift_id="s1")

    def test_get_all_shifts(self) -> None:
        shifts = [
            Shift(id="s1", state=Mock(), receipts=[]),
            Shift(id="s2", state=Mock(), receipts=[])
        ]
        self.shift_repository.get_all.return_value = shifts

        result = self.shift_service.get_all_shifts()
        self.assertEqual(result, shifts)
        self.shift_repository.get_all.assert_called_once()

    def test_update_status(self) -> None:  # Added return type
        shift = Shift(id="s1", state=Mock(), receipts=[])
        # Fix: proper way to mock a method
        shift.state.change_status = Mock()

        self.shift_repository.update = Mock()

        self.shift_service.update_status(shift=shift, status=True)

        shift.state.change_status.assert_called_once_with(shift)
        self.shift_repository.update.assert_called_once_with(shift_id="s1", status=True)

    def test_add_receipt(self) -> None:  # Added return type
        shift = Shift(id="s1", state=Mock(), receipts=[])
        receipt = Receipt(id="r1", shift_id="1",
                          items=[], total=100.0, discount_total=None)

        # Fix: proper way to mock a method
        shift.state.add_item = Mock()
        self.shift_repository.add_receipt = Mock(return_value=shift)

        result = self.shift_service.add_receipt(shift=shift, receipt=receipt)

        shift.state.add_item.assert_called_once_with(shift=shift, receipt=receipt)
        self.assertEqual(result, shift)
        self.shift_repository.add_receipt.assert_called_once_with(shift=shift)


if __name__ == "__main__":
    unittest.main()