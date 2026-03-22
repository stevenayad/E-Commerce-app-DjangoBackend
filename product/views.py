from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response;
from .models import Product
from .serializers import ProductSerializers
from .filter import ProductFilter
from rest_framework.pagination import PageNumberPagination
@api_view(['GET'])
def get_all_product(request):
     product = Product.objects.all()
     serializer = ProductSerializers(product,many=True)
     return Response({"products":serializer.data})

@api_view(['GET'])

def get_product_by_id(request,pk):
     #product = get_object_or_404(Product,id=pk)
     product =Product.objects.get(id=pk)
     serializer = ProductSerializers(product,many=False)
     return Response({"product":serializer.data})
@api_view(['GET'])
def get_product_by_filter(request):
     #request.GET => دي بتجيب الـ query parameters من الـ URL
     filter = ProductFilter(data=request.GET ,queryset=Product.objects.all().order_by('id') ) 
     #filter.qs=>يعني المنتجات اللي طلعت من الفلتر بس
     serializer = ProductSerializers(filter.qs,many=True)
     return Response({"products":serializer.data})

@api_view(['GET'])
def get_all_product_by_Pagination(request):
     product = Product.objects.all()
     paginate = PageNumberPagination()
     paginate.page_size = 1
     queryset = paginate.paginate_queryset(queryset=product,request=request)
     serializer = ProductSerializers(queryset,many=True)
     return Response({"products":serializer.data})
