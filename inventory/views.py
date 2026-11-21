
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from organizations.models import Membership
from products.models import Product
from .models import Inventory, StockMovement
from .forms import StockMovementForm
from .services import record_stock_movement


@login_required(login_url="login")
def inventory_dashboard(request):
    membership = Membership.objects.filter(
        user=request.user
    ).select_related("organization").first()

    if not membership:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    organization = membership.organization

    inventories = Inventory.objects.filter(
        organization=organization
    ).select_related("product", "product__category").order_by(
        "product__name"
    )

    recent_movements = StockMovement.objects.filter(
        organization=organization
    ).select_related("product").order_by("-created_at")[:10]

    total_products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).count()

    context = {
        "organization": organization,
        "inventories": inventories,
        "recent_movements": recent_movements,
        "total_products": total_products,
    }

    return render(request, "inventory/inventory_dashboard.html", context)


@login_required(login_url="login")
def stock_movement(request):
    membership = Membership.objects.filter(
        user=request.user
    ).select_related("organization").first()

    if not membership:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    organization = membership.organization

    if request.method == "POST":
        form = StockMovementForm(
            request.POST,
            organization=organization
        )

        if form.is_valid():
            try:
                inventory, movement = record_stock_movement(
                    organization=organization,
                    product=form.cleaned_data["product"],
                    movement_type=form.cleaned_data["movement_type"],
                    quantity=form.cleaned_data["quantity"],
                    note=form.cleaned_data["note"],
                )

                messages.success(
                    request,
                    f"Stock updated successfully. "
                    f"Current quantity: {inventory.quantity}"
                )

                return redirect("inventory_dashboard")

            except ValidationError as error:
                form.add_error(None, error)

    else:
        form = StockMovementForm(organization=organization)

    return render(request, "inventory/stock_movement.html", {
        "form": form,
        "organization": organization,
    })

