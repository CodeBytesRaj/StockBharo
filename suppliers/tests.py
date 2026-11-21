
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from organizations.models import Organization, Membership
from suppliers.models import Supplier


User = get_user_model()


class SupplierTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="supplier_test",
            email="supplier@test.com",
            password="testpassword123"
        )

        self.organization = Organization.objects.create(
            name="Test Health Store",
            owner=self.user
        )

        Membership.objects.create(
            organization=self.organization,
            user=self.user,
            role=Membership.Role.OWNER
        )

        self.client.login(
            username="supplier_test",
            password="testpassword123"
        )

        self.supplier = Supplier.objects.create(
            organization=self.organization,
            name="Test Supplier",
            contact_person="Test Manager",
            email="test@supplier.com",
            phone="9999999999"
        )

    def test_supplier_list_page_loads(self):
        response = self.client.get(reverse("supplier_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Supplier")

    def test_add_supplier(self):
        response = self.client.post(
            reverse("add_supplier"),
            {
                "name": "New Supplier",
                "contact_person": "Rahul",
                "email": "rahul@example.com",
                "phone": "8888888888",
                "address": "Mathura",
                "notes": "Test supplier",
                "is_active": "on",
            }
        )

        self.assertRedirects(
            response,
            reverse("supplier_list")
        )

        self.assertTrue(
            Supplier.objects.filter(
                organization=self.organization,
                name="New Supplier"
            ).exists()
        )

    def test_edit_supplier(self):
        response = self.client.post(
            reverse(
                "edit_supplier",
                args=[self.supplier.id]
            ),
            {
                "name": "Updated Supplier",
                "contact_person": "Updated Manager",
                "email": "updated@example.com",
                "phone": "7777777777",
                "address": "Updated Address",
                "notes": "Updated notes",
                "is_active": "on",
            }
        )

        self.assertRedirects(
            response,
            reverse("supplier_list")
        )

        self.supplier.refresh_from_db()

        self.assertEqual(
            self.supplier.name,
            "Updated Supplier"
        )

    def test_deactivate_supplier(self):
        response = self.client.post(
            reverse(
                "deactivate_supplier",
                args=[self.supplier.id]
            )
        )

        self.assertRedirects(
            response,
            reverse("supplier_list")
        )

        self.supplier.refresh_from_db()

        self.assertFalse(self.supplier.is_active)

    def test_supplier_cannot_access_another_organization_supplier(self):
        another_user = User.objects.create_user(
            username="another_user",
            email="another@test.com",
            password="testpassword123"
        )

        another_organization = Organization.objects.create(
            name="Another Store",
            owner=another_user
        )

        another_supplier = Supplier.objects.create(
            organization=another_organization,
            name="Private Supplier",
            phone="6666666666"
        )

        response = self.client.get(
            reverse(
                "edit_supplier",
                args=[another_supplier.id]
            )
        )

        self.assertEqual(response.status_code, 404)
