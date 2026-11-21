from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "organization",
        "supplier",
        "status",
        "order_date",
        "created_by",
    )

    list_filter = ("status", "organization", "order_date")

    search_fields = (
        "order_number",
        "supplier__name",
    )

    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_order",
        "product",
        "quantity_ordered",
        "quantity_received",
        "unit_cost",
    )
