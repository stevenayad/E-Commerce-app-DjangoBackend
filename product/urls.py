from django.urls import path
from . import views;
urlpatterns = [
    path('product/', views.get_all_product , name='product'),
    path('product/<int:pk>', views.get_product_by_id , name='get_by_id'),
    path('product/filter', views.get_product_by_filter , name='get_by_filter'),
    path('product/Pagination', views.get_all_product_by_Pagination , name='get_by_Pagination'),
    path('add/product/' , views.add_product , name='add_product'),
    path('update/product/<int:pk>', views.update_product , name='update_product'),
    path('delete/product/<int:pk>', views.delete_product , name='delete_product'),
    path('add/review/<int:pk>', views.add_review , name='add_review'),
    path('delete/review/<int:pk>', views.delete_review , name='delete_review'),
]