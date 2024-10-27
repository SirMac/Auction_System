from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.index, name='index'),
    path('auction/<int:id>/', views.auctionIndex, name='auctionIndex'),
    path('auction', views.addAuction, name='addAuction'),
    path('auction/<int:id>/participant', views.addParticipant, name='addParticipant'),
    path('auction/<int:id>/participants/list', views.listParticipants, name='listParticipant'),
    path('item', views.addItem, name='addItem'),
    path('lot/<int:id>/', views.bidItem, name='bidItem'),
    path('lot/time/<int:id>/', views.getBidClosingTime, name='getBidClosingTime'),
    path('lot/live-bid/<int:id>/', views.getLiveBidDetail, name='getLiveBid'),
    path('sold-items', views.getSoldItems, name='getSoldItems'),
    path('select', views.getSelectHtml, name='getSelect'),
    path('notification', views.getNotification, name='notification'),
]