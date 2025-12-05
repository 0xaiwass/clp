from django.urls import path
from .views import *
#-----------------------------------------------------------
app_name = 'products'
urlpatterns = [
    path("", ProductsListView.as_view(), name="products"),
    path('p/<str:category>/<slug:slug>/', ProductDetailView.as_view(), name="products_detail"),
    # path("<int:product_id>/add-comment/", add_comment, name="add_comment"),
]