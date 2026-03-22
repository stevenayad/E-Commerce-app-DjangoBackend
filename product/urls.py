from django.urls import path
from . import views;
urlpatterns = [
    path('product/', views.get_all_product , name='product'),
    path('product/<int:pk>', views.get_product_by_id , name='get_by_id'),
    path('product/filter', views.get_product_by_filter , name='get_by_filter'),
    path('product/Pagination', views.get_all_product_by_Pagination , name='get_by_Pagination'),
]