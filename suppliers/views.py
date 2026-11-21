
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from organizations.models import Membership
from .models import Supplier
from .forms import SupplierForm


def get_user_organization(user):
    membership = Membership.objects.filter(
        user=user
    ).select_related('organization').first()

    return membership.organization if membership else None


@login_required(login_url='login')
def supplier_list(request):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, 'You are not linked to any organization.')
        return redirect('dashboard')

    suppliers = Supplier.objects.filter(
        organization=organization
    ).order_by('-created_at')

    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers,
        'organization': organization,
    })


@login_required(login_url='login')
def add_supplier(request):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, 'You are not linked to any organization.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SupplierForm(request.POST)

        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.organization = organization
            supplier.save()

            messages.success(request, 'Supplier added successfully!')
            return redirect('supplier_list')

    else:
        form = SupplierForm()

    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'organization': organization,
        'page_title': 'Add Supplier',
    })


@login_required(login_url='login')
def edit_supplier(request, supplier_id):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, 'You are not linked to any organization.')
        return redirect('dashboard')

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id,
        organization=organization
    )

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('supplier_list')

    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'organization': organization,
        'supplier': supplier,
        'page_title': 'Edit Supplier',
    })


@login_required(login_url='login')
def deactivate_supplier(request, supplier_id):
    organization = get_user_organization(request.user)

    if not organization:
        messages.error(request, 'You are not linked to any organization.')
        return redirect('dashboard')

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id,
        organization=organization
    )

    if request.method == 'POST':
        supplier.is_active = False
        supplier.save(update_fields=['is_active', 'updated_at'])

        messages.success(request, 'Supplier deactivated successfully!')
        return redirect('supplier_list')

    return render(request, 'suppliers/deactivate_supplier.html', {
        'supplier': supplier,
        'organization': organization,
    })

