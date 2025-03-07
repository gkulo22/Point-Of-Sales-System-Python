import sqlite3

from fastapi import FastAPI

from app.core.facade import POSCore
from app.infra.api.campaign import campaign_api
from app.infra.api.payments import payment_api
from app.infra.api.products import products_api
from app.infra.api.receipts import receipts_api
from app.infra.api.reports import reports_api
from app.infra.api.shifts import shifts_api
from app.infra.data.sqlite import SqliteRepoFactory


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(products_api, prefix="/products", tags=["Product"])
    app.include_router(campaign_api, prefix="/campaign", tags=["Campaign"])
    app.include_router(receipts_api, prefix="/receipts", tags=["Receipt"])
    app.include_router(shifts_api, prefix="/shifts", tags=["Shift"])
    app.include_router(payment_api, prefix="/pay", tags=["Payment"])
    app.include_router(reports_api, prefix="/reports", tags=["Report"])

    connection = sqlite3.connect("oop.db", check_same_thread=False)
    database = SqliteRepoFactory(connection=connection)
    # database = InMemoryRepoFactory()
    app.state.infra = database
    app.state.core = POSCore.create(database)

    return app