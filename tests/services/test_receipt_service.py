import unittest
from unittest.mock import MagicMock

import pytest

from app.core.exceptions.receipt_exceptions import (
    GetReceiptErrorMessage,
    ReceiptClosedErrorMessage,
)
from app.core.models.campaign import BuyNGetNCampaign, CampaignType, ComboCampaign
from app.core.models.product import Product
from app.core.models.receipt import (
    ProductForReceipt,
    Receipt,
)
from app.core.repositories.receipt_repesitory import IReceiptRepository
from app.core.services.receipt_service import ReceiptService


class TestReceiptService(unittest.TestCase):

    def test_create_receipt(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)
        receipt_repository.create.return_value = mock_receipt

        result = service.create_receipt(mock_receipt)

        receipt_repository.create.assert_called_once_with(receipt=mock_receipt)
        self.assertEqual(result, mock_receipt)

    def test_get_one_receipt(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)
        receipt_repository.get_one.return_value = mock_receipt

        result = service.get_one_receipt("receipt-1")

        receipt_repository.get_one.assert_called_once_with(receipt_id="receipt-1")
        self.assertEqual(result, mock_receipt)

    def test_get_one_receipt_not_found_with_exception(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        receipt_repository.get_one.return_value = None

        with pytest.raises(Exception):
            service.get_one_receipt("receipt-1")

        receipt_repository.get_one.assert_called_once_with(receipt_id="receipt-1")

    def test_delete_receipt(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0, status=True)
        receipt_repository.delete.return_value = None

        service.delete_receipt(mock_receipt)

        receipt_repository.delete.assert_called_once_with(receipt_id="receipt-1")

    def test_add_product(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        mock_product = Product(id="prod-1", name="Test Product", barcode="12345", price=10.0, discount=0.0)
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)

        receipt_repository.add_product.return_value = mock_receipt

        result = service.add_product(mock_receipt, mock_product, 2)

        receipt_repository.add_product.assert_called_once()
        self.assertEqual(result, mock_receipt)

    def test_add_combo_product(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        # Fix: Use an actual CampaignType enum value instead of the class itself
        mock_combo = ComboCampaign(id="combo-1", campaign_type=CampaignType.COMBO, products=[], discount=5.0)
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)

        receipt_repository.add_product.return_value = mock_receipt

        result = service.add_combo_product(mock_receipt, mock_combo, 2)

        receipt_repository.add_product.assert_called_once()
        self.assertEqual(result, mock_receipt)

    def test_delete_receipt_closed(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0, status=False)

        with pytest.raises(ReceiptClosedErrorMessage):
            service.delete_receipt(mock_receipt)

    def test_get_one_receipt_not_found_with_specific_error(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)
        receipt_repository.get_one.return_value = None

        with pytest.raises(GetReceiptErrorMessage):
            service.get_one_receipt("receipt-1")

    def test_update_status(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)
        mock_receipt = MagicMock(spec=Receipt)
        mock_receipt.id = "receipt-1"
        mock_state = MagicMock()
        mock_receipt.get_state.return_value = mock_state

        service.update_status(mock_receipt, False)
        mock_state.close_receipt.assert_called_once_with(receipt=mock_receipt)
        receipt_repository.update.assert_called_once_with(receipt_id="receipt-1", status=False)

    def test_add_product_zero_quantity(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        mock_product = Product(id="prod-1", name="Test Product", barcode="12345", price=10.0, discount=None)
        mock_receipt = MagicMock(spec=Receipt)
        mock_state = MagicMock()
        mock_receipt.get_state.return_value = mock_state

        service.add_product(mock_receipt, mock_product, 0)
        mock_state.add_item.assert_called()

    def test_add_gift_product(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        # Create ProductForReceipt objects instead of using Product directly
        mock_product = Product(id="prod-1", name="Test Product", barcode="12345", price=10.0, discount=0.0)
        mock_gift_product = Product(id="gift-1", name="Gift Product", barcode="67890", price=5.0, discount=0.0)

        product_for_receipt = ProductForReceipt(id=mock_product.id, quantity=1, price=mock_product.price)
        gift_for_receipt = ProductForReceipt(id=mock_gift_product.id, quantity=1, price=mock_gift_product.price)

        # Fix campaign_type and use ProductForReceipt objects
        mock_gift = BuyNGetNCampaign(
            id="gift-1",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=product_for_receipt,
            gift_product=gift_for_receipt
        )

        mock_receipt = MagicMock(spec=Receipt)
        mock_state = MagicMock()
        mock_receipt.get_state.return_value = mock_state
        receipt_repository.add_product.return_value = mock_receipt

        result = service.add_gift_product(mock_receipt, mock_gift, 2)
        mock_state.add_item.assert_called()
        self.assertEqual(result, mock_receipt)

    def test_delete_item(self) -> None:
        receipt_repository = MagicMock(spec=IReceiptRepository)
        service = ReceiptService(receipt_repository=receipt_repository)

        mock_receipt = MagicMock(spec=Receipt)
        mock_state = MagicMock()
        mock_receipt.get_state.return_value = mock_state

        service.delete_item(mock_receipt, "item-1")
        mock_state.delete_item.assert_called_once_with(receipt=mock_receipt, item_id="item-1")
        receipt_repository.delete_item.assert_called_once_with(receipt=mock_receipt)


if __name__ == "__main__":
    unittest.main()