from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.QuickbooksCreatePaymentView.as_view(), name='payment'),
    path("verify/", views.QuickbooksVerifyPaymentView.as_view(), name='verify'),
]