import unittest
from unittest.mock import MagicMock

from app.core.interactors.shift_interactor import ShiftInteractor
from app.core.models import NO_ID
from app.core.models.shift import Shift
from app.core.services.shift_service import ShiftService


class TestShiftInteractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # This method will run once before any tests
        pass

    def setUp(self) -> None:
        # This method will run before every individual test
        self.mock_shift_service = MagicMock(spec=ShiftService)
        self.mock_shift_service.create_shift.return_value = Shift(id="shift_1", receipts=[])
        self.mock_shift_service.get_one_shift.return_value = Shift(id="shift_1", receipts=[])
        self.mock_shift_service.update_status.return_value = None
        self.shift_interactor = ShiftInteractor(shift_service=self.mock_shift_service)

    def test_execute_create(self) -> None:
        shift = self.shift_interactor.execute_create()
        self.mock_shift_service.create_shift.assert_called_once_with(shift=Shift(id=NO_ID, receipts=[]))
        self.assertNotEqual(shift.id, NO_ID)
        self.assertEqual(shift.receipts, [])

    def test_execute_get_one(self) -> None:
        shift = self.shift_interactor.execute_get_one("shift_1")
        self.mock_shift_service.get_one_shift.assert_called_once_with(shift_id="shift_1")
        self.assertEqual(shift.id, "shift_1")
        self.assertEqual(shift.receipts, [])

    def test_execute_change_status(self) -> None:
        self.shift_interactor.execute_change_status("shift_1", True)
        self.mock_shift_service.get_one_shift.assert_called_once_with(shift_id="shift_1")
        self.mock_shift_service.update_status.assert_called_once_with(shift=Shift(id="shift_1", receipts=[]),
                                                                      status=True)

    @classmethod
    def tearDownClass(cls) -> None:
        # This method will run once after all tests
        pass

    def tearDown(self) -> None:
        # This method will run after each individual test
        pass


if __name__ == "__main__":
    unittest.main()