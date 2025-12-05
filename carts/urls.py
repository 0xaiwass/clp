from django.urls import path
from .views import *

app_name = "carts"

urlpatterns = [
    path("add/", CartView.as_view(), name="add_to_cart"),
    path("items/", CartItemsView.as_view(), name="cart_items"),
    path('delete/<int:item_id>/', CartItemDeleteView.as_view(), name='cart_item_delete'),
]