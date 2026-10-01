from django.urls import path

from . import views

urlpatterns = [
    path("connect/", views.connect_page),
    path("link-token/", views.create_link_token),
    path("exchange/", views.exchange_public_token),
    path("holdings/", views.holdings),
]
