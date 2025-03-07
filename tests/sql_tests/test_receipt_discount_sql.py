import sqlite3
import unittest

from app.core.models.campaign import CampaignType, ReceiptCampaign
from app.infra.data.sqlite import ReceiptDiscountCampaignSqliteRepository


class TestReceiptDiscountCampaignSqliteRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(':memory:')
        self.connection.execute(''' 
            CREATE TABLE receipt_discount_campaigns (
                id TEXT PRIMARY KEY,
                campaign_type TEXT,
                total REAL,
                discount REAL
            )
        ''')
        self.repository = ReceiptDiscountCampaignSqliteRepository(self.connection)

    def tearDown(self) -> None:
        self.connection.close()

    def test_create_campaign(self) -> None:
        campaign = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT, total=100, discount=10, id="1")
        created_campaign = self.repository.create(campaign)
        self.assertIsNotNone(created_campaign.id)
        self.assertEqual(created_campaign.total, 100)
        self.assertEqual(created_campaign.discount, 10)

    def test_get_one_campaign(self) -> None:
        campaign = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT, total=200, discount=20, id="1")
        created_campaign = self.repository.create(campaign)
        fetched_campaign = self.repository.get_one_campaign(created_campaign.id)
        self.assertIsNotNone(fetched_campaign)
        # Add null check before accessing attributes
        if fetched_campaign is not None:
            self.assertEqual(fetched_campaign.total, 200)
            self.assertEqual(fetched_campaign.discount, 20)

    def test_get_one_campaign_not_found(self) -> None:
        fetched_campaign = self.repository.get_one_campaign('non-existing-id')
        self.assertIsNone(fetched_campaign)

    def test_get_all_campaigns(self) -> None:
        campaign1 = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT, total=300, discount=30, id="1")
        campaign2 = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT, total=400, discount=40, id="2")
        self.repository.create(campaign1)
        self.repository.create(campaign2)
        campaigns = self.repository.get_all()
        self.assertEqual(len(campaigns), 2)

    def test_delete_campaign(self) -> None:
        campaign = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT,
            total=500, discount=50, id="1")
        created_campaign = self.repository.create(campaign)
        self.repository.delete_campaign(created_campaign.id)
        fetched_campaign = self.repository.get_one_campaign(created_campaign.id)
        self.assertIsNone(fetched_campaign)

    def test_get_discount_on_amount(self) -> None:
        campaign1 = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT,
            total=600, discount=60, id="1")
        campaign2 = ReceiptCampaign(
            campaign_type=CampaignType.RECEIPT_DISCOUNT,
            total=700, discount=70, id="2")
        self.repository.create(campaign1)
        self.repository.create(campaign2)
        best_discount = self.repository.get_discount_on_amount(650)
        self.assertIsNotNone(best_discount)
        if best_discount is not None:
            self.assertEqual(best_discount.discount, 60)