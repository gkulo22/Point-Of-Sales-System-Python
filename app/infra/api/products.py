from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.exceptions.products_exceptions import (
    GetProductError,
    ProductCreationError,
)
from app.core.facade import POSCore
from app.core.schemas.products_schema import (
    CreateProductRequest,
    CreateProductResponse,
    GetAllProductResponse,
    GetOneProductResponse,
    UpdateProductPriceRequest,
)
from app.infra.dependables import get_core

products_api = APIRouter()



class ProductBase(BaseModel):
    name: str
    barcode: str
    price: float

@products_api.post('/', status_code=201,
                   response_model=CreateProductResponse)
def create_product(request: ProductBase,
                   core: POSCore = Depends(get_core)) -> CreateProductResponse:
    try:
        return core.create_product(request=CreateProductRequest(**request.dict()))
    except ProductCreationError as exc:
        raise HTTPException(status_code=409, detail=exc.message)


@products_api.get('/', status_code=200,
                  response_model=GetAllProductResponse)
def get_products(core: POSCore = Depends(get_core)) -> GetAllProductResponse:
    return core.get_all_products()


@products_api.get("/{product_id}",
                  status_code=200,
                  response_model=GetOneProductResponse)
def get_one_product(product_id: str,
                    core: POSCore = Depends(get_core)) -> GetOneProductResponse:
    try:
        return core.get_one_product(product_id)
    except GetProductError as exc:
        raise HTTPException(status_code=404, detail=exc.message)



class ProductPriceBase(BaseModel):
    price: float


@products_api.patch('/{product_id}', status_code=200)
def update_product_price(product_id: str,
                         request: ProductPriceBase,
                         core: POSCore = Depends(get_core)) -> None:
    try:
        core.update_product_price(product_id,
                    UpdateProductPriceRequest(**request.dict()))
    except GetProductError as exc:
        raise HTTPException(status_code=404, detail=exc.message)