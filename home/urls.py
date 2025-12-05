from django.urls import path
from home.views import *
from products.views import *
from blogs.views import *
#------------------------------------
app_name = 'home'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('p/<str:category>/<slug:slug>/', ProductDetailView.as_view(), name="products_detail"),
    path('b/<str:slug>/', BlogDetailView.as_view(), name='detail'),
    path('aboutus/', AboutUsView.as_view(), name='aboutus'),
]