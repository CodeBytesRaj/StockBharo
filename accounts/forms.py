
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import User
from organizations.models import Organization, Membership


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150)
    business_name = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("email",)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["full_name"]

        if commit:
            user.save()

            organization = Organization.objects.create(
                name=self.cleaned_data["business_name"],
                owner=user
            )

            Membership.objects.create(
                organization=organization,
                user=user,
                role=Membership.Role.OWNER
            )

        return user

