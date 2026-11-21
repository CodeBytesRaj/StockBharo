
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

from organizations.models import Organization
from suppliers.models import Supplier
from products.models import Product


class PurchaseOrder(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ORDERED = "ORDERED", "Ordered"
        PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED", "Partially Received"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="purchase_orders"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_orders"
    )

    order_number = models.CharField(max_length=50)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )

    order_date = models.DateField(auto_now_add=True)
    expected_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_purchase_orders"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "order_number"],
                name="unique_purchase_order_number_per_org"
            )
        ]

    @property
    def total_amount(self):
        return sum(
            item.line_total for item in self.items.all()
        )

    def __str__(self):
        return self.order_number


class PurchaseOrderItem(models.Model):

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_order_items"
    )

    quantity_ordered = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    quantity_received = models.PositiveIntegerField(default=0)

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    quantity_received__lte=models.F("quantity_ordered")
                ),
                name="received_qty_not_more_than_ordered"
            )
        ]

    @property
    def line_total(self):
        return self.quantity_ordered * self.unit_cost

    @property
    def remaining_quantity(self):
        return self.quantity_ordered - self.quantity_received

    def __str__(self):
        return f"{self.product.name} - {self.quantity_ordered}"
