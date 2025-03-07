from dataclasses import dataclass
from typing import Any

import httpx

BASE_URL = "https://economia.awesomeapi.com.br"


@dataclass
class PaymentService:
    _client = httpx.AsyncClient()


    async def _calculate_exchange_rate(self,
                                from_currency: str,
                                to_currency: str) -> Any:
        url = f"{BASE_URL}/json/last/{from_currency}-{to_currency}"
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get(f"{from_currency}{to_currency}",
                            {"error": "Invalid currency"})
        except httpx.HTTPStatusError:
            return {"error": "API is down"}
        except Exception:
            return {"error": "Unexpected error"}


    async def pay(self, from_currency: str, to_currency: str, amount: float) -> float:
        rate_data = await self._calculate_exchange_rate(from_currency, to_currency)
        if "error" in rate_data:
            raise Exception(rate_data["error"])

        rate = float(rate_data["ask"])
        converted = round(amount * rate, 2)

        return converted