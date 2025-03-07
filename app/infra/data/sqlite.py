import json
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Any, List, Optional

from app.core.factories.repo_factory import RepoFactory
from app.core.models import ReceiptItem
from app.core.models.campaign import (
    BuyNGetNCampaign,
    CampaignType,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.product import Product
from app.core.models.receipt import (
    ComboForReceipt,
    GiftForReceipt,
    ProductForReceipt,
    Receipt,
)
from app.core.models.shift import Shift
from app.core.repositories.campaign_repository import (
    IBuyNGetNCampaignRepository,
    IComboCampaignRepository,
    IProductDiscountCampaignRepository,
    IReceiptDiscountCampaignRepository,
)
from app.core.repositories.product_repository import IProductRepository
from app.core.repositories.receipt_repesitory import IReceiptRepository
from app.core.repositories.shift_repository import IShiftRepository
from app.core.state.shift_state import ClosedShiftState, OpenShiftState


@dataclass
class SqliteRepoFactory(RepoFactory):
    connection: sqlite3.Connection

    def __post_init__(self) -> None:
        self._initialize_db()
        self._products = ProductSqliteRepository(self.connection)
        self._receipts = ReceiptSqliteRepository(self.connection)
        self._shifts = ShiftSqliteRepository(self.connection)
        self._discount_campaign = (
            ProductDiscountCampaignSqliteRepository(self.connection))
        self._combo_campaign = (
            ComboCampaignSqliteRepository(self.connection))
        self._receipt_discount_campaign = (
            ReceiptDiscountCampaignSqliteRepository(self.connection))
        self._buy_n_get_n_campaign =\
            BuyNGetNCampaignSqliteRepository(self.connection)

    def _initialize_db(self) -> None:
        cursor = self.connection.cursor()

        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            barcode TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            discount REAL
        )
        ''')

        # Create receipts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id TEXT PRIMARY KEY,
            shift_id TEXT NOT NULL,
            total REAL NOT NULL,
            discount_total REAL,
            status INTEGER NOT NULL
        )
        ''')

        # Create receipt_items table for all types of receipt items
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipt_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_id TEXT KEY,
            receipt_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            discount_price REAL,
            discount_total REAL,
            item_data TEXT NOT NULL,
            FOREIGN KEY (receipt_id) REFERENCES receipts (id)
        )
        ''')

        # Create shifts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id TEXT PRIMARY KEY,
            state TEXT NOT NULL
        )
        ''')

        # Create discount_campaigns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS discount_campaigns (
            id TEXT PRIMARY KEY,
            campaign_type TEXT NOT NULL,
            discount INTEGER NOT NULL
        )
        ''')

        # Create discount_campaign_products table (many-to-many relationship)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS discount_campaign_products (
            campaign_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            PRIMARY KEY (campaign_id, product_id),
            FOREIGN KEY (campaign_id) REFERENCES discount_campaigns(id) 
            ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        ''')

        # Create combo_campaigns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS combo_campaigns (
            id TEXT PRIMARY KEY,
            campaign_type TEXT NOT NULL,
            discount REAL NOT NULL,
            products TEXT NOT NULL
        )
        ''')

        # Create buy_n_get_n_campaigns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS buy_n_get_n_campaigns (
            id TEXT PRIMARY KEY,
            campaign_type TEXT NOT NULL,
            buy_product TEXT NOT NULL,
            gift_product TEXT NOT NULL
        )
        ''')

        # Create receipt_discount_campaigns table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipt_discount_campaigns (
            id TEXT PRIMARY KEY,
            campaign_type TEXT NOT NULL,
            total INTEGER NOT NULL,
            discount INTEGER NOT NULL
        )
        ''')

        self.connection.commit()

    def products(self) -> IProductRepository:
        return ProductSqliteRepository(self.connection)

    def receipts(self) -> IReceiptRepository:
        return ReceiptSqliteRepository(self.connection)

    def shifts(self) -> IShiftRepository:
        return ShiftSqliteRepository(self.connection)

    def discount_campaign(self) -> IProductDiscountCampaignRepository:
        return ProductDiscountCampaignSqliteRepository(self.connection)

    def combo_campaign(self) -> IComboCampaignRepository:
        return ComboCampaignSqliteRepository(self.connection)

    def receipt_discount_campaign(self) -> IReceiptDiscountCampaignRepository:
        return ReceiptDiscountCampaignSqliteRepository(self.connection)

    def buy_n_get_n_campaign(self) -> IBuyNGetNCampaignRepository:
        return BuyNGetNCampaignSqliteRepository(self.connection)


@dataclass
class ProductSqliteRepository(IProductRepository):
    connection: sqlite3.Connection

    def create(self, product: Product) -> Product:
        product_id = str(uuid.uuid4())
        setattr(product, "id", product_id)

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO products (id, name, barcode, price, discount) "
            "VALUES (?, ?, ?, ?, ?)",
            (product.id,
             product.name,
             product.barcode,
             product.price,
             product.discount)
        )
        self.connection.commit()

        return product

    def get_one(self, product_id: str) -> Optional[Product]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, "
                       "name, "
                       "barcode, "
                       "price, "
                       "discount FROM products WHERE id = ?",
                       (product_id,))

        row = cursor.fetchone()
        if row:
            return Product(
                id=row[0],
                name=row[1],
                barcode=row[2],
                price=row[3],
                discount=row[4]
            )
        return None

    def get_all(self) -> List[Product]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, barcode, price, discount "
                       "FROM products")

        products = []
        for row in cursor.fetchall():
            products.append(
                Product(
                    id=row[0],
                    name=row[1],
                    barcode=row[2],
                    price=row[3],
                    discount=row[4]
                )
            )
        return products

    def update(self, product_id: str, price: float) -> None:
        cursor = self.connection.cursor()
        cursor.execute("UPDATE products SET price = ? WHERE id = ?",
                       (price, product_id))
        self.connection.commit()

    def has_barcode(self, barcode: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE barcode = ?",
                       (barcode,))
        count = cursor.fetchone()[0]
        return bool(count > 0)


@dataclass
class ReceiptSqliteRepository(IReceiptRepository):
    connection: sqlite3.Connection

    def create(self, receipt: Receipt) -> Receipt:
        receipt_id = str(uuid.uuid4())
        setattr(receipt, "id", receipt_id)

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO receipts (id,"
            " shift_id,"
            " total, "
            "discount_total,"
            " status) VALUES (?, ?, ?, ?, ?)",
            (receipt.id,
             receipt.shift_id,
             receipt.total,
             receipt.discount_total,
             receipt.status)
        )

        # Save all items in the receipt
        for item in receipt.items:
            self._save_receipt_item(cursor, receipt.id, item)

        self.connection.commit()
        return receipt

    def add_product(self, receipt: Receipt) -> Receipt:
        cursor = self.connection.cursor()

        # Update the receipt record
        cursor.execute(
            "UPDATE receipts SET total = ?, "
            "discount_total = ? WHERE id = ?",
            (receipt.total, receipt.discount_total, receipt.id)
        )

        # Delete all existing items for this receipt
        cursor.execute("DELETE FROM receipt_items WHERE receipt_id = ?",
                       (receipt.id,))

        # Save all items in the receipt (including the new one)
        for item in receipt.items:
            self._save_receipt_item(cursor, receipt.id, item)

        self.connection.commit()
        return receipt

    def _save_receipt_item(self, cursor: sqlite3.Cursor,
                           receipt_id: str,
                           item: ReceiptItem) -> None:
        # Determine the item type and serialize the specific data
        item_type = self._get_item_type(item)
        item_data = self._serialize_item_data(item)

        cursor.execute(
            """
            INSERT INTO receipt_items 
            (item_id, 
             receipt_id,
             item_type,
              quantity, 
              price, 
              total, 
              discount_price,
              discount_total, 
              item_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                receipt_id,
                item_type,
                item.quantity,
                item.price,
                item.total,
                item.discount_price,
                item.discount_total,
                item_data
            )
        )

    def _get_item_type(self, item: Any) -> str:
        if isinstance(item, ProductForReceipt):
            return "ProductForReceipt"
        elif isinstance(item, ComboForReceipt):
            return "ComboForReceipt"
        elif isinstance(item, GiftForReceipt):
            return "GiftForReceipt"
        else:
            raise ValueError(f"Unknown receipt item type: {type(item)}")

    def _serialize_item_data(self, item: Any) -> str:
        if isinstance(item, ProductForReceipt):
            return json.dumps({})
        elif isinstance(item, ComboForReceipt):
            # Serialize all products in the combo
            return json.dumps({
                "products": [
                    {
                        "item_id": product.id,
                        "quantity": product.quantity,
                        "price": product.price,
                        "total": product.total,
                        "discount_price": product.discount_price,
                        "discount_total": product.discount_total
                    } for product in item.products
                ]
            })
        elif isinstance(item, GiftForReceipt):
            # Serialize the buy and gift products
            return json.dumps({
                "buy_product": {
                    "item_id": item.buy_product.id,
                    "quantity": item.buy_product.quantity,
                    "price": item.buy_product.price,
                    "total": item.buy_product.total,
                    "discount_price": item.buy_product.discount_price,
                    "discount_total": item.buy_product.discount_total
                },
                "gift_product": {
                    "item_id": item.gift_product.id,
                    "quantity": item.gift_product.quantity,
                    "price": item.gift_product.price,
                    "total": item.gift_product.total,
                    "discount_price": item.gift_product.discount_price,
                    "discount_total": item.gift_product.discount_total
                }
            })
        else:
            raise ValueError(f"Unknown receipt item type: {type(item)}")

    def _deserialize_receipt_item(self, row: tuple) -> ReceiptItem:
        (item_id,
         receipt_id,
         item_type,
         quantity,
         price,
         total,
         discount_price,
         discount_total,
         item_data_str) = row
        item_data = json.loads(item_data_str)

        if item_type == "ProductForReceipt":
            return ProductForReceipt(
                id=item_id,
                quantity=quantity,
                price=price,
                total=total,
                discount_price=discount_price,
                discount_total=discount_total
            )
        elif item_type == "ComboForReceipt":
            products = []
            for product_data in item_data.get("products", []):
                products.append(
                    ProductForReceipt(
                        id=product_data["item_id"],
                        quantity=product_data["quantity"],
                        price=product_data["price"],
                        total=product_data["total"],
                        discount_price=product_data.get("discount_price"),
                        discount_total=product_data.get("discount_total")
                    )
                )

            return ComboForReceipt(
                id=item_id,
                products=products,
                quantity=quantity,
                price=price,
                total=total,
                discount_price=discount_price,
                discount_total=discount_total
            )
        elif item_type == "GiftForReceipt":
            buy_product_data = item_data["buy_product"]
            gift_product_data = item_data["gift_product"]

            buy_product = ProductForReceipt(
                id=buy_product_data["item_id"],
                quantity=buy_product_data["quantity"],
                price=buy_product_data["price"],
                total=buy_product_data["total"],
                discount_price=buy_product_data.get("discount_price"),
                discount_total=buy_product_data.get("discount_total")
            )

            gift_product = ProductForReceipt(
                id=gift_product_data["item_id"],
                quantity=gift_product_data["quantity"],
                price=gift_product_data["price"],
                total=gift_product_data["total"],
                discount_price=gift_product_data.get("discount_price"),
                discount_total=gift_product_data.get("discount_total")
            )

            return GiftForReceipt(
                id=item_id,
                buy_product=buy_product,
                gift_product=gift_product,
                quantity=quantity,
                price=price,
                total=total,
                discount_price=discount_price,
                discount_total=discount_total
            )
        else:
            raise ValueError(f"Unknown receipt item type: {item_type}")

    def get_one(self, receipt_id: str) -> Optional[Receipt]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, shift_id, total, discount_total, status "
            "FROM receipts WHERE id = ?",
            (receipt_id,)
        )

        receipt_row = cursor.fetchone()
        if not receipt_row:
            return None

        # Get all items for this receipt
        cursor.execute(
            """
            SELECT item_id,
             receipt_id, 
             item_type, 
             quantity,
              price,
               total, 
               discount_price, 
               discount_total, 
               item_data 
            FROM receipt_items 
            WHERE receipt_id = ?
            """,
            (receipt_id,)
        )

        items = []
        for item_row in cursor.fetchall():
            items.append(self._deserialize_receipt_item(item_row))

        return Receipt(
            id=receipt_row[0],
            shift_id=receipt_row[1],
            items=items,
            total=receipt_row[2],
            discount_total=receipt_row[3],
            status=bool(receipt_row[4])
        )

    def get_all(self) -> List[Receipt]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, shift_id, total, discount_total, status"
                       " FROM receipts")

        receipts = []
        for receipt_row in cursor.fetchall():
            receipt_id = receipt_row[0]

            # Get all items for this receipt
            cursor.execute(
                """
                SELECT item_id, 
                receipt_id,
                 item_type,
                  quantity, 
                  price,
                   total,
                   discount_price,
                    discount_total,
                     item_data 
                FROM receipt_items 
                WHERE receipt_id = ?
                """,
                (receipt_id,)
            )

            items = []
            for item_row in cursor.fetchall():
                items.append(self._deserialize_receipt_item(item_row))

            receipts.append(
                Receipt(
                    id=receipt_id,
                    shift_id=receipt_row[1],
                    items=items,
                    total=receipt_row[2],
                    discount_total=receipt_row[3],
                    status=bool(receipt_row[4])
                )
            )

        return receipts

    def update(self, receipt_id: str, status: bool) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE receipts SET status = ? WHERE id = ?",
            (status, receipt_id)
        )
        self.connection.commit()

    def delete(self, receipt_id: str) -> None:
        cursor = self.connection.cursor()

        # First delete all items related to this receipt
        cursor.execute("DELETE FROM receipt_items "
                       "WHERE receipt_id = ?", (receipt_id,))

        # Then delete the receipt itself
        cursor.execute("DELETE FROM receipts WHERE id = ?",
                       (receipt_id,))

        self.connection.commit()

    def delete_item(self, receipt: Receipt) -> None:
        self.add_product(receipt)


@dataclass
class ShiftSqliteRepository(IShiftRepository):
    connection: sqlite3.Connection

    def create(self, shift: Shift) -> Shift:
        shift_id = str(uuid.uuid4())
        setattr(shift, "id", shift_id)

        cursor = self.connection.cursor()

        # Convert state to string representation
        state_str = "open" if isinstance(shift.state, OpenShiftState) else "closed"

        cursor.execute(
            "INSERT INTO shifts (id, state) VALUES (?, ?)",
            (shift.id, state_str)
        )

        # Save all receipts in the shift (initially empty for a new shift)
        for receipt in shift.receipts:
            # Update the shift_id for the receipt
            receipt.shift_id = shift.id

            # Use the receipt repository to save the receipt
            cursor.execute(
                "UPDATE receipts SET shift_id = ? WHERE id = ?",
                (shift.id, receipt.id)
            )

        self.connection.commit()
        return shift

    def get_one(self, shift_id: str) -> Optional[Shift]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, state FROM shifts WHERE id = ?",
                       (shift_id,))

        shift_row = cursor.fetchone()
        if not shift_row:
            return None

        # Get all receipts for this shift
        cursor.execute("SELECT id FROM receipts WHERE shift_id = ?",
                       (shift_id,))

        receipt_ids = [row[0] for row in cursor.fetchall()]
        receipts = []

        # For each receipt, get the full receipt object
        receipt_repo = ReceiptSqliteRepository(self.connection)
        for receipt_id in receipt_ids:
            receipt = receipt_repo.get_one(receipt_id)
            if receipt:
                if receipt:
                    if not receipt.status:
                        receipts.append(receipt)

        # Create the shift state
        state_str = shift_row[1]
        state = OpenShiftState() if state_str == "open" else ClosedShiftState()

        return Shift(
            id=shift_row[0],
            receipts=receipts,
            state=state
        )

    def add_receipt(self, shift: Shift) -> Shift:
        cursor = self.connection.cursor()

        # Update the state of the shift
        state_str = "open" if isinstance(shift.state, OpenShiftState) else "closed"
        cursor.execute(
            "UPDATE shifts SET state = ? WHERE id = ?",
            (state_str, shift.id)
        )

        # For each receipt, ensure it's properly linked to this shift
        for receipt in shift.receipts:
            cursor.execute(
                "UPDATE receipts SET shift_id = ? WHERE id = ?",
                (shift.id, receipt.id)
            )

        self.connection.commit()
        return shift

    def get_all(self) -> List[Shift]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, state FROM shifts")

        shifts = []
        receipt_repo = ReceiptSqliteRepository(self.connection)

        for shift_row in cursor.fetchall():
            shift_id = shift_row[0]

            # Get all receipts for this shift
            cursor.execute("SELECT id FROM receipts WHERE shift_id = ?",
                           (shift_id,))

            receipt_ids = [row[0] for row in cursor.fetchall()]
            receipts = []

            # For each receipt, get the full receipt object
            for receipt_id in receipt_ids:
                receipt = receipt_repo.get_one(receipt_id)
                if receipt:
                    if not receipt.status:
                        receipts.append(receipt)

            # Create the shift state
            state_str = shift_row[1]
            state = OpenShiftState() if state_str == "open" else ClosedShiftState()

            shifts.append(
                Shift(
                    id=shift_id,
                    receipts=receipts,
                    state=state
                )
            )

        return shifts

    def update(self, shift_id: str, status: bool) -> None:
        cursor = self.connection.cursor()
        state_str = "open" if status else "closed"
        cursor.execute(
            "UPDATE shifts SET state = ? WHERE id = ?",
            (state_str, shift_id)
        )
        self.connection.commit()

    def delete(self, shift_id: str) -> None:
        cursor = self.connection.cursor()

        # First, get all receipts for this shift
        cursor.execute("SELECT id FROM receipts WHERE shift_id = ?",
                       (shift_id,))
        receipt_ids = [row[0] for row in cursor.fetchall()]

        # Delete all receipt_items for these receipts
        for receipt_id in receipt_ids:
            cursor.execute("DELETE FROM receipt_items WHERE receipt_id = ?",
                           (receipt_id,))

        # Delete all receipts for this shift
        cursor.execute("DELETE FROM receipts WHERE shift_id = ?",
                       (shift_id,))

        # Then delete the shift itself
        cursor.execute("DELETE FROM shifts WHERE id = ?",
                       (shift_id,))

        self.connection.commit()


class ProductDiscountCampaignSqliteRepository(
    IProductDiscountCampaignRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create(self,
    discount_campaign: DiscountCampaign) -> DiscountCampaign:
        campaign_id = str(uuid.uuid4())
        discount_campaign.id = campaign_id
        self.connection.execute(
            "INSERT INTO discount_campaigns (id, campaign_type, discount)"
            " VALUES (?, ?, ?)",
            (campaign_id, discount_campaign.campaign_type.value,
             discount_campaign.discount)
        )
        self.connection.commit()
        for product_id in discount_campaign.products:
            self.connection.execute(
                "INSERT INTO discount_campaign_products (campaign_id,"
                " product_id)"
                " VALUES (?, ?)",
                (campaign_id, product_id)
            )
        self.connection.commit()
        return discount_campaign

    def get_one_campaign(self, campaign_id: str) -> Optional[DiscountCampaign]:
        cursor = self.connection.execute(
            "SELECT id, campaign_type, discount"
            " FROM discount_campaigns WHERE id = ?",
            (campaign_id,)
        )
        row = cursor.fetchone()
        if row:
            cursor_products = self.connection.execute(
                "SELECT product_id FROM discount_campaign_products "
                "WHERE campaign_id = ?",
                (campaign_id,)
            )
            products = [r[0] for r in cursor_products.fetchall()]
            return DiscountCampaign(id=row[0],
                                    campaign_type=CampaignType(row[1]),
                                    discount=row[2],
                                    products=products)

        return None

    def get_all(self) -> List[DiscountCampaign]:
        cursor = self.connection.execute("SELECT id, campaign_type, "
                                         "discount FROM discount_campaigns")
        campaigns = []
        for row in cursor.fetchall():
            campaign_id = row[0]
            cursor_products = self.connection.execute(
                "SELECT product_id "
                "FROM discount_campaign_products WHERE campaign_id = ?",
                (campaign_id,)
            )
            products = [r[0] for r in cursor_products.fetchall()]
            campaigns.append(DiscountCampaign(id=campaign_id,
                                              campaign_type=CampaignType(row[1]),
                                              discount=row[2],
                                              products=products))
        return campaigns

    def add_product(self, product_id: str,
                    campaign_id: str) -> Optional[DiscountCampaign]:
        self.connection.execute(
            "INSERT INTO discount_campaign_products "
            "(campaign_id, product_id) VALUES (?, ?)",
            (campaign_id, product_id)
        )
        self.connection.commit()
        return self.get_one_campaign(campaign_id)

    def delete_product(self, product_id: str, campaign_id: str) -> None:
        self.connection.execute(
            "DELETE FROM discount_campaign_products"
            " WHERE campaign_id = ? AND product_id = ?",
            (campaign_id, product_id)
        )
        self.connection.commit()

    def delete_campaign(self, campaign_id: str) -> None:
        self.connection.execute("DELETE FROM discount_campaigns"
                                " WHERE id = ?",
                                (campaign_id,))
        self.connection.commit()

    def get_campaign_with_product(self, product_id: str) -> Optional[DiscountCampaign]:
        cursor = self.connection.execute(
            """SELECT dc.id, dc.campaign_type, dc.discount 
               FROM discount_campaigns dc
               INNER JOIN discount_campaign_products dcp ON dc.id = dcp.campaign_id
               WHERE dcp.product_id = ?
               ORDER BY dc.discount DESC
               LIMIT 1""",
            (product_id,)
        )
        row = cursor.fetchone()
        if row:
            cursor_products = self.connection.execute(
                "SELECT product_id FROM discount_campaign_products "
                "WHERE campaign_id = ?",
                (row[0],)
            )
            products = [r[0] for r in cursor_products.fetchall()]
            return DiscountCampaign(id=row[0],
                                    campaign_type=CampaignType(row[1]),
                                    discount=row[2],
                                    products=products)

        return None

class ComboCampaignSqliteRepository(IComboCampaignRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create(self, combo_campaign: ComboCampaign) -> ComboCampaign:
        campaign_id = str(uuid.uuid4())
        combo_campaign.id = campaign_id

        # Serialize product data to JSON
        products_data = json.dumps([{
            "id": p.id,
            "quantity": p.quantity,
            "price": p.price,
            "total": p.total,
            "discount_price": p.discount_price,
            "discount_total": p.discount_total
        } for p in combo_campaign.products])

        self.connection.execute(
            "INSERT INTO combo_campaigns"
            " (id, campaign_type, discount, products) "
            "VALUES (?, ?, ?, ?)",
            (campaign_id,
             combo_campaign.campaign_type.value,
             combo_campaign.discount,
             products_data)
        )
        self.connection.commit()
        return combo_campaign

    def get_all(self) -> List[ComboCampaign]:
        cursor = self.connection.execute("SELECT id, "
                                         "campaign_type,"
                                         " discount, "
                                         "products FROM combo_campaigns")
        campaigns = []
        for row in cursor.fetchall():
            campaign_id = row[0]
            campaign_type = CampaignType(row[1])
            discount = row[2]

            # Deserialize product data from JSON
            products_data = json.loads(row[3])
            products = []
            for product_data in products_data:
                products.append(ProductForReceipt(
                    id=product_data["id"],
                    quantity=product_data["quantity"],
                    price=product_data["price"],
                    total=product_data["total"],
                    discount_price=product_data.get("discount_price"),
                    discount_total=product_data.get("discount_total")
                ))

            campaigns.append(
                ComboCampaign(id=campaign_id,
                              campaign_type=campaign_type,
                              discount=discount,
                              products=products))
        return campaigns

    def get_one_campaign(self, campaign_id: str) -> Optional[ComboCampaign]:
        cursor = self.connection.execute(
            "SELECT id, campaign_type, discount, products"
            " FROM combo_campaigns WHERE id = ?",
            (campaign_id,)
        )
        row = cursor.fetchone()
        if row:
            campaign_type = CampaignType(row[1])
            discount = row[2]

            # Deserialize product data from JSON
            products_data = json.loads(row[3])
            products = []
            for product_data in products_data:
                products.append(ProductForReceipt(
                    id=product_data["id"],
                    quantity=product_data["quantity"],
                    price=product_data["price"],
                    total=product_data["total"],
                    discount_price=product_data.get("discount_price"),
                    discount_total=product_data.get("discount_total")
                ))

            return ComboCampaign(id=row[0],
                                 campaign_type=campaign_type,
                                 discount=discount,
                                 products=products)


        return None

    def add_product(self, product: ProductForReceipt,
                    campaign_id: str) -> Optional[ComboCampaign]:
        # Get current campaign
        campaign = self.get_one_campaign(campaign_id)
        if not campaign:
            return None

        # Add product to the list
        campaign.products.append(product)

        # Update products JSON in database
        products_data = json.dumps([{
            "id": p.id,
            "quantity": p.quantity,
            "price": p.price,
            "total": p.total,
            "discount_price": p.discount_price,
            "discount_total": p.discount_total
        } for p in campaign.products])

        self.connection.execute(
            "UPDATE combo_campaigns SET products = ? WHERE id = ?",
            (products_data, campaign_id)
        )
        self.connection.commit()
        return campaign

    def delete_campaign(self, campaign_id: str) -> None:
        self.connection.execute("DELETE FROM combo_campaigns WHERE id = ?",
                                (campaign_id,))
        self.connection.commit()


class BuyNGetNCampaignSqliteRepository(IBuyNGetNCampaignRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create(self, buy_n_get_n_campaign: BuyNGetNCampaign) -> BuyNGetNCampaign:
        campaign_id = str(uuid.uuid4())
        buy_n_get_n_campaign.id = campaign_id

        # Serialize buy_product and gift_product to JSON
        buy_product_data = json.dumps({
            "id": buy_n_get_n_campaign.buy_product.id,
            "quantity": buy_n_get_n_campaign.buy_product.quantity,
            "price": buy_n_get_n_campaign.buy_product.price,
            "total": buy_n_get_n_campaign.buy_product.total,
            "discount_price": buy_n_get_n_campaign.buy_product.discount_price,
            "discount_total": buy_n_get_n_campaign.buy_product.discount_total
        })

        gift_product_data = json.dumps({
            "id": buy_n_get_n_campaign.gift_product.id,
            "quantity": buy_n_get_n_campaign.gift_product.quantity,
            "price": buy_n_get_n_campaign.gift_product.price,
            "total": buy_n_get_n_campaign.gift_product.total,
            "discount_price": buy_n_get_n_campaign.gift_product.discount_price,
            "discount_total": buy_n_get_n_campaign.gift_product.discount_total
        })

        self.connection.execute(
            "INSERT INTO buy_n_get_n_campaigns "
            "(id, campaign_type, buy_product, gift_product) "
            "VALUES (?, ?, ?, ?)",
            (campaign_id,
             buy_n_get_n_campaign.campaign_type.value,
             buy_product_data,
             gift_product_data)
        )
        self.connection.commit()
        return buy_n_get_n_campaign

    def get_all(self) -> List[BuyNGetNCampaign]:
        cursor = self.connection.execute(
            "SELECT id, campaign_type, buy_product, gift_product "
            "FROM buy_n_get_n_campaigns")
        campaigns = []
        for row in cursor.fetchall():
            campaign_id = row[0]
            campaign_type = CampaignType(row[1])

            # Deserialize buy_product data
            buy_product_data = json.loads(row[2])
            buy_product = ProductForReceipt(
                id=buy_product_data["id"],
                quantity=buy_product_data["quantity"],
                price=buy_product_data["price"],
                total=buy_product_data["total"],
                discount_price=buy_product_data.get("discount_price"),
                discount_total=buy_product_data.get("discount_total")
            )

            # Deserialize gift_product data
            gift_product_data = json.loads(row[3])
            gift_product = ProductForReceipt(
                id=gift_product_data["id"],
                quantity=gift_product_data["quantity"],
                price=gift_product_data["price"],
                total=gift_product_data["total"],
                discount_price=gift_product_data.get("discount_price"),
                discount_total=gift_product_data.get("discount_total")
            )

            campaigns.append(BuyNGetNCampaign(
                id=campaign_id,
                campaign_type=campaign_type,
                buy_product=buy_product,
                gift_product=gift_product
            ))
        return campaigns

    def get_one_campaign(self, campaign_id: str) -> Optional[BuyNGetNCampaign]:
        cursor = self.connection.execute(
            "SELECT id, campaign_type, buy_product, gift_product"
            " FROM buy_n_get_n_campaigns WHERE id = ?",
            (campaign_id,)
        )
        row = cursor.fetchone()
        if row:
            campaign_type = CampaignType(row[1])

            # Deserialize buy_product data
            buy_product_data = json.loads(row[2])
            buy_product = ProductForReceipt(
                id=buy_product_data["id"],
                quantity=buy_product_data["quantity"],
                price=buy_product_data["price"],
                total=buy_product_data["total"],
                discount_price=buy_product_data.get("discount_price"),
                discount_total=buy_product_data.get("discount_total")
            )

            # Deserialize gift_product data
            gift_product_data = json.loads(row[3])
            gift_product = ProductForReceipt(
                id=gift_product_data["id"],
                quantity=gift_product_data["quantity"],
                price=gift_product_data["price"],
                total=gift_product_data["total"],
                discount_price=gift_product_data.get("discount_price"),
                discount_total=gift_product_data.get("discount_total")
            )

            return BuyNGetNCampaign(
                id=row[0],
                campaign_type=campaign_type,
                buy_product=buy_product,
                gift_product=gift_product
            )

        return None

    def delete_campaign(self, campaign_id: str) -> None:
        self.connection.execute("DELETE FROM buy_n_get_n_campaigns "
                                "WHERE id = ?",
                                (campaign_id,))
        self.connection.commit()


class ReceiptDiscountCampaignSqliteRepository(
    IReceiptDiscountCampaignRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create(self, receipt_campaign: ReceiptCampaign) -> ReceiptCampaign:
        campaign_id = str(uuid.uuid4())
        receipt_campaign.id = campaign_id
        self.connection.execute(
            "INSERT INTO receipt_discount_campaigns"
            " (id, campaign_type, total, discount) VALUES (?, ?, ?, ?)",
            (campaign_id,
             receipt_campaign.campaign_type.value,
             receipt_campaign.total,
             receipt_campaign.discount)
        )
        self.connection.commit()
        return receipt_campaign

    def get_one_campaign(self, campaign_id: str) -> Optional[ReceiptCampaign]:
        cursor = self.connection.execute(
            "SELECT"
            " id, "
            "campaign_type, "
            "total,"
            " discount FROM receipt_discount_campaigns "
            "WHERE id = ?",
            (campaign_id,)
        )
        row = cursor.fetchone()
        if row:
            return ReceiptCampaign(id=row[0],
                                   campaign_type=CampaignType(row[1]),
                                   total=row[2],
                                   discount=row[3])

        return None

    def get_all(self) -> List[ReceiptCampaign]:
        cursor = self.connection.execute("SELECT id, "
                                         "campaign_type, "
                                         "total, "
                                         "discount FROM receipt_discount_campaigns")
        campaigns = []
        for row in cursor.fetchall():
            campaigns.append(
                ReceiptCampaign(id=row[0],
                                campaign_type=CampaignType(row[1]),
                                total=row[2],
                                discount=row[3]))
        return campaigns

    def delete_campaign(self, campaign_id: str) -> None:
        self.connection.execute("DELETE FROM receipt_discount_campaigns "
                                "WHERE id = ?", (campaign_id,))
        self.connection.commit()

    def get_discount_on_amount(self, amount: float) -> Optional[ReceiptCampaign]:
        cursor = self.connection.execute(
            "SELECT id,"
            " campaign_type,"
            " total, "
            "discount FROM receipt_discount_campaigns"
            " WHERE total <= ? ORDER BY discount DESC LIMIT 1",
            (amount,)
        )
        row = cursor.fetchone()
        if row:
            return ReceiptCampaign(id=row[0],
                                   campaign_type=CampaignType(row[1]),
                                   total=row[2],
                                   discount=row[3])


        return None
