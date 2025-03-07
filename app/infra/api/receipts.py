from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.exceptions.campaign_exceptions import GetCampaignErrorMessage
from app.core.exceptions.products_exceptions import GetProductError
from app.core.exceptions.receipt_exceptions import (
    GetReceiptErrorMessage,
    ItemNotFoundInReceiptError,
    ReceiptClosedErrorMessage,
)
from app.core.facade import POSCore
from app.core.schemas.receipt_schema import (
    AddComboInReceiptRequest,
    AddGiftInReceiptRequest,
    AddItemInReceiptResponse,
    AddProductInReceiptRequest,
    CreateReceiptRequest,
    CreateReceiptResponse,
    GetOneReceiptResponse,
)
from app.infra.dependables import get_core

receipts_api = APIRouter()



class ReceiptBase(BaseModel):
    shift_id: str


@receipts_api.post("", status_code=201,
                   response_model=CreateReceiptResponse)
def create_receipt(request: ReceiptBase,
                   core: POSCore = Depends(get_core)) -> CreateReceiptResponse:
    return core.create_receipt(request=CreateReceiptRequest(**request.dict()))



class ProductForReceiptBase(BaseModel):
    product_id: str
    quantity: int


@receipts_api.post("/{receipt_id}/product",
                   status_code=201,
                   response_model=AddItemInReceiptResponse)
def add_product_in_receipt(receipt_id: str,
                   request: ProductForReceiptBase,
                   core: POSCore = Depends(get_core)) -> AddItemInReceiptResponse:
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Invalid quantity")


    try:
        return core.add_product_in_receipt(receipt_id=receipt_id,
                request=AddProductInReceiptRequest(**request.dict()))
    except GetReceiptErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ReceiptClosedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)
    except GetProductError as exc:
        raise HTTPException(status_code=404, detail=exc.message)



class ComboForReceiptBase(BaseModel):
    combo_id: str
    quantity: int



@receipts_api.post("/{receipt_id}/combo",
                   status_code=201,
                   response_model=AddItemInReceiptResponse)
def add_combo_in_receipt(receipt_id: str,
                   request: ComboForReceiptBase,
                   core: POSCore = Depends(get_core)) -> AddItemInReceiptResponse:
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Invalid quantity")

    try:
        return core.add_combo_in_receipt(receipt_id=receipt_id,
                    request=AddComboInReceiptRequest(**request.dict()))
    except GetReceiptErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ReceiptClosedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)



class GiftForReceiptBase(BaseModel):
    gift_campaign_id: str
    quantity: int


@receipts_api.post("/{receipt_id}/buy_n_get_n",
                   status_code=201,
                   response_model=AddItemInReceiptResponse)
def add_gift_in_receipt(receipt_id: str,
                   request: GiftForReceiptBase,
                   core: POSCore = Depends(get_core)) -> AddItemInReceiptResponse:
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Invalid quantity")

    try:
        return core.add_gift_in_receipt(receipt_id=receipt_id,
            request=AddGiftInReceiptRequest(**request.dict()))
    except GetReceiptErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ReceiptClosedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)



@receipts_api.delete("/{receipt_id}/{item_id}", status_code=200)
def delete_item_from_receipt(receipt_id: str,
                             item_id: str,
                             core: POSCore = Depends(get_core)) -> None:
    try:
        core.delete_item_from_receipt(receipt_id=receipt_id, item_id=item_id)
    except GetReceiptErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ReceiptClosedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)
    except ItemNotFoundInReceiptError as exc:
        raise HTTPException(status_code=404, detail=exc.message)



@receipts_api.get("/{receipt_id}", status_code=200,
                  response_model=GetOneReceiptResponse)
def get_one_receipt(receipt_id: str,
                    core: POSCore = Depends(get_core)) -> GetOneReceiptResponse:
    try:
        return core.get_one_receipt(receipt_id=receipt_id)
    except GetReceiptErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)





@receipts_api.delete("/{receipt_id}", status_code=200)
def delete_receipt(receipt_id: str,
                   core: POSCore = Depends(get_core)) -> None:
    try:
        core.delete_receipt(receipt_id=receipt_id)
    except GetReceiptErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ReceiptClosedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)