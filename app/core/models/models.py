from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class ICalculatePrice(Protocol):
    id: str
    def get_price(self) -> float:
        pass

    def get_discounted_price(self) -> Optional[float]:
        pass


