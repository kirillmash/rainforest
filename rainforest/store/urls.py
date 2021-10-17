from django.urls import path
from .views import ProductsAPIVIew, OrdersAPIView, ConsolidatedReportAPIView

urlpatterns = [
    path('products/', ProductsAPIVIew.as_view()),
    path('order/create/', OrdersAPIView.as_view()),
    path('report/', ConsolidatedReportAPIView.as_view())
]
