
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import PurchaseOrder, PurchaseOrderItem
from inventory.services import record_stock_movement


@transaction.atomic
def create_purchase_order(
    organization,
    supplier,
    order_number,
    created_by,
    items,
    expected_date=None,
    notes=""
):
    # Validate supplier.
    if supplier.organization_id != organization.id:
        raise ValidationError(
            "This supplier does not belong to your organization."
        )

    if not supplier.is_active:
        raise ValidationError("This supplier is inactive.")

    if not items:
        raise ValidationError(
            "A purchase order must contain at least one product."
        )

    # Validate all items before creating anything.
    for item in items:
        product = item["product"]
        quantity = item["quantity_ordered"]
        unit_cost = item["unit_cost"]

        if product.organization_id != organization.id:
            raise ValidationError(
                f"{product.name} does not belong to your organization."
            )

        if not product.is_active:
            raise ValidationError(f"{product.name} is inactive.")

        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValidationError(
                "Ordered quantity must be a positive whole number."
            )

        if unit_cost < 0:
            raise ValidationError("Unit cost cannot be negative.")

    # Create purchase order.
    purchase_order = PurchaseOrder.objects.create(
        organization=organization,
        supplier=supplier,
        order_number=order_number,
        created_by=created_by,
        expected_date=expected_date,
        notes=notes,
    )

    # Create purchase order items.
    for item in items:
        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=item["product"],
            quantity_ordered=item["quantity_ordered"],
            unit_cost=item["unit_cost"],
        )

    return purchase_order


@transaction.atomic
def place_purchase_order(purchase_order_id, organization):
    purchase_order = PurchaseOrder.objects.select_for_update().filter(
        id=purchase_order_id,
        organization=organization
    ).first()

    if not purchase_order:
        raise ValidationError("Purchase order not found.")

    if purchase_order.status != PurchaseOrder.Status.DRAFT:
        raise ValidationError(
            "Only draft purchase orders can be placed."
        )

    

    purchase_order.status = PurchaseOrder.Status.ORDERED
    purchase_order.save(update_fields=["status", "updated_at"])

    return purchase_order


@transaction.atomic
def receive_purchase_order_item(
    purchase_order_id,
    organization,
    item_id,
    quantity,
    received_by=None
):
    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        raise ValidationError(
            "Received quantity must be a positive whole number."
        )

    # Lock the order.
    purchase_order = PurchaseOrder.objects.select_for_update().filter(
        id=purchase_order_id,
        organization=organization
    ).first()

    if not purchase_order:
        raise ValidationError("Purchase order not found.")

    if purchase_order.status not in [
        PurchaseOrder.Status.ORDERED,
        PurchaseOrder.Status.PARTIALLY_RECEIVED,
    ]:
        raise ValidationError(
            "This purchase order cannot receive stock in its current status."
        )

    # Lock the order item.
    item = PurchaseOrderItem.objects.select_for_update().filter(
        id=item_id,
        purchase_order=purchase_order
    ).first()

    if not item:
        raise ValidationError("Purchase order item not found.")

    if quantity > item.remaining_quantity:
        raise ValidationError(
            f"Only {item.remaining_quantity} units remain to be received."
        )

    # Update received quantity.
    item.quantity_received += quantity
    item.save(update_fields=["quantity_received"])

    # Update inventory and create stock movement.
    record_stock_movement(
        organization=organization,
        product=item.product,
        movement_type="IN",
        quantity=quantity,
        note=(
            f"Received against purchase order "
            f"{purchase_order.order_number}"
        )
    )

    # Refresh all order items and determine order status.
    all_items_received = all(
        order_item.remaining_quantity == 0
        for order_item in purchase_order.items.all()
    )

    if all_items_received:
        purchase_order.status = PurchaseOrder.Status.RECEIVED
    else:
        purchase_order.status = PurchaseOrder.Status.PARTIALLY_RECEIVED

    purchase_order.save(update_fields=["status", "updated_at"])

    return purchase_order, item
