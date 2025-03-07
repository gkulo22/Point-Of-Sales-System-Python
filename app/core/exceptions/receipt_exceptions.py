from dataclasses import dataclass, field


@dataclass
class ItemNotFoundInReceiptError(Exception):
    item_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Item with id: {self.item_id} does not exist in receipt."


@dataclass
class GetReceiptErrorMessage(Exception):
    receipt_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Receipt with id: {self.receipt_id} does not exist."



@dataclass
class ReceiptClosedErrorMessage(Exception):
    receipt_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Receipt with id: {self.receipt_id} is closed."