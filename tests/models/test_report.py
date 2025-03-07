import unittest
from dataclasses import dataclass
from typing import List, Optional

from app.core.models.receipt import ProductForReceipt, Receipt
from app.core.models.report import XReport, ZReport
from app.core.schemas.report_schema import ReportResponse
from app.core.services.shift_service import ShiftService


@dataclass
class DummyShift:
    id: str
    receipts: List[Receipt]
    state: str

class DummyShiftService(ShiftService):
    def __init__(self, shifts: List[DummyShift]) -> None:
        self._shifts = shifts

    def get_all_shifts(self) -> List[DummyShift]:
        return self._shifts

    def get_one_shift(self, shift_id: str) -> Optional[DummyShift]:
        for shift in self._shifts:
            if shift.id == shift_id:
                return shift
        return None

class TestReport(unittest.TestCase):
    def setUp(self) -> None:
        self.product1_receipt1 = ProductForReceipt(id="p1", quantity=2, price=10.0)
        self.receipt1 = Receipt(
            id="r1",
            shift_id="s1",
            items=[self.product1_receipt1],
            total=20.0
        )
        self.product2_receipt2 = ProductForReceipt(id="p2", quantity=3, price=5.0)
        self.receipt2 = Receipt(
            id="r2",
            shift_id="s2",
            items=[self.product2_receipt2],
            total=15.0
        )
        self.shift1 = DummyShift(id="s1",
                                 receipts=[self.receipt1], state="some_state_value")
        self.shift2 = DummyShift(id="s2",
                                 receipts=[self.receipt2], state="some_state_value")
        self.dummy_shift_service = DummyShiftService(shifts=[self.shift1, self.shift2])

    def test_xreport_make_report(self) -> None:
        report = XReport()
        response: ReportResponse = report.make_report(shift_service=self.dummy_shift_service)
        self.assertEqual(response.number_of_receipts, 2)
        self.assertEqual(response.revenue.get("GEL"), 35.0)
        sold_counts = {np.product_id: np.num for np in response.sold_product_count}
        self.assertEqual(sold_counts.get("p1"), 2)
        self.assertEqual(sold_counts.get("p2"), 3)

    def test_zreport_make_report(self) -> None:
        report = ZReport(shift_id="s1")
        response: ReportResponse = report.make_report(shift_service=self.dummy_shift_service)
        self.assertEqual(response.number_of_receipts, 1)
        self.assertEqual(response.revenue.get("GEL"), 20.0)
        sold_counts = {np.product_id: np.num for np in response.sold_product_count}
        self.assertEqual(sold_counts.get("p1"), 2)
        self.assertNotIn("p2", sold_counts)

if __name__ == "__main__":
    unittest.main()