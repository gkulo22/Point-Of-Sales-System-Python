from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions.shift_exceptions import (
    GetShiftErrorMessage,
    ShiftOpenedErrorMessage,
)
from app.core.facade import POSCore
from app.core.schemas.report_schema import ReportResponse
from app.infra.dependables import get_core

reports_api = APIRouter()


@reports_api.get('/Xreport', status_code=200,
                 response_model=ReportResponse)
def get_xreport(core: POSCore = Depends(get_core)) -> ReportResponse:
    return core.get_xreport()

@reports_api.get('/Zreport/{shift_id}', status_code=200,
                 response_model=ReportResponse)
def get_zreport(shift_id: str, core: POSCore = Depends(get_core)) -> ReportResponse:
    try:
        return core.get_zreport(shift_id=shift_id)
    except GetShiftErrorMessage as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    except ShiftOpenedErrorMessage as exc:
        raise HTTPException(status_code=403, detail=exc.message)