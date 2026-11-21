from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Main pages
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Product management
    path('products/', include('products.urls')),
    path('inventory/', include('inventory.urls')),
    path('suppliers/', include('suppliers.urls')),
]



