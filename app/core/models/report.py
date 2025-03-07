from abc import abstractmethod
from dataclasses import dataclass
from typing import List

from app.core.exceptions.shift_exceptions import ShiftOpenedErrorMessage
from app.core.models.product import NumProduct
from app.core.models.receipt import Receipt
from app.core.schemas.report_schema import ReportResponse
from app.core.services.shift_service import ShiftService
from app.core.state.shift_state import OpenShiftState


@dataclass
class Report:
    def make_report(self, shift_service: ShiftService) -> ReportResponse:
        receipts = self.get_shift_data(shift_service)
        revenue = self._get_revenue(receipts)
        sold_count = self._get_sold_count(receipts)

        response = ReportResponse(
            number_of_receipts=len(receipts),
            revenue=revenue,
            sold_product_count=sold_count)
        return response


    def _get_revenue(self, receipts: List[Receipt]) -> dict[str, float]:
        result = {}
        revenue = float(sum(
            receipt.get_discounted_price() or receipt.get_price() for
            receipt in
            receipts))

        result["GEL"] = revenue
        return result

    def _get_sold_count(self, receipts: List[Receipt]) -> List[NumProduct]:
        ret_list: List[NumProduct] = []
        for receipt in receipts:
            for item in receipt.items:
                existing_product = next((p for p in ret_list
                                         if p.product_id == item.id),
                                         None)

                if existing_product:
                    existing_product.num += item.quantity
                else:
                    product = NumProduct(product_id=item.id,
                                         num=item.quantity)
                    ret_list.append(product)

        return ret_list

    @abstractmethod
    def get_shift_data(self, shift_service: ShiftService) -> List[Receipt]:
        pass



class XReport(Report):
    def get_shift_data(self, shift_service: ShiftService) -> List[Receipt]:
        shifts = shift_service.get_all_shifts()
        receipts = []
        for shift in shifts:
            receipts += shift.receipts
        return receipts

class ZReport(Report):
    def __init__(self, shift_id: str) -> None:
        super().__init__()
        self.shift_id = shift_id

    def get_shift_data(self, shift_service: ShiftService) -> List[Receipt]:
        shift = shift_service.get_one_shift(self.shift_id)
        if isinstance(shift.state, OpenShiftState):
            raise ShiftOpenedErrorMessage(shift_id=shift.id)

        return shift.receipts



