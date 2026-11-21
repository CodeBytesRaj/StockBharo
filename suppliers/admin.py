
from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'organization',
        'contact_person',
        'phone',
        'email',
        'is_active',
        'created_at',
    )

    search_fields = (
        'name',
        'contact_person',
        'phone',
        'email',
    )

    list_filter = (
        'organization',
        'is_active',
    )

