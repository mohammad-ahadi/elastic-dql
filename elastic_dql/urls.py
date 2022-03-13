from django.urls import path

from .views import MappingsAPIView, SuggestionsAPIView

urlpatterns = [
    path('mappings', MappingsAPIView.as_view(), name='mappings_api'),
    path('suggestions/<str:field>', SuggestionsAPIView.as_view(), name='suggestions_api'),
]


def get_urls():
    return urlpatterns
