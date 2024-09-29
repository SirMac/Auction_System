from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.addItem, name='addItem'),
    path('bid-item/<int:id>/', views.bidItem, name='bidItem'),
    path('read', views.readContact, name='readContact'),
    path('update/<int:id>/', views.updateContact, name='updateContact'),
    path('delete/<int:id>/', views.deleteContact, name='deleteContact'),
]