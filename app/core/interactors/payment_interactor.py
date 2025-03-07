from dataclasses import dataclass

from app.core.services.payment_service import PaymentService
from app.core.services.receipt_service import ReceiptService
from app.core.services.shift_service import ShiftService


@dataclass
class PaymentInteractor:
    payment_service: PaymentService
    receipt_service: ReceiptService
    shift_service: ShiftService

    async def execute_pay(self,
                          receipt_id: str,
                          to_currency: str) -> float:
        receipt = self.receipt_service.get_one_receipt(
            receipt_id=receipt_id)
        amount = receipt.get_price()
        if receipt.get_discounted_price() is not None:
            amount = receipt.get_discounted_price()

        if to_currency == "GEL":
            converted_amount = amount
        else:
            converted_amount = await self.payment_service.pay(
                from_currency="GEL",
                to_currency= to_currency,
                amount=amount)
        self.receipt_service.update_status(receipt=receipt, status=False)
        shift = self.shift_service.get_one_shift(shift_id=receipt.shift_id)
        self.shift_service.add_receipt(receipt=receipt, shift=shift)
        return converted_amount



