import sqlite3
import unittest
from uuid import uuid4

from app.core.models.receipt import Receipt
from app.core.models.shift import Shift
from app.core.state.shift_state import ClosedShiftState, OpenShiftState
from app.infra.data.sqlite import ShiftSqliteRepository


class TestShiftSqliteRepository(unittest.TestCase):
    connection: sqlite3.Connection  # Indicate that 'connection' is a class attribute

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the database connection and tables once for all tests."""
        cls.connection = sqlite3.connect(':memory:')
        cursor = cls.connection.cursor()

        cursor.execute('''CREATE TABLE shifts (
            id TEXT PRIMARY KEY,
            state TEXT
        )''')
        cursor.execute('''CREATE TABLE receipts (
            id TEXT PRIMARY KEY,
            shift_id TEXT
        )''')
        cursor.execute('''CREATE TABLE receipt_items (
            id TEXT PRIMARY KEY,
            receipt_id TEXT
        )''')
        cls.connection.commit()

    def setUp(self) -> None:
        """Set up the shift repository and sample objects before each test."""
        self.shift_sqlite_repository = ShiftSqliteRepository(connection=self.connection)

        self.sample_shift = Shift(
            id=str(uuid4()),
            receipts=[],
            state=OpenShiftState()
        )

        self.sample_receipt = Receipt(
            id=str(uuid4()),
            shift_id=str(uuid4()),
            total=100,
            discount_total=10,
            status=True,
            items=[]
        )

    def tearDown(self) -> None:
        """Clean up the database after each test."""
        self.connection.execute("DELETE FROM shifts")
        self.connection.execute("DELETE FROM receipts")
        self.connection.execute("DELETE FROM receipt_items")
        self.connection.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Close the connection after all tests."""
        cls.connection.close()

    def test_create_shift(self) -> None:
        created_shift = self.shift_sqlite_repository.create(self.sample_shift)
        self.assertIsNotNone(created_shift.id)
        self.assertIsInstance(created_shift.state, OpenShiftState)

    def test_get_one_shift(self) -> None:
        self.shift_sqlite_repository.create(self.sample_shift)
        retrieved_shift = self.shift_sqlite_repository.get_one(self.sample_shift.id)
        self.assertIsNotNone(retrieved_shift)
        if retrieved_shift:
            self.assertEqual(retrieved_shift.id, self.sample_shift.id)
            self.assertIsInstance(retrieved_shift.state, OpenShiftState)

    def test_get_all_shifts(self) -> None:
        self.shift_sqlite_repository.create(self.sample_shift)
        shifts = self.shift_sqlite_repository.get_all()
        self.assertEqual(len(shifts), 1)
        self.assertEqual(shifts[0].id, self.sample_shift.id)

    def test_update_shift_state(self) -> None:
        self.shift_sqlite_repository.create(self.sample_shift)
        self.shift_sqlite_repository.update(self.sample_shift.id, status=False)
        updated_shift = self.shift_sqlite_repository.get_one(self.sample_shift.id)
        if updated_shift:
            self.assertIsInstance(updated_shift.state, ClosedShiftState)

    def test_delete_shift(self) -> None:
        self.shift_sqlite_repository.create(self.sample_shift)
        self.shift_sqlite_repository.delete(self.sample_shift.id)
        deleted_shift = self.shift_sqlite_repository.get_one(self.sample_shift.id)
        self.assertIsNone(deleted_shift)

    def test_delete_shift_with_receipts(self) -> None:
        self.shift_sqlite_repository.create(self.sample_shift)
        self.shift_sqlite_repository.add_receipt(self.sample_shift)
        self.shift_sqlite_repository.delete(self.sample_shift.id)
        deleted_shift = self.shift_sqlite_repository.get_one(self.sample_shift.id)
        self.assertIsNone(deleted_shift)

    def test_add_receipt_to_shift(self) -> None:
        self.shift_sqlite_repository.create(self.sample_shift)
        self.sample_receipt.shift_id = self.sample_shift.id
        self.sample_shift.receipts.append(self.sample_receipt)
        self.shift_sqlite_repository.add_receipt(self.sample_shift)
        updated_shift = self.shift_sqlite_repository.get_one(self.sample_shift.id)
        self.assertIsNotNone(updated_shift)


if __name__ == '__main__':
    unittest.main()
