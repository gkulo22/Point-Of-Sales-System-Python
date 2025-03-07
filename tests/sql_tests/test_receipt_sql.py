import sqlite3
import unittest
import uuid

from app.core.models.receipt import (
    ProductForReceipt,
    Receipt,
)
from app.infra.data.sqlite import ReceiptSqliteRepository


class TestReceiptSqliteRepository(unittest.TestCase):
    def setUp(self) -> None:
        # Set up an in-memory SQLite database for testing
        self.connection = sqlite3.connect(':memory:')
        self.repository = ReceiptSqliteRepository(connection=self.connection)

        # Create the receipts and receipt_items tables for testing
        self._create_tables()

    def tearDown(self) -> None:
        self.connection.close()

    def _create_tables(self) -> None:
        # Create the necessary tables for the tests
        cursor = self.connection.cursor()
        cursor.execute("""
        CREATE TABLE receipts (
            id TEXT PRIMARY KEY,
            shift_id TEXT,
            total REAL,
            discount_total REAL,
            status BOOLEAN
        )
        """)
        cursor.execute("""
        CREATE TABLE receipt_items (
            item_id TEXT,
            receipt_id TEXT,
            item_type TEXT,
            quantity INTEGER,
            price REAL,
            total REAL,
            discount_price REAL,
            discount_total REAL,
            item_data TEXT,
            PRIMARY KEY (item_id, receipt_id)
        )
        """)
        self.connection.commit()

    def test_create_receipt(self) -> None:
        # Create a receipt
        receipt = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_1",
            total=100.0,
            discount_total=10.0,
            status=True,
            items=[]  # No items for this test case
        )

        created_receipt = self.repository.create(receipt)

        self.assertEqual(created_receipt.id, receipt.id)
        self.assertEqual(created_receipt.total, receipt.total)
        self.assertEqual(created_receipt.discount_total, receipt.discount_total)
        self.assertTrue(created_receipt.status)

    def test_add_product_to_receipt(self) -> None:
        # Create a receipt with an item
        product = ProductForReceipt(
            id=str(uuid.uuid4()),
            quantity=1,
            price=50.0,
            total=50.0,
            discount_price=5.0,
            discount_total=5.0
        )
        receipt = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_1",
            total=50.0,
            discount_total=5.0,
            status=True,
            items=[product]
        )
        created_receipt = self.repository.create(receipt)

        # Add another product to the existing receipt
        new_product = ProductForReceipt(
            id=str(uuid.uuid4()),
            quantity=2,
            price=25.0,
            total=50.0,
            discount_price=2.5,
            discount_total=5.0
        )
        created_receipt.items.append(new_product)
        created_receipt.total = (created_receipt.total or 0) + new_product.total

        created_receipt.discount_total = ((created_receipt.discount_total or 0) +
                                          (new_product.discount_total or 0))

        updated_receipt = self.repository.add_product(created_receipt)

        self.assertEqual(len(updated_receipt.items), 2)  # Two items now in the receipt
        self.assertEqual(updated_receipt.total, 100.0)
        self.assertEqual(updated_receipt.discount_total, 10.0)

    def test_update_receipt_status(self) -> None:
        # Create a receipt
        receipt = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_1",
            total=100.0,
            discount_total=10.0,
            status=True,
            items=[]
        )
        created_receipt = self.repository.create(receipt)

        # Update the status of the receipt
        self.repository.update(created_receipt.id, False)

        updated_receipt = self.repository.get_one(created_receipt.id)

        if updated_receipt:
            self.assertFalse(updated_receipt.status)  # The status should now be False
        else:
            self.fail("Receipt should not be None")

    def test_delete_receipt(self) -> None:
        # Create a receipt
        receipt = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_1",
            total=100.0,
            discount_total=10.0,
            status=True,
            items=[]
        )
        created_receipt = self.repository.create(receipt)

        # Ensure the receipt exists before deletion
        receipt_exists_before = self.repository.get_one(created_receipt.id)
        self.assertIsNotNone(receipt_exists_before)

        # Delete the receipt
        self.repository.delete(created_receipt.id)

        # Ensure the receipt no longer exists after deletion
        receipt_exists_after = self.repository.get_one(created_receipt.id)
        self.assertIsNone(receipt_exists_after)

    def test_get_all_receipts(self) -> None:
        # Create a few receipts
        receipt_1 = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_1",
            total=50.0,
            discount_total=5.0,
            status=True,
            items=[]
        )
        receipt_2 = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_2",
            total=100.0,
            discount_total=10.0,
            status=False,
            items=[]
        )
        self.repository.create(receipt_1)
        self.repository.create(receipt_2)

        receipts = self.repository.get_all()

        self.assertEqual(len(receipts), 2)  # Two receipts should be in the database
        self.assertEqual(receipts[0].shift_id, "shift_1")
        self.assertEqual(receipts[1].shift_id, "shift_2")

    def test_delete_item_from_receipt(self) -> None:
        # Create a receipt with an item
        product = ProductForReceipt(
            id=str(uuid.uuid4()),
            quantity=1,
            price=50.0,
            total=50.0,
            discount_price=5.0,
            discount_total=5.0
        )
        receipt = Receipt(
            id=str(uuid.uuid4()),
            shift_id="shift_1",
            total=50.0,
            discount_total=5.0,
            status=True,
            items=[product]
        )
        created_receipt = self.repository.create(receipt)

        # Remove the item by calling delete_item (this updates the receipt)
        created_receipt.items = []  # Empty the items list
        created_receipt.total = 0
        created_receipt.discount_total = 0
        self.repository.delete_item(created_receipt)

        updated_receipt = self.repository.get_one(created_receipt.id)

        if updated_receipt:
            self.assertEqual(len(updated_receipt.items), 0)
            self.assertEqual(updated_receipt.total, 0)
            self.assertEqual(updated_receipt.discount_total, 0)
        else:
            self.fail("Receipt should not be None")


if __name__ == "__main__":
    unittest.main()
