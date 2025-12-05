from django.urls import path
from .views import *
#------------------------------------
app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/<uuid:public_id>/', DashboardView.as_view(), name='dashboard'),

    path("addresses/", ProfileAddressView.as_view(), name="profile_address"),
    path("addresses/add/", AddAddressView.as_view(), name="add_address"),
    path("addresses/<int:pk>/edit/", UpdateAddressView.as_view(), name="address_update"),
    path("addresses/<int:pk>/delete/", DeleteAddressView.as_view(), name="address_delete"),

    path('wishlist/', ProfileWishlistView.as_view(), name='wishlist'),
    path('resetpassword/', ResetPasswordView.as_view(), name='resetpassword'),
    path('newpassword/', NewPasswordView.as_view(), name='newpassword'),
]