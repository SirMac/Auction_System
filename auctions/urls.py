from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.index, name='index'),
    path('create', views.createContact, name='createContact'),
    path('read', views.readContact, name='readContact'),
    path('update/<int:id>/', views.updateContact, name='updateContact'),
    path('delete/<int:id>/', views.deleteContact, name='deleteContact'),
    path('detail/<int:id>/', views.viewDetail, name='detailContact'),
]