from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.index, name='index'),
    path('auction', views.addAuction, name='addAuction'),
    path('auction/closed-auction', views.getClosedAuction, name='closedAuction'),
    path('auction/<int:id>/edit', views.editAuction, name='editAuction'),
    path('auction/<int:id>/', views.auctionIndex, name='auctionIndex'),
    path('auction/<int:id>/participant/add', views.addParticipant, name='addParticipant'),
    path('auction/<int:id>/participant/list', views.listParticipants, name='listParticipant'),
    path('auction/<int:aid>/participant/<int:pid>/edit', views.editParticipant, name='editParticipant'),
    path('auction/<int:aid>/participant/<int:pid>/delete', views.deleteParticipant, name='deleteParticipant'),
    path('auction/<int:id>/item/add', views.addItem, name='addItem'),
    path('auction/<int:aid>/item/<int:itemid>/bid', views.bidItem, name='bidItem'),
    path('auction/<int:aid>/item/<int:itemid>/bid-detail', views.getBidDetail, name='getBidDetail'),
    path('auction/<int:aid>/sold-items', views.getSoldItems, name='getSoldItems'),
    path('lot/time/<int:id>/', views.getBidClosingTime, name='getBidClosingTime'),
    path('select', views.getSelectHtml, name='getSelect'),
    path('notification', views.getNotification, name='notification'),
]