
from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier

        fields = [
            'name',
            'contact_person',
            'email',
            'phone',
            'address',
            'notes',
            'is_active',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier name'
            }),

            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact person'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter supplier address',
                'rows': 3
            }),

            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional notes',
                'rows': 3
            }),

            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
