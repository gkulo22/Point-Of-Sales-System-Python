from dataclasses import dataclass, field


@dataclass
class ProductCreationError(Exception):
    barcode: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Product with barcode: {self.barcode} already exists."


@dataclass
class GetProductError(Exception):
    product_id: str
    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"Product with id: {self.product_id} does not exist."
