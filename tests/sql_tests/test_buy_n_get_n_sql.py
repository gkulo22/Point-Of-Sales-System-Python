import sqlite3
import unittest
import uuid
from typing import ClassVar

from app.core.models.campaign import BuyNGetNCampaign, CampaignType
from app.core.models.receipt import ProductForReceipt  # Fixed import path
from app.infra.data.sqlite import BuyNGetNCampaignSqliteRepository


class TestBuyNGetNCampaignSqliteRepository(unittest.TestCase):
    connection: ClassVar[sqlite3.Connection]

    def setUp(self) -> None:
        self.connection = sqlite3.connect(':memory:')
        self.connection.execute('''CREATE TABLE buy_n_get_n_campaigns (
                                    id TEXT PRIMARY KEY,
                                    campaign_type TEXT,
                                    buy_product TEXT,
                                    gift_product TEXT)''')
        self.repository = BuyNGetNCampaignSqliteRepository(self.connection)

        self.buy_product = ProductForReceipt(
            id="1", quantity=2, price=10.0,
            total=20.0, discount_price=8.0,
            discount_total=16.0)
        self.gift_product = ProductForReceipt(
            id="2", quantity=1, price=5.0,
            total=5.0, discount_price=4.0,
            discount_total=4.0)
        self.campaign = BuyNGetNCampaign(
            id=str(uuid.uuid4()),
            campaign_type=CampaignType.BUY_N_GET_N,
            buy_product=self.buy_product,
            gift_product=self.gift_product
        )

    def tearDown(self) -> None:
        self.connection.close()

    def test_create_campaign(self) -> None:
        created_campaign = self.repository.create(self.campaign)
        self.assertEqual(created_campaign.id, self.campaign.id)
        self.assertEqual(created_campaign.buy_product.quantity,
                         self.buy_product.quantity)
        self.assertEqual(created_campaign.gift_product.quantity,
                         self.gift_product.quantity)

    def test_get_all_campaigns(self) -> None:
        self.repository.create(self.campaign)
        campaigns = self.repository.get_all()
        self.assertEqual(len(campaigns), 1)
        self.assertEqual(campaigns[0].id, self.campaign.id)

    def test_get_one_campaign(self) -> None:
        self.repository.create(self.campaign)
        fetched_campaign = self.repository.get_one_campaign(self.campaign.id)
        self.assertIsNotNone(fetched_campaign)
        if fetched_campaign is not None:  # Type guard for the type checker
            self.assertEqual(fetched_campaign.id, self.campaign.id)
            self.assertEqual(fetched_campaign.buy_product.id, self.buy_product.id)
            self.assertEqual(fetched_campaign.gift_product.id, self.gift_product.id)

    def test_get_one_campaign_not_found(self) -> None:
        fetched_campaign = self.repository.get_one_campaign(str(uuid.uuid4()))
        self.assertIsNone(fetched_campaign)

    def test_delete_campaign(self) -> None:
        self.repository.create(self.campaign)
        self.repository.delete_campaign(self.campaign.id)
        fetched_campaign = self.repository.get_one_campaign(self.campaign.id)
        self.assertIsNone(fetched_campaign)


if __name__ == '__main__':
    unittest.main()