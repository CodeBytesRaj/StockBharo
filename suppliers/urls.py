
from django.urls import path
from . import views


urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('add/', views.add_supplier, name='add_supplier'),
    path('edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path(
        'deactivate/<int:supplier_id>/',
        views.deactivate_supplier,
        name='deactivate_supplier'
    ),
]
