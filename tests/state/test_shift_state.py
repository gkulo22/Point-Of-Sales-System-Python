import unittest
from dataclasses import dataclass, field
from typing import List, Optional, Protocol


# These are placeholder implementations based on the test usage
class ShiftClosedErrorMessage(Exception):
    pass


class ShiftState(Protocol):
    def add_item(self, shift: "Shift", receipt: "Receipt") -> None: ...
    def change_status(self, shift: "Shift") -> None: ...


class OpenShiftState:
    def add_item(self, shift: "Shift", receipt: "Receipt") -> None:
        shift.receipts.append(receipt)

    def change_status(self, shift: "Shift") -> None:
        shift.state = ClosedShiftState()


class ClosedShiftState:
    def add_item(self, shift: "Shift", receipt: "Receipt") -> None:
        raise ShiftClosedErrorMessage("Cannot add items to a closed shift")

    def change_status(self, shift: "Shift") -> None:
        raise ShiftClosedErrorMessage("Shift is already closed")


class Receipt(Protocol):
    id: str
    shift_id: str
    items: List[str]


class Shift(Protocol):
    id: str
    receipts: List["Receipt"]
    state: ShiftState


@dataclass
class DummyReceipt:
    # All required fields must be defined before fields with defaults
    shift_id: str
    items: List[str]
    id: str = "receipt1"


@dataclass
class DummyShift:
    id: str
    receipts: List[DummyReceipt] = field(default_factory=list)
    state: Optional[ShiftState] = None

    def __post_init__(self) -> None:
        if self.state is None:
            self.state = OpenShiftState()


class TestShiftState(unittest.TestCase):
    def setUp(self) -> None:
        self.shift = DummyShift(id="s1")
        # Provide all required positional arguments for a receipt
        self.receipt = DummyReceipt(shift_id="s1", items=[])

    def test_open_shift_add_item(self) -> None:
        self.assertIsInstance(self.shift.state, OpenShiftState)

        # Type: ignore added since we're using dummy classes for testing
        self.shift.state.add_item(self.shift, self.receipt)  # type: ignore
        self.assertEqual(len(self.shift.receipts), 1)
        # Compare the receipt id with the one provided in the dummy receipt
        self.assertEqual(self.shift.receipts[0].id, self.receipt.id)

    def test_open_shift_change_status(self) -> None:
        self.assertIsInstance(self.shift.state, OpenShiftState)
        self.shift.state.change_status(self.shift)  # type: ignore
        self.assertIsInstance(self.shift.state, ClosedShiftState)

    def test_closed_shift_add_item_raises(self) -> None:
        self.shift.state = ClosedShiftState()
        with self.assertRaises(ShiftClosedErrorMessage):
            self.shift.state.add_item(self.shift, self.receipt)  # type: ignore

    def test_closed_shift_change_status(self) -> None:
        self.shift.state = ClosedShiftState()
        with self.assertRaises(ShiftClosedErrorMessage):
            self.shift.state.change_status(self.shift)  # type: ignore


if __name__ == "__main__":
    unittest.main()
