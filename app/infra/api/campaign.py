from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.exceptions.campaign_exceptions import GetCampaignErrorMessage
from app.core.exceptions.products_exceptions import GetProductError
from app.core.facade import POSCore
from app.core.models.product import NumProduct
from app.core.schemas.campaign_schema import (
    AddProductInComboRequest,
    AddProductInComboResponse,
    AddProductInDiscountResponse,
    CreateBuyNGetNProductRequest,
    CreateBuyNGetNProductResponse,
    CreateComboRequest,
    CreateComboResponse,
    CreateDiscountRequest,
    CreateDiscountResponse,
    CreateReceiptDiscountRequest,
    CreateReceiptDiscountResponse,
    GetAllCampaignsResponse,
    GetOneCampaignResponse,
)
from app.infra.dependables import get_core

campaign_api = APIRouter()



class ComboBase(BaseModel):
    discount: float


@campaign_api.post('/combo', status_code=201,
                   response_model=CreateComboResponse)
def create_combo_campaign(request: ComboBase,
                          core: POSCore = Depends(get_core)) -> CreateComboResponse:
    return core.create_combo_campaign(request=CreateComboRequest(**request.dict()))



class ProductForComboBase(BaseModel):
    product_id: str
    quantity: int


@campaign_api.post('/combo/{campaign_id}/{product}',
                   status_code=201,
                   response_model=AddProductInComboResponse)
def add_product_to_combo(campaign_id: str,
                         request: ProductForComboBase,
            core: POSCore = Depends(get_core)) -> AddProductInComboResponse:
    try:
        return core.add_product_to_combo(campaign_id=campaign_id,
                    request=AddProductInComboRequest(**request.dict()))
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except GetProductError as exc:
        raise HTTPException(status_code=404, detail=exc.message)



class ReceiptDiscountBase(BaseModel):
    discount: int
    amount: int


@campaign_api.post('/receipt_discount',
                   status_code=201,
                   response_model=CreateReceiptDiscountResponse)
def create_receipt_discount_campaign(request: ReceiptDiscountBase,
            core: POSCore = Depends(get_core)) -> CreateReceiptDiscountResponse:
    return core.create_receipt_discount_campaign(
        request=CreateReceiptDiscountRequest(**request.dict()))




class DiscountBase(BaseModel):
    discount: int


@campaign_api.post('/discount',
                   status_code=201,
                   response_model=CreateDiscountResponse)
def create_discount_campaign(request: DiscountBase,
        core: POSCore = Depends(get_core)) -> CreateDiscountResponse:
    return core.create_discount_campaign(
        request=CreateDiscountRequest(**request.dict()))



@campaign_api.post('/discount/{campaign_id}/{product_id}',
                   status_code=201,
                   response_model=AddProductInDiscountResponse)
def add_product_to_discount(campaign_id: str,
                            product_id: str,
            core: POSCore = Depends(get_core)) -> AddProductInDiscountResponse:
    try:
        return core.add_product_to_discount(campaign_id=campaign_id,
                                            product_id=product_id)
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except GetProductError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@campaign_api.delete('/discount/{campaign_id}/{product_id}',
                     status_code=200)
def delete_product_from_discount(campaign_id: str,
                                 product_id: str,
                                 core: POSCore = Depends(get_core)) -> None:
    try:
        return core.delete_product_from_discount(
            campaign_id=campaign_id,
            product_id=product_id)
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except GetProductError as exc:
        raise HTTPException(status_code=404, detail=exc.message)



class BuyNGetNProductBase(BaseModel):
    product: NumProduct
    gift: NumProduct


@campaign_api.post('/buy_n_get_n', status_code=201,
                   response_model=CreateBuyNGetNProductResponse)
def create_buy_n_get_n_campaign(request: BuyNGetNProductBase,
             core: POSCore = Depends(get_core)) -> CreateBuyNGetNProductResponse:
    return core.create_buy_n_get_n_campaign(
        request=CreateBuyNGetNProductRequest(
            product=request.product, gift=request.gift))


@campaign_api.get('/{campaign_id}',
                  status_code=200,
                  response_model=GetOneCampaignResponse)
def get_one_campaign(campaign_id: str,
                     core: POSCore = Depends(get_core)) -> GetOneCampaignResponse:
    try:
        return core.get_one_campaign(campaign_id=campaign_id)
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)



@campaign_api.get('', status_code=200,
                  response_model=GetAllCampaignsResponse)
def get_all_campaigns(core: POSCore = Depends(get_core)) -> GetAllCampaignsResponse:
    return core.get_all_campaigns()


@campaign_api.delete('/{campaign_id}', status_code=200)
def delete_campaign(campaign_id: str,
                    core: POSCore = Depends(get_core)) -> None:
    try:
        core.delete_campaigns(campaign_id=campaign_id)
    except GetCampaignErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)

