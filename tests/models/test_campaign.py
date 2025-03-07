import unittest

from app.core.models.campaign import (
    BuyNGetNCampaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.receipt import ProductForReceipt


class TestCampaigns(unittest.TestCase):

    def setUp(self) -> None:
        self.product_1 = ProductForReceipt(id="1", quantity=1, price=100)
        self.product_2 = ProductForReceipt(id="2", quantity=1, price=50)
        self.product_3 = ProductForReceipt(id="3", quantity=1, price=30)

    def test_combo_campaign_get_price(self) -> None:
        combo_campaign = ComboCampaign(
            id="combo1",
            campaign_type=CampaignType.COMBO,
            discount=20,
            products=[self.product_1, self.product_2]
        )
        self.assertEqual(combo_campaign.get_price(), 150)

    def test_combo_campaign_real_price(self) -> None:
        combo_campaign = ComboCampaign(
            id="combo1",
            campaign_type=CampaignType.COMBO,
            discount=20,
            products=[self.product_1, self.product_2]
        )
        self.assertEqual(combo_campaign.real_price(), 130)

    def test_discount_campaign(self) -> None:
        discount_campaign = DiscountCampaign(
            id="discount1",
            campaign_type=CampaignType.DISCOUNT,
            discount=10,
            products=["prod1", "prod2"]
        )
        self.assertEqual(discount_campaign.discount, 10)
        self.assertEqual(discount_campaign.products, ["prod1", "prod2"])

    def test_buy_n_get_n_campaign_get_price(self) -> None:
        buy_n_get_n_campaign = BuyNGetNCampaign(
            id="buyget1",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=self.product_1,
            gift_product=self.product_2
        )
        self.assertEqual(buy_n_get_n_campaign.get_price(), 150)

    def test_buy_n_get_n_campaign_real_price(self) -> None:
        buy_n_get_n_campaign = BuyNGetNCampaign(
            id="buyget1",
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=self.product_1,
            gift_product=self.product_2
        )
        self.assertEqual(buy_n_get_n_campaign.real_price(), 100)

    def test_receipt_campaign(self) -> None:
        receipt_campaign = ReceiptCampaign(
            id="receipt1",
            campaign_type=CampaignType.RECEIPT_DISCOUNT,
            total=200,
            discount=50
        )
        self.assertEqual(receipt_campaign.total, 200)
        self.assertEqual(receipt_campaign.discount, 50)


if __name__ == "__main__":
    unittest.main()