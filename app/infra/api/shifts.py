from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions.shift_exceptions import (
    GetShiftErrorMessage,
    ShiftClosedErrorMessage,
)
from app.core.facade import POSCore
from app.core.schemas.shift_schema import (
    CreateShiftResponse,
    GetOneShiftResponse,
    UpdateShiftStateRequest,
)
from app.infra.dependables import get_core

shifts_api = APIRouter()


@shifts_api.post("", status_code=201,
                 response_model=CreateShiftResponse)
def create_shift(core: POSCore = Depends(get_core)) -> CreateShiftResponse:
    return core.create_shift()



@shifts_api.get("/{shift_id}", status_code=200,
                response_model=GetOneShiftResponse)
def get_one_shift(shift_id: str,
                    core: POSCore = Depends(get_core)) -> GetOneShiftResponse:
    try:
        return core.get_one_shift(shift_id=shift_id)
    except GetShiftErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)




@shifts_api.patch("/{shift_id}", status_code=200)
def close_shift(shift_id: str,
                  core: POSCore = Depends(get_core)) -> None:
    try:
        return core.update_shift_status(shift_id=shift_id,
                              request=UpdateShiftStateRequest(
                                  status=False
                                  )
                              )
    except GetShiftErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ShiftClosedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)