# import unittest
#
# import pytest
# import httpx
# from unittest.mock import AsyncMock
#
# from app.core.services.payment_service import PaymentService
#
#
# @pytest.mark.asyncio
# async def test_calculate_exchange_rate_success():
#     service = PaymentService()
#     mock_response = AsyncMock(spec=httpx.Response)
#     mock_response.json.return_value = {"ask": "5.25"}
#     service._client.get = AsyncMock(return_value=mock_response)
#
#     result = await service._calculate_exchange_rate("USD", "BRL")
#     assert result == {"ask": "5.25"}
#
#
# @pytest.mark.asyncio
# async def test_calculate_exchange_rate_error():
#     service = PaymentService()
#     mock_request = AsyncMock(spec=httpx.Request)
#     mock_response = AsyncMock(spec=httpx.Response)
#     service._client.get = AsyncMock(side_effect=httpx.HTTPStatusError("API is down", request=mock_request, response=mock_response))
#
#     result = await service._calculate_exchange_rate("USD", "BRL")
#     assert result == {"error": "API is down"}
#
#
# @pytest.mark.asyncio
# async def test_pay_success():
#     service = PaymentService()
#     service._calculate_exchange_rate = AsyncMock(return_value={"ask": "5.25"})
#
#     result = await service.pay("USD", "BRL", 100)
#     assert result == 525.0
#
#
# @pytest.mark.asyncio
# async def test_pay_error():
#     service = PaymentService()
#     service._calculate_exchange_rate = AsyncMock(return_value={"error": "Invalid currency"})
#
#     with pytest.raises(Exception, match="Invalid currency"):
#         await service.pay("USD", "BRL", 100)
#
# if __name__ == "__main__":
#     unittest.main()