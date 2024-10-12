from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.addItem, name='addItem'),
    path('lot/<int:id>/', views.bidItem, name='bidItem'),
    path('lot/time/<int:id>/', views.getBidClosingTime, name='getBidClosingTime'),
    path('lot/winner/<int:id>/', views.getWinner, name='getWinner'),
    path('select', views.getSelectHtml, name='getSelect'),
    path('notification', views.getNotification, name='notification'),
]