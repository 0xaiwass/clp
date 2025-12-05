from django.urls import path
from .views import *

app_name = 'blogs'
urlpatterns = [
    path('', BlogsView.as_view(), name='blogs'),
    path('b/<str:slug>/', BlogDetailView.as_view(), name='detail'),
    path('<str:slug>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('tag/<slug:slug>/', TagView.as_view(), name='tag'),
]
