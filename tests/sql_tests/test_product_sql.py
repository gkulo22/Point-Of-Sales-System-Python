import sqlite3
import unittest
from typing import ClassVar
from uuid import uuid4

from app.core.models.product import Product
from app.infra.data.sqlite import ProductSqliteRepository


class TestProductSqliteRepository(unittest.TestCase):
    # Define connection as class variable with type annotation
    connection: ClassVar[sqlite3.Connection]

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the database connection and tables once for all tests."""
        cls.connection = sqlite3.connect(':memory:')
        cursor = cls.connection.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            barcode TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            discount REAL
        )''')
        cls.connection.commit()

    def setUp(self) -> None:
        """Set up the product repository before each test."""
        self.product_repo = ProductSqliteRepository(self.connection)

    def tearDown(self) -> None:
        """Clean up the database after each test."""
        self.connection.execute("DELETE FROM products")
        self.connection.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up the database after all tests."""
        cls.connection.close()

    def test_create_product_with_generated_id(self) -> None:
        original_id = str(uuid4())  # Store original ID before creation

        temp_product = Product(
            id=original_id,
            name="Test Product",
            barcode="123456789",
            price=10.99,
            discount=0.0
        )

        created_product = self.product_repo.create(temp_product)

        # Assert the ID has been generated and is different from the original
        self.assertNotEqual(created_product.id, original_id)
        self.assertEqual(len(created_product.id), 36)

    def test_get_product_by_id(self) -> None:
        original = Product(
            id=str(uuid4()),
            name="Test Product",
            barcode="TEST123",
            price=15.0,
            discount=5.0
        )
        self.product_repo.connection.execute(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
            (original.id,
             original.name,
             original.barcode,
             original.price,
             original.discount)
        )
        self.product_repo.connection.commit()

        retrieved = self.product_repo.get_one(original.id)

        # Ensure retrieved is not None before accessing attributes
        self.assertIsNotNone(retrieved)
        if retrieved is not None:  # This check helps the type checker
            # Assert the retrieved product matches the original
            self.assertEqual(retrieved.id, original.id)
            self.assertEqual(retrieved.name, original.name)
            self.assertEqual(retrieved.barcode, original.barcode)
            self.assertEqual(retrieved.price, original.price)
            self.assertEqual(retrieved.discount, original.discount)

    def test_update_product_price(self) -> None:
        original = Product(
            id=str(uuid4()),
            name="Test Product",
            barcode="UPD123",
            price=100.0,
            discount=10.0
        )
        self.product_repo.connection.execute(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
            (original.id,
             original.name,
             original.barcode,
             original.price,
             original.discount)
        )
        self.product_repo.connection.commit()

        # Update price
        self.product_repo.update(original.id, 90.0)

        # Verify update
        cursor = self.product_repo.connection.cursor()
        cursor.execute("SELECT price FROM products WHERE id = ?", (original.id,))
        self.assertEqual(cursor.fetchone()[0], 90.0)

    def test_barcode_uniqueness_constraint(self) -> None:
        barcode = "DUPLICATE123"

        # Create first product
        product1 = Product(
            id=str(uuid4()),
            name="Product 1",
            barcode=barcode,
            price=10.0,
            discount=0.0
        )
        self.product_repo.create(product1)

        # Attempt duplicate
        product2 = Product(
            id=str(uuid4()),
            name="Product 2",
            barcode=barcode,
            price=20.0,
            discount=5.0
        )

        with self.assertRaises(sqlite3.IntegrityError):
            self.product_repo.create(product2)

    def test_has_barcode_check(self) -> None:
        barcode = "EXISTS123"

        # Verify non-existent barcode
        self.assertFalse(self.product_repo.has_barcode(barcode))

        # Create product
        product = Product(
            id=str(uuid4()),
            name="Barcode Test",
            barcode=barcode,
            price=50.0,
            discount=0.0
        )
        self.product_repo.create(product)

        # Verify exists
        self.assertTrue(self.product_repo.has_barcode(barcode))


if __name__ == '__main__':
    unittest.main()