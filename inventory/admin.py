
from django.contrib import admin
from .models import Inventory, StockMovement


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'organization', 'quantity', 'updated_at')
    search_fields = ('product__name', 'product__sku')
    list_filter = ('organization',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'organization',
        'movement_type',
        'quantity',
        'created_at',
    )
    search_fields = ('product__name', 'product__sku')
    list_filter = ('movement_type', 'organization', 'created_at')

