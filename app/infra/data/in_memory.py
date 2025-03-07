import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.core.factories.repo_factory import RepoFactory
from app.core.models.campaign import (
    BuyNGetNCampaign,
    ComboCampaign,
    DiscountCampaign,
    ReceiptCampaign,
)
from app.core.models.product import Product
from app.core.models.receipt import ProductForReceipt, Receipt
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
class ProductInMemoryRepository(IProductRepository):
    _store: Dict[str, Product] = field(default_factory=dict)

    def create(self, product: Product) -> Product:
        product_id = str(uuid.uuid4())
        setattr(product, "id", product_id)
        self._store[product_id] = product
        return product

    def get_one(self, product_id: str) -> Optional[Product]:
        return self._store.get(product_id)

    def get_all(self) -> List[Product]:
        return list(self._store.values())

    def update(self, product_id: str, price: float) -> None:
        product = self._store[product_id]
        product.price = price


    def has_barcode(self, barcode: str) -> bool:
        return any(product.barcode == barcode for product in self._store.values())



@dataclass
class ReceiptInMemoryRepository(IReceiptRepository):
    _store: Dict[str, Receipt] = field(default_factory=dict)

    def create(self, receipt: Receipt) -> Receipt:
        receipt_id = str(uuid.uuid4())
        setattr(receipt, "id", receipt_id)
        self._store[receipt_id] = receipt
        return receipt

    def add_product(self, receipt: Receipt) -> Receipt:
        self._store[receipt.id] = receipt
        return receipt

    def get_one(self, receipt_id: str) -> Optional[Receipt]:
        return self._store.get(receipt_id)

    def get_all(self) -> List[Receipt]:
        return list(self._store.values())

    def update(self, receipt_id: str, status: bool) -> None:
        receipt = self._store[receipt_id]
        receipt.status = status

    def delete(self, receipt_id: str) -> None:
        self._store.pop(receipt_id)

    def delete_item(self, receipt: Receipt) -> None:
        self._store[receipt.id] = receipt



@dataclass
class ShiftInMemoryRepository(IShiftRepository):
    _store: Dict[str, Shift] = field(default_factory=dict)

    def create(self, shift: Shift) -> Shift:
        shift_id = str(uuid.uuid4())
        setattr(shift, "id", shift_id)
        self._store[shift_id] = shift
        return shift

    def get_one(self, shift_id: str) -> Optional[Shift]:
        return self._store.get(shift_id)

    def add_receipt(self, shift: Shift) -> Shift:
        self._store[shift.id] = shift
        return shift

    def get_all(self) -> List[Shift]:
        return list(self._store.values())

    def update(self, shift_id: str, status: bool) -> None:
        shift = self._store[shift_id]
        shift.state = OpenShiftState if status else ClosedShiftState

    def delete(self, shift_id: str) -> None:
        self._store.pop(shift_id)



@dataclass
class ProductDiscountCampaignInMemoryRepository(
    IProductDiscountCampaignRepository):
    _store: Dict[str, DiscountCampaign] = field(default_factory=dict)

    def create(self,
               discount_campaign: DiscountCampaign) -> DiscountCampaign:
        campaign_id = str(uuid.uuid4())
        setattr(discount_campaign, "id", campaign_id)
        self._store[campaign_id] = discount_campaign
        return discount_campaign

    def get_one_campaign(self,
                         campaign_id: str) -> Optional[DiscountCampaign]:
        return self._store.get(campaign_id)

    def get_all(self) -> List[DiscountCampaign]:
        return list(self._store.values())

    def add_product(self,
                    product_id: str,
                    campaign_id: str) -> Optional[DiscountCampaign]:
        campaign = self._store[campaign_id]
        campaign.products.append(product_id)
        return campaign

    def delete_product(self,
                       product_id: str,
                       campaign_id: str) -> None:
        campaign = self._store[campaign_id]
        campaign.products.remove(product_id)

    def delete_campaign(self, campaign_id: str) -> None:
        self._store.pop(campaign_id)

    def get_campaign_with_product(self,
                        product_id: str) -> Optional[DiscountCampaign]:
        ret_campaign = None
        max_discount = 0
        for campaign in self._store.values():
            for product in campaign.products:
                if product_id == product:
                    if ret_campaign is None:
                        ret_campaign = campaign
                        max_discount = campaign.discount
                    elif max_discount < campaign.discount:
                        max_discount = campaign.discount
                        ret_campaign = campaign

        return ret_campaign


@dataclass
class ComboCampaignInMemoryRepository(IComboCampaignRepository):
    _store: Dict[str, ComboCampaign]= field(default_factory=dict)

    def create(self, combo_campaign: ComboCampaign) -> ComboCampaign:
        campaign_id = str(uuid.uuid4())
        setattr(combo_campaign, "id", campaign_id)
        self._store[campaign_id] = combo_campaign
        return combo_campaign

    def get_all(self) -> List[ComboCampaign]:
        return list(self._store.values())

    def get_one_campaign(self, campaign_id: str) -> Optional[ComboCampaign]:
        return self._store.get(campaign_id)

    def add_product(self,
                    product: ProductForReceipt,
                    campaign_id: str) -> ComboCampaign:
        campaign = self._store[campaign_id]
        campaign.products.append(product) 
        return campaign

    def delete_campaign(self, campaign_id: str) -> None:
        self._store.pop(campaign_id)


@dataclass
class BuyNGetNCampaignInMemoryRepository(IBuyNGetNCampaignRepository):
    _store: Dict[str, BuyNGetNCampaign] = field(default_factory=dict)

    def create(self,
               buy_n_get_n_campaign: BuyNGetNCampaign) -> BuyNGetNCampaign:
        campaign_id = str(uuid.uuid4())
        setattr(buy_n_get_n_campaign, "id", campaign_id)
        self._store[campaign_id] = buy_n_get_n_campaign
        return buy_n_get_n_campaign


    def get_all(self) -> List[BuyNGetNCampaign]:
        return list(self._store.values())

    def get_one_campaign(self, campaign_id: str) -> Optional[BuyNGetNCampaign]:
        return self._store.get(campaign_id)

    def delete_campaign(self, campaign_id: str) -> None:
        self._store.pop(campaign_id)


@dataclass
class ReceiptDiscountCampaignInMemoryRepository(
    IReceiptDiscountCampaignRepository):
    _store: Dict[str, ReceiptCampaign] = field(default_factory=dict)

    def create(self,
            receipt_campaign: ReceiptCampaign) -> ReceiptCampaign:
        campaign_id = str(uuid.uuid4())
        setattr(receipt_campaign, "id", campaign_id)
        self._store[campaign_id] = receipt_campaign
        return receipt_campaign

    def get_one_campaign(self, campaign_id: str) -> Optional[ReceiptCampaign]:
        return self._store.get(campaign_id)

    def get_all(self) -> List[ReceiptCampaign]:
        return list(self._store.values())

    def delete_campaign(self, campaign_id: str) -> None:
        self._store.pop(campaign_id)

    def get_discount_on_amount(self, amount: float) -> Optional[ReceiptCampaign]:
        ret_campaign = None
        max_discount = 0
        for campaign in self._store.values():
            if amount >= campaign.total:
                if max_discount < campaign.discount:
                    max_discount = campaign.discount
                    ret_campaign = campaign

        return ret_campaign



@dataclass
class InMemoryRepoFactory(RepoFactory):
    _products: ProductInMemoryRepository = field(
        init=False,
        default_factory=ProductInMemoryRepository,
    )

    _receipts: ReceiptInMemoryRepository = field(
        init=False,
        default_factory=ReceiptInMemoryRepository,
    )

    _shifts: ShiftInMemoryRepository = field(
        init=False,
        default_factory=ShiftInMemoryRepository,
    )

    _discount_campaign: ProductDiscountCampaignInMemoryRepository = field(
        init=False,
        default_factory=ProductDiscountCampaignInMemoryRepository,
    )

    _combo_campaign: ComboCampaignInMemoryRepository = field(
        init=False,
        default_factory=ComboCampaignInMemoryRepository,
    )

    _receipt_discount_campaign: ReceiptDiscountCampaignInMemoryRepository = field(
        init=False,
        default_factory=ReceiptDiscountCampaignInMemoryRepository,
    )

    _buy_n_get_n_campaign: BuyNGetNCampaignInMemoryRepository = field(
        init=False,
        default_factory=BuyNGetNCampaignInMemoryRepository,
    )

    def products(self) -> IProductRepository:
        return self._products

    def receipts(self) -> IReceiptRepository:
        return self._receipts

    def shifts(self) -> IShiftRepository:
        return self._shifts

    def discount_campaign(self) -> IProductDiscountCampaignRepository:
        return self._discount_campaign

    def combo_campaign(self) -> IComboCampaignRepository:
        return self._combo_campaign

    def receipt_discount_campaign(self) -> IReceiptDiscountCampaignRepository:
        return self._receipt_discount_campaign

    def buy_n_get_n_campaign(self) -> IBuyNGetNCampaignRepository:
        return self._buy_n_get_n_campaign

