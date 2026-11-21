
from django import forms

from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product

        fields = [
            'name',
            'sku',
            'category',
            'description',
            'cost_price',
            'selling_price',
            'unit',
            'is_active',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique SKU',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product description',
                'rows': 3,
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter cost price',
                'step': '0.01',
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter selling price',
                'step': '0.01',
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. piece, box, kg',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)

        if organization is not None:
            self.fields['category'].queryset = Category.objects.filter(
                organization=organization
            ).order_by('name')
        else:
            self.fields['category'].queryset = Category.objects.none()

