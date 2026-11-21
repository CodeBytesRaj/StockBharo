
from django.urls import path
from . import views

urlpatterns = [
    path("", views.inventory_dashboard, name="inventory_dashboard"),
    path("movement/", views.stock_movement, name="stock_movement"),
]
