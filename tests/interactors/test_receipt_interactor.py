import unittest
from unittest.mock import MagicMock

from app.core.interactors.receipt_interactor import ReceiptInteractor
from app.core.models.campaign import BuyNGetNCampaign, CampaignType, ComboCampaign
from app.core.models.product import DiscountedProduct, Product
from app.core.models.receipt import ProductForReceipt, Receipt
from app.core.services.campaign_service import CampaignService
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.core.services.shift_service import ShiftService


class TestReceiptInteractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # This method will run once before any tests
        pass

    def setUp(self) -> None:
        # This method will run before each individual test
        self.mock_receipt_service = MagicMock(spec=ReceiptService)
        self.mock_product_service = MagicMock(spec=ProductService)
        self.mock_shift_service = MagicMock(spec=ShiftService)
        self.mock_campaign_service = MagicMock(spec=CampaignService)

        self.receipt_interactor = ReceiptInteractor(
            receipt_service=self.mock_receipt_service,
            product_service=self.mock_product_service,
            shift_service=self.mock_shift_service,
            campaign_service=self.mock_campaign_service
        )

    def test_execute_create(self) -> None:
        shift_id = "shift_1"
        mock_shift = MagicMock()
        mock_shift.state = MagicMock()
        self.mock_shift_service.get_one_shift.return_value = mock_shift
        self.mock_receipt_service.create_receipt.return_value = Receipt(id="receipt_1",
                                                                        shift_id=shift_id, items=[],
                                                                        total=0.0)

        result = self.receipt_interactor.execute_create(shift_id)

        self.assertEqual(result.id, "receipt_1")
        self.assertEqual(result.shift_id, shift_id)
        self.mock_shift_service.get_one_shift.assert_called_once_with(shift_id=shift_id)

        expected_receipt = Receipt(id="NO_ID", shift_id=shift_id, items=[], total=0.0)
        self.mock_receipt_service.create_receipt.assert_called_once_with(receipt=expected_receipt)

    def test_execute_get_one(self) -> None:
        receipt_id = "receipt_1"
        expected_receipt = Receipt(id=receipt_id, shift_id="shift_1",
                                   items=[], total=0.0)

        # Mock the return value correctly
        self.mock_receipt_service.get_one_receipt.return_value = expected_receipt
        self.mock_campaign_service.get_campaign_receipt.return_value = expected_receipt  # Add this line

        result = self.receipt_interactor.execute_get_one(receipt_id)

        self.assertEqual(result.id, receipt_id)
        self.mock_receipt_service.get_one_receipt.assert_called_once_with(receipt_id=receipt_id)

    def test_execute_delete_item(self) -> None:
        receipt_id = "receipt_1"
        item_id = "item_1"
        receipt = Receipt(id=receipt_id, shift_id="shift_1", items=[], total=0.0)
        self.mock_receipt_service.get_one_receipt.return_value = receipt
        self.mock_receipt_service.delete_item.return_value = None

        self.receipt_interactor.execute_delete_item(receipt_id, item_id)

        self.mock_receipt_service.get_one_receipt.assert_called_once_with(receipt_id=receipt_id)
        self.mock_receipt_service.delete_item.assert_called_once_with(receipt=receipt, item_id=item_id)

    @unittest.mock.patch("pytest.mark.asyncio")
    def test_execute_addition_product(self, mock_asyncio: MagicMock) -> None:
        mock_product = Product(id="prod-1", name="Test Product", barcode="N/A", price=10.0, discount=0.0)
        mock_discounted_product = DiscountedProduct(inner_product=mock_product, discount=10)
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)

        self.mock_product_service.get_one_product.return_value = mock_product
        self.mock_campaign_service.get_campaign_product.return_value = mock_discounted_product
        self.mock_receipt_service.get_one_receipt.return_value = mock_receipt
        self.mock_receipt_service.add_product.return_value = mock_receipt
        self.mock_campaign_service.get_campaign_receipt.return_value = mock_receipt

        result = self.receipt_interactor.execute_addition_product("receipt-1", "prod-1", 2)

        self.mock_product_service.get_one_product.assert_called_once_with(product_id="prod-1")
        self.mock_campaign_service.get_campaign_product.assert_called_once_with(product=mock_product)
        self.mock_receipt_service.get_one_receipt.assert_called_once_with(receipt_id="receipt-1")
        self.mock_receipt_service.add_product.assert_called_once_with(receipt=mock_receipt,
                                                                      product=mock_product,
                                                                      quantity=2)
        self.mock_campaign_service.get_campaign_receipt.assert_called_once_with(receipt=mock_receipt)

        self.assertEqual(result, mock_receipt)

    def test_execute_delete(self) -> None:
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)
        self.mock_receipt_service.get_one_receipt.return_value = mock_receipt

        self.receipt_interactor.execute_delete("receipt-1")

        self.mock_receipt_service.get_one_receipt.assert_called_once_with(receipt_id="receipt-1")
        self.mock_receipt_service.delete_receipt.assert_called_once_with(receipt=mock_receipt)

    def test_execute_addition_combo(self) -> None:
        mock_combo = ComboCampaign(id="combo-1", campaign_type=CampaignType.DISCOUNT, products=[], discount=5.0)
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)

        self.mock_campaign_service.get_one_campaign.return_value = mock_combo
        self.mock_receipt_service.get_one_receipt.return_value = mock_receipt
        self.mock_receipt_service.add_combo_product.return_value = mock_receipt
        self.mock_campaign_service.get_campaign_receipt.return_value = mock_receipt

        result = self.receipt_interactor.execute_addition_combo("receipt-1",
                                                                "combo-1", 2)

        self.mock_campaign_service.get_one_campaign.assert_called_once_with(campaign_id="combo-1")
        self.mock_receipt_service.get_one_receipt.assert_called_once_with(receipt_id="receipt-1")
        self.mock_receipt_service.add_combo_product.assert_called_once_with(receipt=mock_receipt, combo=mock_combo,
                                                                            quantity=2)
        self.mock_campaign_service.get_campaign_receipt.assert_called_once_with(receipt=mock_receipt)

        self.assertEqual(result, mock_receipt)

    def test_execute_addition_gift(self) -> None:
        # Create proper ProductForReceipt objects for buy_product and gift_product
        buy_product = ProductForReceipt(id="prod-1", quantity=2,
                                        price=10.0, total=20.0)
        gift_product = ProductForReceipt(id="prod-2", quantity=1,
                                         price=5.0, total=5.0, discount_total=0)

        mock_gift = BuyNGetNCampaign(
            id="gift-1",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=buy_product,
            gift_product=gift_product
        )
        mock_receipt = Receipt(id="receipt-1", shift_id="shift-1", items=[], total=0.0)

        self.mock_campaign_service.get_one_campaign.return_value = mock_gift
        self.mock_receipt_service.get_one_receipt.return_value = mock_receipt
        self.mock_receipt_service.add_gift_product.return_value = mock_receipt
        self.mock_campaign_service.get_campaign_receipt.return_value = mock_receipt

        result = self.receipt_interactor.execute_addition_gift("receipt-1", "gift-1", 2)

        self.mock_campaign_service.get_one_campaign.assert_called_once_with(campaign_id="gift-1")
        self.mock_receipt_service.get_one_receipt.assert_called_once_with(receipt_id="receipt-1")
        self.mock_receipt_service.add_gift_product.assert_called_once_with(receipt=mock_receipt,
                                                                           gift=mock_gift,
                                                                           quantity=2)
        self.mock_campaign_service.get_campaign_receipt.assert_called_once_with(receipt=mock_receipt)

        self.assertEqual(result, mock_receipt)

    @classmethod
    def tearDownClass(cls) -> None:
        # This method will run once after all tests
        pass

    def tearDown(self) -> None:
        # This method will run after each individual test
        pass


if __name__ == "__main__":
    unittest.main()