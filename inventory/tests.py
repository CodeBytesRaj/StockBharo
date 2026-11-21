
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from organizations.models import Organization
from products.models import Category, Product
from inventory.models import Inventory, StockMovement
from inventory.services import record_stock_movement


User = get_user_model()


class InventoryServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="inventory_test",
            email="inventory@test.com",
            password="testpassword123"
        )

        self.organization = Organization.objects.create(
            name="Test Organization",
            owner=self.user
        )

        self.category = Category.objects.create(
            organization=self.organization,
            name="Electronics"
        )

        self.product = Product.objects.create(
            organization=self.organization,
            category=self.category,
            name="Test Mouse",
            sku="TEST-001",
            cost_price=100,
            selling_price=150
        )

    def test_stock_in(self):
        inventory, movement = record_stock_movement(
            self.organization,
            self.product,
            StockMovement.MovementType.STOCK_IN,
            50
        )

        self.assertEqual(inventory.quantity, 50)
        self.assertEqual(movement.quantity, 50)

    def test_stock_out(self):
        record_stock_movement(
            self.organization,
            self.product,
            StockMovement.MovementType.STOCK_IN,
            50
        )

        inventory, movement = record_stock_movement(
            self.organization,
            self.product,
            StockMovement.MovementType.STOCK_OUT,
            20
        )

        self.assertEqual(inventory.quantity, 30)
        self.assertEqual(movement.quantity, 20)

    def test_negative_stock_is_not_allowed(self):
        with self.assertRaises(ValidationError):
            record_stock_movement(
                self.organization,
                self.product,
                StockMovement.MovementType.STOCK_OUT,
                10
            )

        self.assertFalse(
            Inventory.objects.filter(product=self.product).exists()
        )

    def test_negative_adjustment(self):
        record_stock_movement(
            self.organization,
            self.product,
            StockMovement.MovementType.STOCK_IN,
            50
        )

        inventory, movement = record_stock_movement(
            self.organization,
            self.product,
            StockMovement.MovementType.ADJUSTMENT,
            -5
        )

        self.assertEqual(inventory.quantity, 45)
        self.assertEqual(movement.quantity, -5)

    def test_zero_adjustment_is_rejected(self):
        with self.assertRaises(ValidationError):
            record_stock_movement(
                self.organization,
                self.product,
                StockMovement.MovementType.ADJUSTMENT,
                0
            )

    def test_other_organization_cannot_change_product_stock(self):
        another_organization = Organization.objects.create(
            name="Another Organization",
            owner=self.user
        )

        with self.assertRaises(ValidationError):
            record_stock_movement(
                another_organization,
                self.product,
                StockMovement.MovementType.STOCK_IN,
                20
            )

        self.assertFalse(
            Inventory.objects.filter(product=self.product).exists()
        )
