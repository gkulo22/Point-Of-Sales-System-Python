from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions.receipt_exceptions import ReceiptClosedErrorMessage
from app.core.facade import POSCore
from app.infra.dependables import get_core

payment_api = APIRouter()

@payment_api.post('/usd/{receipt_id}')
async def pay_usd(receipt_id: str,
                  core: POSCore = Depends(get_core)) -> Any:
    try:
        return await core.pay_receipt(receipt_id=receipt_id,
                                      to_currency="USD")
    except ReceiptClosedErrorMessage as exc:
        return HTTPException(status_code=403, detail=exc.message)

@payment_api.post('/eur/{receipt_id}')
async def pay_eur(receipt_id: str,
                  core: POSCore = Depends(get_core)) -> Any:
    try:
        return await core.pay_receipt(receipt_id=receipt_id,
                                      to_currency="EUR")
    except ReceiptClosedErrorMessage as exc:
        return HTTPException(status_code=403, detail=exc.message)

@payment_api.post('/gel/{receipt_id}')
async def pay_gel(receipt_id: str,
                  core: POSCore = Depends(get_core)) -> Any:
    try:
        return await core.pay_receipt(receipt_id=receipt_id,
                                      to_currency="GEL")
    except ReceiptClosedErrorMessage as exc:
        return HTTPException(status_code=403, detail=exc.message)

