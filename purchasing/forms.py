from django import forms

from suppliers.models import Supplier
from products.models import Product
from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "order_number",
            "expected_date",
            "notes",
        ]

        widgets = {
            "supplier": forms.Select(attrs={
                "class": "form-select"
            }),
            "order_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter purchase order number"
            }),
            "expected_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Additional notes",
                "rows": 3
            }),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["supplier"].queryset = Supplier.objects.filter(
                organization=organization,
                is_active=True
            ).order_by("name")
        else:
            self.fields["supplier"].queryset = Supplier.objects.none()


class PurchaseOrderItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "product",
            "quantity_ordered",
            "unit_cost",
        ]

        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select"
            }),
            "quantity_ordered": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "placeholder": "Enter quantity"
            }),
            "unit_cost": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
                "placeholder": "Enter unit cost"
            }),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["product"].queryset = Product.objects.filter(
                organization=organization,
                is_active=True
            ).order_by("name")
        else:
            self.fields["product"].queryset = Product.objects.none()