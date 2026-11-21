
from django.db import models
from organizations.models import Organization


class Supplier(models.Model):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="suppliers"
    )

    name = models.CharField(max_length=255)

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=20)

    address = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
