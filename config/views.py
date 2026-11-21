
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import RegisterForm


# Public homepage
def home(request):
    return render(request, 'home.html')


# User login
def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


# User registration
def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created successfully. Please log in.'
            )
            return redirect('login')

    else:
        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


# User logout
def logout_page(request):
    logout(request)
    return redirect('login')


# Protected dashboard
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

