from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.purchase_order_list,
        name="purchase_order_list"
    ),
    path(
        "create/",
        views.create_purchase_order_view,
        name="create_purchase_order"
    ),
    path(
        "<int:purchase_order_id>/",
        views.purchase_order_detail,
        name="purchase_order_detail"
    ),
    path(
        "<int:purchase_order_id>/add-item/",
        views.add_purchase_order_item,
        name="add_purchase_order_item"
    ),
    path(
        "<int:purchase_order_id>/place/",
        views.place_purchase_order_view,
        name="place_purchase_order"
    ),
    path(
        "<int:purchase_order_id>/items/<int:item_id>/receive/",
        views.receive_purchase_order_item_view,
        name="receive_purchase_order_item"
    ),
]