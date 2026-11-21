from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from organizations.models import Membership
from .models import PurchaseOrder
from .forms import PurchaseOrderForm, PurchaseOrderItemForm
from .services import (
    create_purchase_order,
    place_purchase_order,
    receive_purchase_order_item,
)


def get_user_organization(user):
    membership = Membership.objects.filter(
        user=user
    ).select_related("organization").first()

    return membership.organization if membership else None


@login_required(login_url="login")
def purchase_order_list(request):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    purchase_orders = PurchaseOrder.objects.filter(
        organization=organization
    ).select_related("supplier", "created_by")

    return render(request, "purchasing/purchase_order_list.html", {
        "purchase_orders": purchase_orders,
        "organization": organization,
    })


@login_required(login_url="login")
def create_purchase_order_view(request):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    if request.method == "POST":
        form = PurchaseOrderForm(
            request.POST,
            organization=organization
        )

        if form.is_valid():
            try:
                purchase_order = create_purchase_order(
                    organization=organization,
                    supplier=form.cleaned_data["supplier"],
                    order_number=form.cleaned_data["order_number"],
                    created_by=request.user,
                    items=[],
                    expected_date=form.cleaned_data["expected_date"],
                    notes=form.cleaned_data["notes"],
                )
            except ValidationError as error:
                messages.error(request, error.messages[0])
            else:
                messages.success(
                    request,
                    "Purchase order created successfully. Add products next."
                )
                return redirect(
                    "purchase_order_detail",
                    purchase_order_id=purchase_order.id
                )
    else:
        form = PurchaseOrderForm(organization=organization)

    return render(request, "purchasing/purchase_order_form.html", {
        "form": form,
        "organization": organization,
        "page_title": "Create Purchase Order",
    })


@login_required(login_url="login")
def purchase_order_detail(request, purchase_order_id):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    purchase_order = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "created_by"),
        id=purchase_order_id,
        organization=organization,
    )

    items = purchase_order.items.select_related("product").all()

    item_form = PurchaseOrderItemForm(organization=organization)

    return render(request, "purchasing/purchase_order_detail.html", {
        "purchase_order": purchase_order,
        "items": items,
        "item_form": item_form,
        "organization": organization,
    })


@login_required(login_url="login")
def add_purchase_order_item(request, purchase_order_id):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    purchase_order = get_object_or_404(
        PurchaseOrder,
        id=purchase_order_id,
        organization=organization,
    )

    if purchase_order.status != PurchaseOrder.Status.DRAFT:
        messages.error(request, "Products can only be added to draft orders.")
        return redirect(
            "purchase_order_detail",
            purchase_order_id=purchase_order.id
        )

    if request.method == "POST":
        form = PurchaseOrderItemForm(
            request.POST,
            organization=organization
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.purchase_order = purchase_order

            if purchase_order.items.filter(product=item.product).exists():
                messages.error(
                    request,
                    "This product is already in the purchase order."
                )
            else:
                item.save()
                messages.success(request, "Product added to purchase order.")
    else:
        messages.error(request, "Invalid request.")

    return redirect(
        "purchase_order_detail",
        purchase_order_id=purchase_order.id
    )


@login_required(login_url="login")
def place_purchase_order_view(request, purchase_order_id):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    if request.method == "POST":
        try:
            place_purchase_order(purchase_order_id, organization)
            messages.success(request, "Purchase order placed successfully.")
        except ValidationError as error:
            messages.error(request, error.messages[0])

    return redirect("purchase_order_detail", purchase_order_id=purchase_order_id)


@login_required(login_url="login")
def receive_purchase_order_item_view(request, purchase_order_id, item_id):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, "You are not linked to any organization.")
        return redirect("dashboard")

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", ""))
            receive_purchase_order_item(
                purchase_order_id=purchase_order_id,
                organization=organization,
                item_id=item_id,
                quantity=quantity,
                received_by=request.user,
            )
            messages.success(request, "Stock received and inventory updated.")
        except (ValueError, ValidationError) as error:
            if isinstance(error, ValidationError):
                message = error.messages[0]
            else:
                message = "Enter a valid whole-number quantity."

            messages.error(request, message)

    return redirect("purchase_order_detail", purchase_order_id=purchase_order_id)