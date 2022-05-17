from django_filters import CharFilter, FilterSet, NumberFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    genre = CharFilter(
        field_name='genre__slug', lookup_expr='icontains')
    category = CharFilter(
        field_name='category__slug', lookup_expr='icontains')
    year = NumberFilter()
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
