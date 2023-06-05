from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:id>', views.stock, name='stock')
]