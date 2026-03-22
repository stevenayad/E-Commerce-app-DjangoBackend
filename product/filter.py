import django_filters
from .models import Product
class ProductFilter(django_filters.FilterSet):
    #نفس القيمة بس مش حساس لحالة الحروف
    name = django_filters.CharFilter(lookup_expr='iexact')
    #بيبحث جوا النص
    keyword = django_filters.filters.CharFilter(field_name='name' ,lookup_expr='icontains')
    #أكبر من أو يساوي
    minprice=  django_filters.filters.NumberFilter(field_name='price' or  0, lookup_expr='gte')
    #أصغر من أو يساوي
    maxprice = django_filters.filters.NumberFilter(field_name='price' or  10000, lookup_expr='lte')
    class Meta:
        model = Product
        fields = ['price', 'brand' ,'keyword' , 'minprice' , 'maxprice']