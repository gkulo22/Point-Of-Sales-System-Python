import unittest
from unittest.mock import MagicMock

import pytest

from app.core.interactors.campaign_interactor import CampaignInteractor
from app.core.models import NO_ID
from app.core.models.campaign import (
    BuyNGetNCampaign,
    Campaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.product import NumProduct, Product
from app.core.models.receipt import ProductForReceipt
from app.core.services.campaign_service import CampaignService
from app.core.services.product_service import ProductService


# Fixtures to mock the services
@pytest.fixture
def mock_campaign_service() -> MagicMock:
    return MagicMock(CampaignService)


@pytest.fixture
def mock_product_service() -> MagicMock:
    return MagicMock(ProductService)


@pytest.fixture
def campaign_interactor(mock_campaign_service: MagicMock,
                        mock_product_service: MagicMock) -> CampaignInteractor:
    return CampaignInteractor(campaign_service=mock_campaign_service,
                              product_service=mock_product_service)


# Test cases for CampaignInteractor methods
class TestCampaignInteractor:
    def test_execute_get_one(self, campaign_interactor: CampaignInteractor,
                             mock_campaign_service: MagicMock) -> None:
        campaign_id = "test_campaign_id"
        campaign = Campaign(id=campaign_id, campaign_type=CampaignType.DISCOUNT)
        mock_campaign_service.get_one_campaign.return_value = campaign

        result = campaign_interactor.execute_get_one(campaign_id)

        mock_campaign_service.get_one_campaign.assert_called_once_with(campaign_id=campaign_id)
        assert result == campaign

    def test_execute_get_all(self, campaign_interactor: CampaignInteractor, mock_campaign_service: MagicMock) -> None:
        campaign1 = Campaign(id="1", campaign_type=CampaignType.DISCOUNT)
        campaign2 = Campaign(id="2", campaign_type=CampaignType.COMBO)
        mock_campaign_service.get_all_campaigns.return_value = [campaign1, campaign2]

        result = campaign_interactor.execute_get_all()

        mock_campaign_service.get_all_campaigns.assert_called_once()
        assert result == [campaign1, campaign2]

    def test_execute_create_discount(self, campaign_interactor: CampaignInteractor, mock_campaign_service: MagicMock) -> None:
        discount = 20
        discount_campaign = DiscountCampaign(id=NO_ID, campaign_type=CampaignType.DISCOUNT, discount=discount,
                                             products=[])
        mock_campaign_service.create_discount.return_value = discount_campaign

        result = campaign_interactor.execute_create_discount(discount)

        mock_campaign_service.create_discount.assert_called_once_with(discount_campaign=discount_campaign)
        assert result == discount_campaign

    def test_execute_create_combo(self, campaign_interactor: CampaignInteractor, mock_campaign_service: MagicMock) -> None:
        discount = 15.0
        combo_campaign = ComboCampaign(id=NO_ID, campaign_type=CampaignType.COMBO, discount=discount, products=[])
        mock_campaign_service.create_combo.return_value = combo_campaign

        result = campaign_interactor.execute_create_combo(discount)

        mock_campaign_service.create_combo.assert_called_once_with(combo_campaign=combo_campaign)
        assert result == combo_campaign

    def test_execute_create_receipt_discount(self,
                                             campaign_interactor: CampaignInteractor,
                                             mock_campaign_service: MagicMock) -> None:
        discount = 30
        amount = 100
        receipt_campaign = ReceiptCampaign(id=NO_ID, campaign_type=CampaignType.RECEIPT_DISCOUNT, total=amount,
                                           discount=discount)
        mock_campaign_service.create_receipt_discount.return_value = receipt_campaign

        result = campaign_interactor.execute_create_receipt_discount(discount, amount)

        mock_campaign_service.create_receipt_discount.assert_called_once_with(receipt_campaign=receipt_campaign)
        assert result == receipt_campaign

    def test_execute_create_buy_n_get_n(
        self,
        campaign_interactor: CampaignInteractor,
        mock_campaign_service: MagicMock,
        mock_product_service: MagicMock
    ) -> None:
        buy_product = NumProduct(product_id="buy_product_id", num=2)
        gift_product = NumProduct(product_id="gift_product_id", num=1)
        product_mock = MagicMock()
        product_mock.get_price.return_value = 10.0
        mock_product_service.get_one_product.return_value = product_mock

        buy_n_get_n_campaign = BuyNGetNCampaign(
            id=NO_ID, campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=ProductForReceipt(id=buy_product.product_id,
                                          quantity=buy_product.num,
                                          price=10.0, total=20.0),
            gift_product=ProductForReceipt(id=gift_product.product_id,
                                           quantity=gift_product.num, price=10.0,
                                           total=10.0,
                                           discount_total=0)
        )
        mock_campaign_service.create_buy_n_get_n.return_value = buy_n_get_n_campaign

        result = campaign_interactor.execute_create_buy_n_get_n(buy_product, gift_product)

        mock_product_service.get_one_product.assert_any_call(product_id=buy_product.product_id)
        mock_product_service.get_one_product.assert_any_call(product_id=gift_product.product_id)
        mock_campaign_service.create_buy_n_get_n.assert_called_once_with(buy_n_get_n_campaign=buy_n_get_n_campaign)
        assert result == buy_n_get_n_campaign

    def test_execute_delete(self, campaign_interactor: CampaignInteractor,
                            mock_campaign_service: MagicMock) -> None:
        campaign_id = "test_campaign_id"
        campaign_interactor.execute_delete(campaign_id)
        mock_campaign_service.delete_campaign.assert_called_once_with(campaign_id=campaign_id)

    def test_execute_adding_in_combo(
        self,
        campaign_interactor: CampaignInteractor,
        mock_campaign_service: MagicMock,
        mock_product_service: MagicMock
    ) -> None:
        campaign_id = "test_combo_campaign"
        product_id = "test_product"
        quantity = 2
        campaign = ComboCampaign(id=campaign_id, campaign_type=CampaignType.COMBO, discount=10.0, products=[])
        product = MagicMock(spec=Product)
        mock_campaign_service.get_one_campaign.return_value = campaign
        mock_product_service.get_one_product.return_value = product
        mock_campaign_service.add_product_in_combo.return_value = campaign

        result = campaign_interactor.execute_adding_in_combo(campaign_id,
                                                             product_id, quantity)

        mock_campaign_service.get_one_campaign.assert_called_once_with(campaign_id=campaign_id)
        mock_product_service.get_one_product.assert_called_once_with(product_id=product_id)
        mock_campaign_service.add_product_in_combo.assert_called_once_with(product=product, quantity=quantity,
                                                                           campaign_id=campaign_id)
        assert result == campaign

    def test_execute_adding_in_discount(
        self,
        campaign_interactor: CampaignInteractor,
        mock_campaign_service: MagicMock
    ) -> None:
        campaign_id = "test_discount_campaign"
        product_id = "test_product"
        campaign = DiscountCampaign(id=campaign_id, campaign_type=CampaignType.DISCOUNT, discount=15, products=[])
        mock_campaign_service.get_one_campaign.return_value = campaign
        mock_campaign_service.add_product_in_discount.return_value = campaign

        result = campaign_interactor.execute_adding_in_discount(campaign_id, product_id)

        mock_campaign_service.get_one_campaign.assert_called_once_with(campaign_id=campaign_id)
        mock_campaign_service.add_product_in_discount.assert_called_once_with(product_id=product_id,
                                                                              campaign_id=campaign_id)
        assert result == campaign

    def test_execute_delete_from_discount(
        self,
        campaign_interactor: CampaignInteractor,
        mock_campaign_service: MagicMock
    ) -> None:
        campaign_id = "test_discount_campaign"
        product_id = "test_product"
        campaign = DiscountCampaign(id=campaign_id, campaign_type=CampaignType.DISCOUNT,
                                    discount=10, products=[])
        mock_campaign_service.get_one_campaign.return_value = campaign
        campaign_interactor.execute_delete_from_discount(campaign_id, product_id)
        mock_campaign_service.get_one_campaign.assert_called_once_with(campaign_id=campaign_id)
        mock_campaign_service.execute_delete_from_discount.assert_called_once_with(campaign_id=campaign_id,
                                                                                   product_id=product_id)


if __name__ == "__main__":
    unittest.main()