from dataclasses import dataclass

from app.core.factories.repo_factory import RepoFactory
from app.core.interactors.campaign_interactor import CampaignInteractor
from app.core.interactors.payment_interactor import PaymentInteractor
from app.core.interactors.product_interactor import ProductInteractor
from app.core.interactors.receipt_interactor import ReceiptInteractor
from app.core.interactors.shift_interactor import ShiftInteractor
from app.core.models.product import DiscountedProduct
from app.core.models.report import XReport, ZReport
from app.core.schemas.campaign_schema import (
    AddProductInComboRequest,
    AddProductInComboResponse,
    AddProductInDiscountResponse,
    CreateBuyNGetNProductRequest,
    CreateBuyNGetNProductResponse,
    CreateComboRequest,
    CreateComboResponse,
    CreateDiscountRequest,
    CreateDiscountResponse,
    CreateReceiptDiscountRequest,
    CreateReceiptDiscountResponse,
    GetAllCampaignsResponse,
    GetOneCampaignResponse,
)
from app.core.schemas.products_schema import (
    CreateProductRequest,
    CreateProductResponse,
    GetAllProductResponse,
    GetOneProductResponse,
    UpdateProductPriceRequest,
)
from app.core.schemas.receipt_schema import (
    AddComboInReceiptRequest,
    AddGiftInReceiptRequest,
    AddItemInReceiptResponse,
    AddProductInReceiptRequest,
    CreateReceiptRequest,
    CreateReceiptResponse,
    GetOneReceiptResponse,
)
from app.core.schemas.report_schema import ReportResponse
from app.core.schemas.shift_schema import (
    CreateShiftResponse,
    GetOneShiftResponse,
    UpdateShiftStateRequest,
)
from app.core.services.campaign_service import CampaignService
from app.core.services.payment_service import PaymentService
from app.core.services.product_service import ProductService
from app.core.services.receipt_service import ReceiptService
from app.core.services.shift_service import ShiftService
from app.core.state.shift_state import OpenShiftState


@dataclass
class POSCore:
    product_interactor: ProductInteractor
    receipt_interactor: ReceiptInteractor
    shift_interactor: ShiftInteractor
    campaign_interactor: CampaignInteractor
    payment_interactor: PaymentInteractor


    @classmethod
    def create(cls, database: RepoFactory) -> 'POSCore':
        product_service = ProductService(database.products())
        receipt_service = ReceiptService(database.receipts())
        shift_service = ShiftService(database.shifts())
        campaign_service = CampaignService(
            product_discount_repo=database.discount_campaign(),
            receipt_discount_repo=database.receipt_discount_campaign(),
            combo_campaign_repo=database.combo_campaign(),
            buy_get_gift_repo=database.buy_n_get_n_campaign(),
        )
        payment_service = PaymentService()
        return cls(
            product_interactor=ProductInteractor(
                product_service=product_service,
                campaign_service=campaign_service),
            receipt_interactor=ReceiptInteractor(
                receipt_service=receipt_service,
                product_service=product_service,
                shift_service=shift_service,
                campaign_service=campaign_service),
            shift_interactor=ShiftInteractor(shift_service=shift_service),
            campaign_interactor=CampaignInteractor(
                campaign_service=campaign_service,
                product_service=product_service),
            payment_interactor=PaymentInteractor(
                payment_service=payment_service,
                receipt_service=receipt_service,
                shift_service=shift_service),
        )


    # Products
    def create_product(self,
        request: CreateProductRequest) -> CreateProductResponse:
        product = self.product_interactor.execute_create(
            name=request.name,
            barcode=request.barcode,
            price=request.price)
        return CreateProductResponse(product=product)


    def get_all_products(self) -> GetAllProductResponse:
        products = self.product_interactor.execute_get_all()
        return GetAllProductResponse(products=products)

    def get_one_product(self, product_id: str) -> GetOneProductResponse:
        product_decorator = self.product_interactor.execute_get_one(
            product_id=product_id)
        inner_product = product_decorator.inner_product
        product = inner_product

        response = GetOneProductResponse(
            id=product.id,
            name=product.name,
            barcode=product.barcode,
            price=product.get_price())
        if isinstance(product_decorator, DiscountedProduct):
            response.discount = product_decorator.get_price()

        return response

    def update_product_price(self, product_id: str,
                    request: UpdateProductPriceRequest) -> None:
        self.product_interactor.execute_update(
            product_id=product_id,
            price=request.price)
    
    
    
    # Receipts
    def create_receipt(self,
                       request: CreateReceiptRequest) -> CreateReceiptResponse:
        receipt = self.receipt_interactor.execute_create(
            shift_id=request.shift_id)
        return CreateReceiptResponse(
            id=receipt.id,
            items=receipt.items,
            status="open" if receipt.status else "closed",
            total=receipt.get_price())

    def add_product_in_receipt(self, receipt_id: str,
            request: AddProductInReceiptRequest) -> AddItemInReceiptResponse:
        receipt = self.receipt_interactor.execute_addition_product(
            receipt_id=receipt_id,
            product_id=request.product_id,
            quantity=request.quantity)
        return AddItemInReceiptResponse(
            id=receipt.id,
            items=receipt.items,
            status="open" if receipt.status else "closed",
            total=receipt.get_price(),
            discounted_total=receipt.get_discounted_price())

    def add_combo_in_receipt(self, receipt_id: str,
            request: AddComboInReceiptRequest) -> AddItemInReceiptResponse:
        receipt = self.receipt_interactor.execute_addition_combo(
            receipt_id=receipt_id,
            combo_id=request.combo_id,
            quantity=request.quantity)
        return AddItemInReceiptResponse(
            id=receipt.id,
            items=receipt.items,
            status="open" if receipt.status else "closed",
            total=receipt.get_price(),
            discounted_total=receipt.get_discounted_price())

    def add_gift_in_receipt(self, receipt_id: str,
                request: AddGiftInReceiptRequest) -> AddItemInReceiptResponse:
        receipt = self.receipt_interactor.execute_addition_gift(
            receipt_id=receipt_id,
            gift_id=request.gift_campaign_id,
            quantity=request.quantity)
        return AddItemInReceiptResponse(
            id=receipt.id,
            items=receipt.items,
            status="open" if receipt.status else "closed",
            total=receipt.get_price(),
            discounted_total=receipt.get_discounted_price())

    def delete_item_from_receipt(self, receipt_id: str,
                                 item_id: str) -> None:
        self.receipt_interactor.execute_delete_item(
            receipt_id=receipt_id, item_id=item_id)

    def get_one_receipt(self, receipt_id: str) -> GetOneReceiptResponse:
        receipt = self.receipt_interactor.execute_get_one(
            receipt_id=receipt_id)
        return GetOneReceiptResponse(
            id=receipt.id,
            items=receipt.items,
            status="open" if receipt.status else "closed",
            total=receipt.total,
            discounted_total=receipt.discount_total)

    def delete_receipt(self, receipt_id: str) -> None:
        self.receipt_interactor.execute_delete(receipt_id=receipt_id)

    async def pay_receipt(self, receipt_id: str,
                          to_currency: str) -> float:
        converted_amount = await self.payment_interactor.execute_pay(
            receipt_id=receipt_id, to_currency=to_currency)
        return converted_amount


    # Shifts
    def create_shift(self) -> CreateShiftResponse:
        shift = self.shift_interactor.execute_create()
        return CreateShiftResponse(
            id=shift.id,
            receipts=shift.receipts,
            state="Open" if isinstance(shift.state, OpenShiftState) else "Closed")

    def get_one_shift(self, shift_id: str) -> GetOneShiftResponse:
        shift = self.shift_interactor.execute_get_one(shift_id=shift_id)
        return GetOneShiftResponse(
            id=shift.id,
            receipts=shift.receipts,
            state="Open" if isinstance(shift.state, OpenShiftState) else "Closed",
            total=shift.get_price())

    def update_shift_status(self, shift_id: str,
                            request: UpdateShiftStateRequest) -> None:
        self.shift_interactor.execute_change_status(shift_id,
                                                    status=request.status)


    # Campaigns
    def get_one_campaign(self, campaign_id: str) -> GetOneCampaignResponse:
        campaign = self.campaign_interactor.execute_get_one(
            campaign_id=campaign_id)
        return GetOneCampaignResponse(campaign=campaign)

    def get_all_campaigns(self) -> GetAllCampaignsResponse:
        campaigns = self.campaign_interactor.execute_get_all()
        return GetAllCampaignsResponse(campaigns=campaigns)

    def delete_campaigns(self, campaign_id: str) -> None:
        return self.campaign_interactor.execute_delete(
            campaign_id=campaign_id)

    def create_discount_campaign(self,
            request: CreateDiscountRequest) -> CreateDiscountResponse:
        discount = self.campaign_interactor.execute_create_discount(
            discount=request.discount)
        return CreateDiscountResponse(
            id=discount.id,
            campaign_type=discount.campaign_type,
            discount=discount.discount,
            products=discount.products)

    def create_combo_campaign(self,
                              request: CreateComboRequest) -> CreateComboResponse:
        combo = self.campaign_interactor.execute_create_combo(
            discount=request.discount)
        return CreateComboResponse(
            id=combo.id,
            campaign_type=combo.campaign_type,
            discount=combo.discount,
            products=combo.products)

    def create_receipt_discount_campaign(self,
            request: CreateReceiptDiscountRequest) -> CreateReceiptDiscountResponse:
        receipt_discount = self.campaign_interactor.execute_create_receipt_discount(
            discount=request.discount, amount=request.amount)
        return CreateReceiptDiscountResponse(
            id=receipt_discount.id,
            campaign_type=receipt_discount.campaign_type,
            discount=receipt_discount.discount,
            amount=receipt_discount.total)

    def create_buy_n_get_n_campaign(self,
            request: CreateBuyNGetNProductRequest) -> CreateBuyNGetNProductResponse:
        gift = self.campaign_interactor.execute_create_buy_n_get_n(
            buy_product=request.product, gift_product=request.gift)
        return CreateBuyNGetNProductResponse(
            id=gift.id,
            campaign_type=gift.campaign_type,
            buy_product=gift.buy_product,
            gift_product=gift.gift_product)

    def add_product_to_combo(self, campaign_id: str,
            request: AddProductInComboRequest) -> AddProductInComboResponse:
        combo = self.campaign_interactor.execute_adding_in_combo(
            campaign_id=campaign_id,
            product_id=request.product_id,
            quantity=request.quantity)
        return AddProductInComboResponse(
            id=combo.id,
            campaign_type=combo.campaign_type,
            discount=combo.discount,
            products=combo.products)

    def add_product_to_discount(self, campaign_id: str,
                    product_id: str) -> AddProductInDiscountResponse:
        discount = self.campaign_interactor.execute_adding_in_discount(
            campaign_id=campaign_id, product_id=product_id)
        return AddProductInDiscountResponse(
            id=discount.id,
            campaign_type=discount.campaign_type,
            discount=discount.discount,
            products=discount.products)

    def delete_product_from_discount(self,
                    campaign_id: str,
                    product_id: str) -> None:
        self.campaign_interactor.execute_delete_from_discount(
            campaign_id=campaign_id, product_id=product_id)

    # Reports
    def get_xreport(self) -> ReportResponse:
        report = XReport()
        return report.make_report(self.shift_interactor.shift_service)

    def get_zreport(self, shift_id: str) -> ReportResponse:
        report = ZReport(shift_id=shift_id)
        return report.make_report(self.shift_interactor.shift_service)



