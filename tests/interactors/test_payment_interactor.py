import unittest
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.interactors.payment_interactor import PaymentInteractor
from app.core.schemas.payment_schema import PaymentRequest


class DummyReceipt:
    def __init__(self, price: float, discounted_price: Optional[float], shift_id: str) -> None:
        self._price = price
        self._discounted_price = discounted_price
        self.shift_id = shift_id

    def get_price(self) -> float:
        return float(self._price)  # Explicit conversion to float

    def get_discounted_price(self) -> float:
        if self._discounted_price is None:
            return float(self._price)  # Return price if discounted_price is None
        return float(self._discounted_price)  # Explicit conversion to float


class DummyShift:
    def __init__(self, shift_id: str) -> None:
        self.shift_id = shift_id


class TestPaymentInteractor:

    @pytest.mark.asyncio
    async def test_execute_pay_no_conversion(self) -> None:
        request = PaymentRequest(to_currency="GEL", amount=100.0)
        dummy_receipt = DummyReceipt(price=100.0, discounted_price=None, shift_id="shift_1")

        payment_service = AsyncMock()
        receipt_service = MagicMock()
        receipt_service.get_one_receipt.return_value = dummy_receipt
        receipt_service.update_status = MagicMock()
        shift_service = MagicMock()
        dummy_shift = DummyShift(shift_id="shift_1")
        shift_service.get_one_shift.return_value = dummy_shift
        shift_service.add_receipt = MagicMock()

        interactor = PaymentInteractor(
            payment_service=payment_service,
            receipt_service=receipt_service,
            shift_service=shift_service
        )

        result = await interactor.execute_pay(receipt_id="dummy_receipt_id", to_currency=request.to_currency)
        assert result == 100.0
        receipt_service.update_status.assert_called_once_with(receipt=dummy_receipt, status=False)
        shift_service.get_one_shift.assert_called_once_with(shift_id="shift_1")
        shift_service.add_receipt.assert_called_once_with(receipt=dummy_receipt, shift=dummy_shift)

    @pytest.mark.asyncio
    async def test_execute_pay_with_conversion(self) -> None:
        request = PaymentRequest(to_currency="USD", amount=100.0)
        dummy_receipt = DummyReceipt(price=200.0, discounted_price=180.0, shift_id="shift_2")

        payment_service = AsyncMock()
        payment_service.pay.return_value = 50.0
        receipt_service = MagicMock()
        receipt_service.get_one_receipt.return_value = dummy_receipt
        receipt_service.update_status = MagicMock()
        shift_service = MagicMock()
        dummy_shift = DummyShift(shift_id="shift_2")
        shift_service.get_one_shift.return_value = dummy_shift
        shift_service.add_receipt = MagicMock()

        interactor = PaymentInteractor(
            payment_service=payment_service,
            receipt_service=receipt_service,
            shift_service=shift_service
        )

        result = await interactor.execute_pay(receipt_id="dummy_receipt_id", to_currency=request.to_currency)
        payment_service.pay.assert_awaited_once_with(from_currency="GEL", to_currency="USD", amount=180.0)
        assert result == 50.0
        receipt_service.update_status.assert_called_once_with(receipt=dummy_receipt, status=False)
        shift_service.get_one_shift.assert_called_once_with(shift_id="shift_2")
        shift_service.add_receipt.assert_called_once_with(receipt=dummy_receipt, shift=dummy_shift)


if __name__ == "__main__":
    unittest.main()