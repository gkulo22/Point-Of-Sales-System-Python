import sqlite3
import unittest
import uuid
from typing import ClassVar

from app.core.models.campaign import CampaignType, DiscountCampaign
from app.infra.data.sqlite import (
    ProductDiscountCampaignSqliteRepository,
    SqliteRepoFactory,
)


class TestDiscountCampaignSqliteRepository(unittest.TestCase):
    # Define connection as class variable with type annotation
    connection: ClassVar[sqlite3.Connection]

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the database connection and tables once for all tests."""
        cls.connection = sqlite3.connect(":memory:")
        cls.connection.execute('''CREATE TABLE discount_campaigns (
                                    id TEXT PRIMARY KEY,
                                    campaign_type TEXT,
                                    discount REAL
                                  )''')
        cls.connection.execute('''CREATE TABLE discount_campaign_products (
                                    campaign_id TEXT,
                                    product_id TEXT,
                                    PRIMARY KEY (campaign_id, product_id)
                                  )''')

    def setUp(self) -> None:
        """Set up a sample discount campaign before each test."""
        campaign = DiscountCampaign(
            id=str(uuid.uuid4()),
            campaign_type=CampaignType.DISCOUNT,
            discount=10,
            products=["product1", "product2"]
        )

        self.repo = ProductDiscountCampaignSqliteRepository(self.connection)
        self.discount_campaign = self.repo.create(campaign)

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.connection.execute("DELETE FROM discount_campaigns")
        self.connection.execute("DELETE FROM discount_campaign_products")

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the database after all tests."""
        cls.connection.close()

    def test_create_discount_campaign(self) -> None:
        repo = SqliteRepoFactory(self.connection)
        retrieved_campaign = repo.discount_campaign().create(self.discount_campaign)

        self.assertIsNotNone(retrieved_campaign)
        self.assertEqual(retrieved_campaign.id, self.discount_campaign.id)
        self.assertEqual(retrieved_campaign.campaign_type,
                         self.discount_campaign.campaign_type)
        self.assertEqual(retrieved_campaign.discount, self.discount_campaign.discount)
        self.assertEqual(len(retrieved_campaign.products),
                         len(self.discount_campaign.products))

    def test_add_product_to_campaign(self) -> None:
        repo = SqliteRepoFactory(self.connection)

        campaign = repo.discount_campaign().add_product(
            "product3", self.discount_campaign.id)

        self.assertIn("product3", campaign.products)

    def test_delete_product_from_campaign(self) -> None:
        repo = SqliteRepoFactory(self.connection)
        # Add a new product first
        repo.discount_campaign().add_product("product3", self.discount_campaign.id)

        # Remove the added product
        repo.discount_campaign().delete_product("product3", self.discount_campaign.id)
        updated_campaign = repo.discount_campaign().get_one_campaign(
            self.discount_campaign.id)

        # Ensure the campaign exists and the product is deleted
        self.assertIsNotNone(updated_campaign)
        if updated_campaign is not None:  # Type guard for the type checker
            self.assertNotIn("product3", updated_campaign.products)
            self.assertEqual(len(updated_campaign.products), 2)
        else:
            self.fail("Updated campaign should not be None")

    def test_get_all_campaigns(self) -> None:
        repo = SqliteRepoFactory(self.connection)
        # Retrieve all campaigns
        campaigns = repo.discount_campaign().get_all()

        # Ensure the campaign exists in the list
        self.assertGreaterEqual(len(campaigns), 0)
        self.assertTrue(any(campaign.id == self.discount_campaign.id
                            for campaign in campaigns))

    def test_delete_campaign(self) -> None:
        repo = ProductDiscountCampaignSqliteRepository(self.connection)
        # Delete the campaign
        repo.delete_campaign(self.discount_campaign.id)

        # Ensure the campaign is deleted
        deleted_campaign = repo.get_one_campaign(self.discount_campaign.id)
        self.assertIsNone(deleted_campaign)

    def test_get_campaign_with_non_existent_product(self) -> None:
        repo = ProductDiscountCampaignSqliteRepository(self.connection)
        campaign = repo.get_campaign_with_product("non_existent_product")
        self.assertIsNone(campaign)


if __name__ == '__main__':
    unittest.main()