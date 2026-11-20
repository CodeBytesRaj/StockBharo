from django.db import models
from organizations.models import Organization


class Category(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'name'],
                name='unique_category_per_organization'
            )
        ]

    def __str__(self):
        return f'{self.name} - {self.organization.name}'


class Product(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='products'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products'
    )

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    unit = models.CharField(max_length=30, default='piece')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'sku'],
                name='unique_sku_per_organization'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.sku})'
