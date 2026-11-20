from django.db import models
from django.conf import settings


class Organization(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_organizations'
    )
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class Membership(models.Model):

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        MANAGER = 'MANAGER', 'Manager'
        STAFF = 'STAFF', 'Staff'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'user'],
                name='unique_organization_membership'
            )
        ]

    def __str__(self):
        return f'{self.user.email} - {self.organization.name} ({self.role})'