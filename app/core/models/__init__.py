from typing import Union

from app.core.models.receipt import ComboForReceipt, GiftForReceipt, ProductForReceipt

ReceiptItem = Union[ProductForReceipt, ComboForReceipt, GiftForReceipt]
NO_ID = "NO_ID"
