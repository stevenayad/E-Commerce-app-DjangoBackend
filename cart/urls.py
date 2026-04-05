from django.urls import path

from . import views

urlpatterns = [
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_get, name='cart_get'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
]
