import sqlite3
import unittest
from typing import ClassVar

from app.core.models import ProductForReceipt
from app.core.models.campaign import CampaignType, ComboCampaign
from app.infra.data.sqlite import ComboCampaignSqliteRepository


class TestComboCampaignSqliteRepository(unittest.TestCase):
    conn: ClassVar[sqlite3.Connection]

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the database connection and table once for all tests."""
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.execute("""
            CREATE TABLE combo_campaigns (
                id TEXT PRIMARY KEY,
                campaign_type TEXT,
                discount INTEGER,
                products TEXT
            )
        """)

    def setUp(self) -> None:
        """Set up the individual test fixtures."""
        self.combo_campaign = ComboCampaign(
            id="test-campaign",
            campaign_type=CampaignType.COMBO,
            discount=20,
            products=[
                ProductForReceipt(
                    id="product1",
                    quantity=2,
                    price=100,
                    total=200,
                    discount_price=90,
                    discount_total=180)
            ]
        )
        self.repo = ComboCampaignSqliteRepository(self.conn)

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.conn.execute("DELETE FROM combo_campaigns")

    def test_create_combo_campaign(self) -> None:
        result = self.repo.create(self.combo_campaign)

        # Check that the result has the correct properties
        self.assertIsNotNone(result.id)
        self.assertEqual(result.discount, 20)
        self.assertEqual(len(result.products), 1)

        # Verify that the data was inserted into the database
        cursor = self.conn.execute(
            "SELECT * FROM combo_campaigns WHERE id = ?",
            (result.id,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)

    def test_get_all_combo_campaigns(self) -> None:
        self.repo.create(self.combo_campaign)
        result = self.repo.get_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.combo_campaign.id)
        self.assertEqual(result[0].discount, 20)

    def test_get_one_combo_campaign(self) -> None:
        self.repo.create(self.combo_campaign)
        result = self.repo.get_one_campaign(self.combo_campaign.id)

        self.assertIsNotNone(result)
        if result:  # Add None check
            self.assertEqual(result.id, self.combo_campaign.id)
            self.assertEqual(result.discount, 20)

    def test_add_product_to_combo_campaign(self) -> None:
        self.repo.create(self.combo_campaign)

        new_product = ProductForReceipt(
            id="product2", quantity=1, price=50, total=50,
            discount_price=None, discount_total=None)
        updated_campaign = self.repo.add_product(new_product, self.combo_campaign.id)

        if updated_campaign:  # Add None check
            self.assertEqual(len(updated_campaign.products), 2)
            self.assertEqual(updated_campaign.products[1].id, "product2")

    def test_delete_combo_campaign(self) -> None:
        self.repo.create(self.combo_campaign)

        self.repo.delete_campaign(self.combo_campaign.id)

        result = self.repo.get_one_campaign(self.combo_campaign.id)
        self.assertIsNone(result)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the database after all tests."""
        cls.conn.close()


if __name__ == '__main__':
    unittest.main()