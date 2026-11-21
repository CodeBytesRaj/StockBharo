
from django.core.exceptions import ValidationError
from django.db import transaction

from organizations.models import Organization
from products.models import Product
from .models import Inventory, StockMovement


@transaction.atomic
def record_stock_movement(
    organization,
    product,
    movement_type,
    quantity,
    note=""
):
    # Ensure the product belongs to this organization.
    if product.organization_id != organization.id:
        raise ValidationError(
            "This product does not belong to your organization."
        )

    # Validate movement type and quantity.
    if movement_type not in StockMovement.MovementType.values:
        raise ValidationError("Invalid stock movement type.")

    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise ValidationError("Quantity must be a whole number.")

    if movement_type in [
        StockMovement.MovementType.STOCK_IN,
        StockMovement.MovementType.STOCK_OUT,
    ] and quantity <= 0:
        raise ValidationError(
            "Stock In and Stock Out quantities must be positive."
        )

    if movement_type == StockMovement.MovementType.ADJUSTMENT and quantity == 0:
        raise ValidationError(
            "Adjustment quantity cannot be zero."
        )

    # Get or create the inventory record.
    inventory, created = Inventory.objects.get_or_create(
        product=product,
        defaults={
            "organization": organization,
            "quantity": 0,
        }
    )

    if inventory.organization_id != organization.id:
        raise ValidationError(
            "Inventory organization does not match."
        )

    # Lock the inventory row before changing its quantity.
    inventory = Inventory.objects.select_for_update().get(
        pk=inventory.pk
    )

    # Calculate the new stock quantity.
    if movement_type == StockMovement.MovementType.STOCK_IN:
        new_quantity = inventory.quantity + quantity

    elif movement_type == StockMovement.MovementType.STOCK_OUT:
        new_quantity = inventory.quantity - quantity

    else:
        # Adjustment quantity can be positive or negative.
        new_quantity = inventory.quantity + quantity

    if new_quantity < 0:
        raise ValidationError(
            "Insufficient stock. Available quantity: "
            f"{inventory.quantity}"
        )

    # Update inventory.
    inventory.quantity = new_quantity
    inventory.save(update_fields=["quantity", "updated_at"])

    # Record the movement history.
    movement = StockMovement.objects.create(
        organization=organization,
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
    )

    return inventory, movement
