
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from organizations.models import Membership
from .models import Product
from .forms import ProductForm


# ==========================================
# 1. PRODUCT LIST
# ==========================================

@login_required(login_url='login')
def product_list(request):

    membership = Membership.objects.filter(
        user=request.user
    ).select_related('organization').first()

    if not membership:
        return render(
            request,
            'products/product_list.html',
            {
                'products': [],
                'organization': None
            }
        )

    organization = membership.organization

    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).select_related('category').order_by('-created_at')

    context = {
        'products': products,
        'organization': organization,
    }

    return render(
        request,
        'products/product_list.html',
        context
    )


# ==========================================
# 2. ADD PRODUCT
# ==========================================

@login_required(login_url='login')
def add_product(request):

    membership = Membership.objects.filter(
        user=request.user
    ).select_related('organization').first()

    if not membership:
        messages.error(
            request,
            'You are not linked to any organization.'
        )
        return redirect('dashboard')

    organization = membership.organization

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            organization=organization
        )

        if form.is_valid():

            product = form.save(commit=False)
            product.organization = organization
            product.save()

            messages.success(
                request,
                'Product added successfully!'
            )

            return redirect('product_list')

    else:

        form = ProductForm(
            organization=organization
        )

    return render(
        request,
        'products/add_product.html',
        {
            'form': form,
            'organization': organization,
        }
    )


# ==========================================
# 3. EDIT PRODUCT
# ==========================================

@login_required(login_url='login')
def edit_product(request, product_id):

    membership = Membership.objects.filter(
        user=request.user
    ).select_related('organization').first()

    if not membership:
        messages.error(
            request,
            'You are not linked to any organization.'
        )
        return redirect('dashboard')

    organization = membership.organization

    product = get_object_or_404(
        Product,
        id=product_id,
        organization=organization
    )

    if request.method == 'POST':

        form = ProductForm(
            request.POST,
            instance=product,
            organization=organization
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Product updated successfully!'
            )

            return redirect('product_list')

    else:

        form = ProductForm(
            instance=product,
            organization=organization
        )

    return render(
        request,
        'products/edit_product.html',
        {
            'form': form,
            'product': product,
            'organization': organization,
        }
    )

@login_required(login_url='login')
def delete_product(request, product_id):

    membership = Membership.objects.filter(
        user=request.user
    ).select_related('organization').first()

    if not membership:
        messages.error(
            request,
            'You are not linked to any organization.'
        )
        return redirect('dashboard')

    organization = membership.organization

    product = get_object_or_404(
        Product,
        id=product_id,
        organization=organization
    )

    if request.method == 'POST':
        product.delete()

        messages.success(
            request,
            'Product deleted successfully!'
        )

        return redirect('product_list')

    return render(
        request,
        'products/delete_product.html',
        {
            'product': product,
            'organization': organization,
        }
    )

