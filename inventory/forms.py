
from django import forms

from products.models import Product
from .models import StockMovement


class StockMovementForm(forms.Form):

    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    movement_type = forms.ChoiceField(
        choices=StockMovement.MovementType.choices,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter quantity"
        })
    )

    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Add a note (optional)",
            "rows": 3
        })
    )

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organization:
            self.fields["product"].queryset = Product.objects.filter(
                organization=organization,
                is_active=True
            ).order_by("name")

    def clean(self):
        cleaned_data = super().clean()

        movement_type = cleaned_data.get("movement_type")
        quantity = cleaned_data.get("quantity")

        if quantity is not None and movement_type:
            if movement_type in [
                StockMovement.MovementType.STOCK_IN,
                StockMovement.MovementType.STOCK_OUT,
            ] and quantity <= 0:
                self.add_error(
                    "quantity",
                    "Stock In and Stock Out quantities must be positive."
                )

            if (
                movement_type == StockMovement.MovementType.ADJUSTMENT
                and quantity == 0
            ):
                self.add_error(
                    "quantity",
                    "Adjustment quantity cannot be zero."
                )

        return cleaned_data

