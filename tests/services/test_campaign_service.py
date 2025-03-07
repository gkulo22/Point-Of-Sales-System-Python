import unittest
from typing import List, Protocol
from unittest.mock import MagicMock

from app.core.exceptions.campaign_exceptions import GetCampaignErrorMessage
from app.core.models.campaign import (
    BuyNGetNCampaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.product import DiscountedProduct, Product, ProductDecorator
from app.core.models.receipt import ProductForReceipt, Receipt
from app.core.services.campaign_service import (
    CampaignService,
)


# Define repository interfaces that our mocks should implement
class IProductDiscountCampaignRepository(Protocol):
    def get_campaign_with_product(self, product_id: str) -> DiscountCampaign | None:
        ...

    def get_one_campaign(self, campaign_id: str) -> DiscountCampaign | None:
        ...

    def delete_campaign(self, campaign_id: str) -> None:
        ...

    def create(self, discount_campaign: DiscountCampaign) -> DiscountCampaign:
        ...

    def add_product(self, product_id: str, campaign_id: str) -> DiscountCampaign:
        ...

    def delete_product(self, product_id: str, campaign_id: str) -> None:
        ...

    def get_all(self) -> List[DiscountCampaign]:
        ...


class IReceiptDiscountCampaignRepository(Protocol):
    def get_one_campaign(self, campaign_id: str) -> ReceiptCampaign | None:
        ...

    def delete_campaign(self, campaign_id: str) -> None:
        ...

    def create(self, receipt_campaign: ReceiptCampaign) -> ReceiptCampaign:
        ...

    def get_discount_on_amount(self, amount: int) -> ReceiptCampaign | None:
        ...

    def get_all(self) -> List[ReceiptCampaign]:
        ...


class IComboCampaignRepository(Protocol):
    def get_one_campaign(self, campaign_id: str) -> ComboCampaign | None:
        ...

    def delete_campaign(self, campaign_id: str) -> None:
        ...

    def create(self, combo_campaign: ComboCampaign) -> ComboCampaign:
        ...

    def add_product(self, product: ProductForReceipt,
                    campaign_id: str) -> ComboCampaign:
        ...

    def get_all(self) -> List[ComboCampaign]:
        ...


class IBuyNGetNCampaignRepository(Protocol):
    def get_one_campaign(self, campaign_id: str) -> BuyNGetNCampaign | None:
        ...

    def delete_campaign(self, campaign_id: str) -> None:
        ...

    def create(self, buy_n_get_n_campaign: BuyNGetNCampaign) -> BuyNGetNCampaign:
        ...

    def get_all(self) -> List[BuyNGetNCampaign]:
        ...


# Mock Repositories - implement the interfaces properly
class MockProductDiscountCampaignRepository(IProductDiscountCampaignRepository):
    def get_campaign_with_product(self, product_id: str) -> DiscountCampaign | None:
        return None

    def get_one_campaign(self, campaign_id: str) -> DiscountCampaign | None:
        return None

    def delete_campaign(self, campaign_id: str) -> None:
        pass

    def create(self, discount_campaign: DiscountCampaign) -> DiscountCampaign:
        return discount_campaign

    def add_product(self, product_id: str, campaign_id: str) -> DiscountCampaign:
        return DiscountCampaign(id=campaign_id, campaign_type=CampaignType.DISCOUNT, discount=10, products=[product_id])

    def delete_product(self, product_id: str, campaign_id: str) -> None:
        pass

    def get_all(self) -> List[DiscountCampaign]:
        return []


class MockReceiptDiscountCampaignRepository(IReceiptDiscountCampaignRepository):
    def get_one_campaign(self, campaign_id: str) -> ReceiptCampaign | None:
        return None

    def delete_campaign(self, campaign_id: str) -> None:
        pass

    def create(self, receipt_campaign: ReceiptCampaign) -> ReceiptCampaign:
        return receipt_campaign

    def get_discount_on_amount(self, amount: int) -> ReceiptCampaign | None:
        return None

    def get_all(self) -> List[ReceiptCampaign]:
        return []


class MockComboCampaignRepository(IComboCampaignRepository):
    def get_one_campaign(self, campaign_id: str) -> ComboCampaign | None:
        return None

    def delete_campaign(self, campaign_id: str) -> None:
        pass

    def create(self, combo_campaign: ComboCampaign) -> ComboCampaign:
        return combo_campaign

    def add_product(self, product: ProductForReceipt, campaign_id: str) -> ComboCampaign:
        return ComboCampaign(id=campaign_id,
                             campaign_type=CampaignType.COMBO,
                             discount=10,
                             products=[product])

    def get_all(self) -> List[ComboCampaign]:
        return []


class MockBuyNGetNCampaignRepository(IBuyNGetNCampaignRepository):
    def get_one_campaign(self, campaign_id: str) -> BuyNGetNCampaign | None:
        return None

    def delete_campaign(self, campaign_id: str) -> None:
        pass

    def create(self, buy_n_get_n_campaign: BuyNGetNCampaign) -> BuyNGetNCampaign:
        return buy_n_get_n_campaign

    def get_all(self) -> List[BuyNGetNCampaign]:
        return []


class TestCampaignService(unittest.TestCase):
    def setUp(self) -> None:
        self.product_discount_repo = MockProductDiscountCampaignRepository()
        self.receipt_discount_repo = MockReceiptDiscountCampaignRepository()
        self.combo_campaign_repo = MockComboCampaignRepository()
        self.buy_get_gift_repo = MockBuyNGetNCampaignRepository()

        self.campaign_service = CampaignService(
            product_discount_repo=self.product_discount_repo,
            receipt_discount_repo=self.receipt_discount_repo,
            combo_campaign_repo=self.combo_campaign_repo,
            buy_get_gift_repo=self.buy_get_gift_repo
        )

    def test_get_campaign_product_no_campaign(self) -> None:
        product = Product(id="p1", name="Product 1", barcode="123", price=100.0)
        result = self.campaign_service.get_campaign_product(product=product)
        self.assertIsInstance(result, ProductDecorator)
        self.assertEqual(result.inner_product, product)

    def test_get_campaign_product_with_discount(self) -> None:
        product = Product(id="p1", name="Product 1", barcode="123", price=100.0)
        # Use MagicMock instead of assigning to method
        mock_repo = MagicMock()
        mock_repo.get_campaign_with_product.return_value = DiscountCampaign(
            id="c1", campaign_type=CampaignType.DISCOUNT, discount=10, products=["p1"]
        )

        # Replace the repo with our mock
        self.campaign_service.product_discount_repo = mock_repo

        result = self.campaign_service.get_campaign_product(product=product)
        self.assertIsInstance(result, DiscountedProduct)
        # Check if result has discount attribute via hasattr
        self.assertTrue(hasattr(result, "discount"))
        self.assertEqual(result.discount, 10)
        self.assertEqual(result.inner_product, product)

    def test_get_campaign_receipt_no_discount(self) -> None:
        receipt = Receipt(id="123", shift_id="1", items=[], total=0.0)
        result = self.campaign_service.get_campaign_receipt(receipt=receipt)
        self.assertEqual(result.discount_total, None)

    def test_get_campaign_receipt_with_discount(self) -> None:
        receipt = Receipt(id="123", shift_id="1", items=[], total=0.0)
        mock_repo = MagicMock()
        mock_repo.get_discount_on_amount.return_value = ReceiptCampaign(
            id="c1", campaign_type=CampaignType.DISCOUNT, total=200, discount=20
        )

        # Replace the repo with our mock
        self.campaign_service.receipt_discount_repo = mock_repo

        result = self.campaign_service.get_campaign_receipt(receipt=receipt)
        self.assertEqual(result.discount_total, -20.0)

    def test_get_one_campaign_not_found(self) -> None:
        with self.assertRaises(GetCampaignErrorMessage):
            self.campaign_service.get_one_campaign(campaign_id="c1")

    def test_delete_campaign_not_found(self) -> None:
        with self.assertRaises(Exception):
            self.campaign_service.delete_campaign(campaign_id="c1")

    def test_create_discount_campaign(self) -> None:
        # Creating a mock discount campaign
        discount_campaign = DiscountCampaign(id="c1", campaign_type=CampaignType.DISCOUNT, discount=10, products=["p1"])

        # Create a mock repo
        mock_repo = MagicMock()
        mock_repo.create.return_value = discount_campaign

        # Replace the repo with our mock
        self.campaign_service.product_discount_repo = mock_repo

        # Calling the service method to create the campaign
        result = self.campaign_service.create_discount(discount_campaign)

        # Asserting that the returned result matches the mock campaign
        self.assertEqual(result.id, "c1")
        self.assertEqual(result.discount, 10)
        self.assertEqual(result.products, ["p1"])

    def test_add_product_in_combo(self) -> None:
        product = Product(id="p1", name="Product 1", barcode="123", price=100.0)
        # Create a proper ProductForReceipt object
        product_for_receipt = ProductForReceipt(id="p1", quantity=2, price=100)

        # Create a mock repo
        mock_repo = MagicMock()
        mock_repo.add_product.return_value = ComboCampaign(
            id="c1",
            campaign_type=CampaignType.COMBO,
            discount=10,
            products=[product_for_receipt]
        )

        # Replace the repo with our mock
        self.campaign_service.combo_campaign_repo = mock_repo

        result = self.campaign_service.add_product_in_combo(product=product,
                                                            quantity=2,
                                                            campaign_id="c1")
        self.assertEqual(result.id, "c1")
        self.assertEqual(len(result.products), 1)

    def test_add_product_in_discount(self) -> None:
        result = self.campaign_service.add_product_in_discount(product_id="p1",
                                                               campaign_id="c1")
        self.assertEqual(result.id, "c1")
        self.assertEqual(result.products, ["p1"])

    def test_create_combo(self) -> None:
        # Create proper ProductForReceipt object
        product = ProductForReceipt(id="p1", quantity=2, price=100)
        campaign = ComboCampaign(
            id="c1",
            campaign_type=CampaignType.COMBO,
            discount=10,
            products=[product]
        )

        # Use create_combo directly instead of patching
        mock_repo = MagicMock()
        mock_repo.create.return_value = campaign
        self.campaign_service.combo_campaign_repo = mock_repo

        result = self.campaign_service.create_combo(campaign)
        self.assertEqual(result, campaign)

    def test_execute_delete_from_discount(self) -> None:
        # Create a mock and attach it to delete_product
        mock_repo = MagicMock()
        self.campaign_service.product_discount_repo = mock_repo

        self.campaign_service.execute_delete_from_discount(campaign_id="c1",
                                                           product_id="p1")
        mock_repo.delete_product.assert_called_once_with(product_id="p1",
                                                         campaign_id="c1")

    def test_get_all_campaigns(self) -> None:
        discount_campaign = DiscountCampaign(
            id="c1",
            campaign_type=CampaignType.DISCOUNT,
            discount=10,
            products=["p1"]
        )
        receipt_campaign = ReceiptCampaign(
            id="c2",
            campaign_type=CampaignType.DISCOUNT,
            total=200,
            discount=20
        )
        # Create proper ProductForReceipt object
        product = ProductForReceipt(id="p1", quantity=2, price=100)
        combo_campaign = ComboCampaign(
            id="c3",
            campaign_type=CampaignType.COMBO,
            discount=10,
            products=[product]
        )

        # Create ProductForReceipt objects for buy/gift products
        buy_product = ProductForReceipt(id="p2", quantity=2, price=100)
        gift_product = ProductForReceipt(id="p3", quantity=1, price=50)

        buy_campaign = BuyNGetNCampaign(
            id="c4",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=buy_product,
            gift_product=gift_product
        )

        # Set up mock repos
        mock_product_repo = MagicMock()
        mock_product_repo.get_all.return_value = [discount_campaign]
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_receipt_repo = MagicMock()
        mock_receipt_repo.get_all.return_value = [receipt_campaign]
        self.campaign_service.receipt_discount_repo = mock_receipt_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_all.return_value = [combo_campaign]
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        mock_buy_repo = MagicMock()
        mock_buy_repo.get_all.return_value = [buy_campaign]
        self.campaign_service.buy_get_gift_repo = mock_buy_repo

        result = self.campaign_service.get_all_campaigns()
        self.assertEqual(len(result), 4)
        self.assertIn(discount_campaign, result)
        self.assertIn(receipt_campaign, result)
        self.assertIn(combo_campaign, result)
        self.assertIn(buy_campaign, result)


class TestCampaignServiceAdditional(unittest.TestCase):
    def setUp(self) -> None:
        self.product_discount_repo = MockProductDiscountCampaignRepository()
        self.receipt_discount_repo = MockReceiptDiscountCampaignRepository()
        self.combo_campaign_repo = MockComboCampaignRepository()
        self.buy_get_gift_repo = MockBuyNGetNCampaignRepository()

        self.campaign_service = CampaignService(
            product_discount_repo=self.product_discount_repo,
            receipt_discount_repo=self.receipt_discount_repo,
            combo_campaign_repo=self.combo_campaign_repo,
            buy_get_gift_repo=self.buy_get_gift_repo
        )

    def test_create_discount_campaign(self) -> None:
        discount_campaign = DiscountCampaign(id="c1",
                                             campaign_type=CampaignType.DISCOUNT, discount=10,
                                             products=["p1"])

        result = self.campaign_service.create_discount(discount_campaign)
        self.assertEqual(result.id, "c1")
        self.assertEqual(result.discount, 10)

    def test_create_combo_campaign(self) -> None:
        # Create proper ProductForReceipt objects
        product1 = ProductForReceipt(id="p1", quantity=1, price=100)
        product2 = ProductForReceipt(id="p2", quantity=1, price=100)

        combo_campaign = ComboCampaign(
            id="c2",
            campaign_type=CampaignType.COMBO,
            discount=15,
            products=[product1, product2]
        )

        result = self.campaign_service.create_combo(combo_campaign)
        self.assertEqual(result.id, "c2")
        self.assertEqual(result.discount, 15)

    def test_create_receipt_campaign(self) -> None:
        receipt_campaign = ReceiptCampaign(
            id="c3",
            campaign_type=CampaignType.DISCOUNT,
            total=200,
            discount=20
        )

        result = self.campaign_service.create_receipt_discount(receipt_campaign)
        self.assertEqual(result.id, "c3")
        self.assertEqual(result.discount, 20)

    def test_create_buy_n_get_n_campaign(self) -> None:
        # Create ProductForReceipt objects for buy/gift products
        buy_product = ProductForReceipt(id="p2", quantity=3, price=100)
        gift_product = ProductForReceipt(id="p3", quantity=1, price=50)

        buy_n_get_n_campaign = BuyNGetNCampaign(
            id="c4",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=buy_product,
            gift_product=gift_product
        )

        # Call the create method and assert the result
        result = self.campaign_service.create_buy_n_get_n(buy_n_get_n_campaign)
        self.assertEqual(result.id, "c4")

    def test_get_one_discount_campaign(self) -> None:
        # Create a mock discount campaign
        discount_campaign = DiscountCampaign(id="c1",
                                             campaign_type=CampaignType.DISCOUNT,
                                             discount=10,
                                             products=["p1"])

        # Create a mock repo
        mock_repo = MagicMock()
        mock_repo.get_one_campaign.return_value = discount_campaign
        self.campaign_service.product_discount_repo = mock_repo

        # Call the get_one_campaign method and assert the result
        result = self.campaign_service.get_one_campaign(campaign_id="c1")
        # Check if the returned object has expected attributes
        self.assertEqual(result.id, "c1")
        # Only check discount if it's a DiscountCampaign
        if isinstance(result, DiscountCampaign):
            self.assertEqual(result.discount, 10)

    def test_get_one_combo_campaign(self) -> None:
        # Create proper ProductForReceipt objects
        product1 = ProductForReceipt(id="p1", quantity=1, price=100)
        product2 = ProductForReceipt(id="p2", quantity=1, price=100)

        # Create a mock combo campaign
        combo_campaign = ComboCampaign(
            id="c2",
            campaign_type=CampaignType.COMBO,
            discount=15,
            products=[product1, product2]
        )

        # Set up repo mocks to handle the chain of responsibility pattern
        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = None
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_one_campaign.return_value = combo_campaign
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        # Call the get_one_campaign method and assert the result
        result = self.campaign_service.get_one_campaign(campaign_id="c2")
        self.assertEqual(result.id, "c2")
        # Only check discount if it's a ComboCampaign
        if isinstance(result, ComboCampaign):
            self.assertEqual(result.discount, 15)

    def test_get_one_receipt_campaign(self) -> None:
        # Create a mock receipt campaign
        receipt_campaign = ReceiptCampaign(
            id="c3",
            campaign_type=CampaignType.DISCOUNT,
            total=200,
            discount=20
        )

        # Set up repo mocks to handle the chain of responsibility pattern
        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = None
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_one_campaign.return_value = None
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        mock_receipt_repo = MagicMock()
        mock_receipt_repo.get_one_campaign.return_value = receipt_campaign
        self.campaign_service.receipt_discount_repo = mock_receipt_repo

        # Call the get_one_campaign method and assert the result
        result = self.campaign_service.get_one_campaign(campaign_id="c3")
        self.assertEqual(result.id, "c3")
        # Only check discount if it's a ReceiptCampaign
        if isinstance(result, ReceiptCampaign):
            self.assertEqual(result.discount, 20)

    def test_get_one_buy_n_get_n_campaign(self) -> None:
        # Create ProductForReceipt objects for buy/gift products
        buy_product = ProductForReceipt(id="p2", quantity=3, price=100)
        gift_product = ProductForReceipt(id="p3", quantity=1, price=50)

        # Create a mock Buy N Get N campaign
        buy_n_get_n_campaign = BuyNGetNCampaign(
            id="c4",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=buy_product,
            gift_product=gift_product
        )

        # Set up repo mocks to handle the chain of responsibility pattern
        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = None
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_one_campaign.return_value = None
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        mock_receipt_repo = MagicMock()
        mock_receipt_repo.get_one_campaign.return_value = None
        self.campaign_service.receipt_discount_repo = mock_receipt_repo

        mock_buy_repo = MagicMock()
        mock_buy_repo.get_one_campaign.return_value = buy_n_get_n_campaign
        self.campaign_service.buy_get_gift_repo = mock_buy_repo

        # Call the get_one_campaign method and assert the result
        result = self.campaign_service.get_one_campaign(campaign_id="c4")
        self.assertEqual(result.id, "c4")

    def test_delete_discount_campaign(self) -> None:
        # Mock the get_one_campaign method first to find the campaign
        discount_campaign = DiscountCampaign(
            id="c1",
            campaign_type=CampaignType.DISCOUNT,
            discount=10,
            products=["p1"]
        )

        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = discount_campaign
        mock_product_repo.delete_campaign = MagicMock()
        self.campaign_service.product_discount_repo = mock_product_repo

        # Call the delete_campaign method
        self.campaign_service.delete_campaign(campaign_id="c1")

        # Assert the delete_campaign method was called
        mock_product_repo.delete_campaign.assert_called_once_with(campaign_id="c1")

    def test_delete_combo_campaign(self) -> None:
        # Create proper ProductForReceipt objects
        product1 = ProductForReceipt(id="p1", quantity=1, price=100)
        product2 = ProductForReceipt(id="p2", quantity=1, price=100)

        # Mock the get_one_campaign method first to find the campaign
        combo_campaign = ComboCampaign(
            id="c2",
            campaign_type=CampaignType.COMBO,
            discount=15,
            products=[product1, product2]
        )

        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = None
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_one_campaign.return_value = combo_campaign
        mock_combo_repo.delete_campaign = MagicMock()
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        # Call the delete_campaign method
        self.campaign_service.delete_campaign(campaign_id="c2")

        # Assert the delete_campaign method was called
        mock_combo_repo.delete_campaign.assert_called_once_with(campaign_id="c2")

    def test_delete_receipt_campaign(self) -> None:
        # Mock the get_one_campaign method first to find the campaign
        receipt_campaign = ReceiptCampaign(
            id="c3",
            campaign_type=CampaignType.DISCOUNT,
            total=200,
            discount=20
        )

        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = None
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_one_campaign.return_value = None
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        mock_receipt_repo = MagicMock()
        mock_receipt_repo.get_one_campaign.return_value = receipt_campaign
        mock_receipt_repo.delete_campaign = MagicMock()
        self.campaign_service.receipt_discount_repo = mock_receipt_repo

        # Call the delete_campaign method
        self.campaign_service.delete_campaign(campaign_id="c3")

        # Assert the delete_campaign method was called
        mock_receipt_repo.delete_campaign.assert_called_once_with(campaign_id="c3")

    def test_delete_buy_n_get_n_campaign(self) -> None:
        # Create ProductForReceipt objects for buy/gift products
        buy_product = ProductForReceipt(id="p2", quantity=3, price=100)
        gift_product = ProductForReceipt(id="p3", quantity=1, price=50)

        # Mock the get_one_campaign method first to find the campaign
        buy_n_get_n_campaign = BuyNGetNCampaign(
            id="c4",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=buy_product,
            gift_product=gift_product
        )

        mock_product_repo = MagicMock()
        mock_product_repo.get_one_campaign.return_value = None
        self.campaign_service.product_discount_repo = mock_product_repo

        mock_combo_repo = MagicMock()
        mock_combo_repo.get_one_campaign.return_value = None
        self.campaign_service.combo_campaign_repo = mock_combo_repo

        mock_receipt_repo = MagicMock()
        mock_receipt_repo.get_one_campaign.return_value = None
        self.campaign_service.receipt_discount_repo = mock_receipt_repo

        mock_buy_repo = MagicMock()
        mock_buy_repo.get_one_campaign.return_value = buy_n_get_n_campaign
        mock_buy_repo.delete_campaign = MagicMock()
        self.campaign_service.buy_get_gift_repo = mock_buy_repo

        # Call the delete_campaign method
        self.campaign_service.delete_campaign(campaign_id="c4")

        # Assert the delete_campaign method was called
        mock_buy_repo.delete_campaign.assert_called_once_with(campaign_id="c4")


if __name__ == "__main__":
    unittest.main()