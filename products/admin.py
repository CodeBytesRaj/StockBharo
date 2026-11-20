from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'created_at')
    search_fields = ('name', 'organization__name')
    list_filter = ('organization',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'organization',
        'category',
        'cost_price',
        'selling_price',
        'is_active',
    )

    search_fields = ('name', 'sku')
    list_filter = ('organization', 'category', 'is_active')

    ordering = ('name',)
