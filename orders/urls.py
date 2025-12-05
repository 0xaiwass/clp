from django.urls import path
from .views import *

app_name = 'orders'
urlpatterns = [
    path('', OrdersListView.as_view(), name='order_list'),
    path("create/", CreateOrderView.as_view(), name="order_create"),
    path('<uuid:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('<uuid:order_id>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path("remove/<uuid:item_id>/", RemoveOrderItemView.as_view(), name="remove_item"),
]