
from decimal import Decimal

from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import User
from organizations.models import Organization, Membership
from products.models import Category, Product
from suppliers.models import Supplier
from purchasing.models import PurchaseOrder
from purchasing.services import (
    create_purchase_order,
    place_purchase_order,
    receive_purchase_order_item,
)
from inventory.models import Inventory, StockMovement


class PurchaseOrderWorkflowTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpassword123",
        )

        self.organization = Organization.objects.create(
            name="Test Business",
            owner=self.user,
        )

        Membership.objects.create(
            organization=self.organization,
            user=self.user,
            role=Membership.Role.OWNER,
        )

        self.category = Category.objects.create(
            organization=self.organization,
            name="Electronics",
        )

        self.product = Product.objects.create(
            organization=self.organization,
            category=self.category,
            name="Wireless Mouse",
            sku="MOUSE-001",
            cost_price=Decimal("300.00"),
            selling_price=Decimal("500.00"),
            unit="piece",
        )

        self.supplier = Supplier.objects.create(
            organization=self.organization,
            name="Test Supplier",
            phone="9999999999",
        )

        self.order = create_purchase_order(
            organization=self.organization,
            supplier=self.supplier,
            order_number="PO-TEST-001",
            created_by=self.user,
            items=[
                {
                    "product": self.product,
                    "quantity_ordered": 20,
                    "unit_cost": Decimal("350.00"),
                }
            ],
        )

        self.item = self.order.items.get(product=self.product)

    def test_purchase_order_created(self):
        self.assertEqual(self.order.status, PurchaseOrder.Status.DRAFT)
        self.assertEqual(self.order.items.count(), 1)

    def test_purchase_order_total_amount(self):
        self.assertEqual(
            self.order.total_amount,
            Decimal("7000.00"),
        )

    def test_place_purchase_order(self):
        order = place_purchase_order(
            self.order.id,
            self.organization,
        )

        self.assertEqual(order.status, PurchaseOrder.Status.ORDERED)

    def test_partial_stock_receiving(self):
        place_purchase_order(self.order.id, self.organization)

        order, item = receive_purchase_order_item(
            purchase_order_id=self.order.id,
            organization=self.organization,
            item_id=self.item.id,
            quantity=8,
        )

        self.assertEqual(item.quantity_received, 8)
        self.assertEqual(item.remaining_quantity, 12)
        self.assertEqual(
            order.status,
            PurchaseOrder.Status.PARTIALLY_RECEIVED,
        )

        inventory = Inventory.objects.get(product=self.product)
        self.assertEqual(inventory.quantity, 8)

    def test_full_stock_receiving(self):
        place_purchase_order(self.order.id, self.organization)

        order, item = receive_purchase_order_item(
            purchase_order_id=self.order.id,
            organization=self.organization,
            item_id=self.item.id,
            quantity=20,
        )

        self.assertEqual(item.quantity_received, 20)
        self.assertEqual(item.remaining_quantity, 0)
        self.assertEqual(order.status, PurchaseOrder.Status.RECEIVED)

        inventory = Inventory.objects.get(product=self.product)
        self.assertEqual(inventory.quantity, 20)

    def test_over_receiving_is_rejected(self):
        place_purchase_order(self.order.id, self.organization)

        with self.assertRaises(ValidationError):
            receive_purchase_order_item(
                purchase_order_id=self.order.id,
                organization=self.organization,
                item_id=self.item.id,
                quantity=21,
            )

        self.assertEqual(self.item.quantity_received, 0)
        self.assertFalse(Inventory.objects.filter(product=self.product).exists())

    def test_stock_movement_created_when_receiving(self):
        place_purchase_order(self.order.id, self.organization)

        receive_purchase_order_item(
            purchase_order_id=self.order.id,
            organization=self.organization,
            item_id=self.item.id,
            quantity=5,
        )

        movement = StockMovement.objects.get(product=self.product)

        self.assertEqual(
            movement.movement_type,
            StockMovement.MovementType.STOCK_IN,
        )
        self.assertEqual(movement.quantity, 5)

