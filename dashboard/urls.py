from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('sell/<int:stock_id>/', views.sell_stock, name='sell_stock'),
    path('<str:stock_symbol>/', views.stock, name='stock')
]