from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response;
from .models import Product , Review
from .serializers import ProductSerializers
from .filter import ProductFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.status import HTTP_403_FORBIDDEN 
from rest_framework import status
from django.db.models import Avg
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
     paginate.page_size = 2
     queryset = paginate.paginate_queryset(queryset=product,request=request)
     serializer = ProductSerializers(queryset,many=True)
     return Response({"products":serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
     data = request.data
     serializer = ProductSerializers(data=data)

     if serializer.is_valid():
           prodcut = Product.objects.create(**data,user=request.user)
           ser = ProductSerializers(prodcut,many=False)
           return Response({"product":ser.data})
     else:
           return Response({"product":serializer.errors})  
     
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request,pk):
     
     product = Product.objects.get(id=pk)

     if product.user != request.user:
          return Response({"error":"Sorry Can not Update"}, status=status.HTTP_403_FORBIDDEN)  
      
     
     product.name = request.data['name']
     product.price = request.data['price']
     product.description = request.data['description']
     product.category = request.data['category']
     product.stock = request.data['stock']
     product.ratings = request.data['ratings']
      
     product.save()
     serializer = ProductSerializers(product,many=False)
     return Response({"product":serializer.data})
      

   
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request,pk):
     product = Product.objects.get(id=pk)
      
     if product.user != request.user:
          return Response({"error":"Sorry Can not Update"}, status=status.HTTP_403_FORBIDDEN)  
     
     product.delete()
     return Response({"Message":"Product Deltete Successfully"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request,pk):
     product = Product.objects.get(id=pk)
     user = request.user
     data =request.data
     review = product.reviews.filter(user=user)

     if data['ratings'] <= 0 or data['ratings']>5:
       return  Response({"Message":"Select Rating from 1 to 5 "})
     
     elif review.exists():
          newreview={'ratings':data['ratings'], 'comment':data['comment']}
          review.update(**newreview)

          rating = product.reviews.aggregate(avg_rating =Avg('ratings'))
          product.ratings = rating['avg_rating']
          product.save()
          return Response({"Message":"Updated Reviw Successfully"})

     else:
          Review.objects.create(
               user=user,
               ratings=data['ratings'],
               product= product,
               comment=data['comment']
          )
          rating = product.reviews.aggregate(avg_rating =Avg('ratings'))
          product.ratings = rating['avg_rating']
          product.save()
          return Response({"Message":"Product Reviw Successfully"})
     
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user
    product = get_object_or_404(Product, id=pk)
    review = product.reviews.filter(user=user)

    if review.exists():
        review.delete()

        rating = product.reviews.aggregate(avg_ratings=Avg('ratings'))

        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0

        product.ratings = rating['avg_ratings']
        product.save()

        return Response({'details': 'Product review deleted'})
    else:
        return Response(
            {'error': 'Review not found'},
            status=status.HTTP_404_NOT_FOUND
        )