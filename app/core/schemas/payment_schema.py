from pydantic import BaseModel


class PaymentRequest(BaseModel):
    to_currency: str
    amount: float
