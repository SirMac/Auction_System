from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, success
from django.http import HttpResponse
from time import strftime
from .utils import addNewItem, getAllRecords, getAuctionByItemId
from .utils import addNewBid, getBidTimeDiffInSecTupple, resetTimeForItemNotBidded
from .utils import handleAuctionClosure, hasAuctionClosed, getNotificationCount
from .utils import getNotificationList, getRecordByPk
from .models import Item, Bid, Notification
import logging



# @login_required
def index(req):
    items = getAllRecords(Item)
    filteredItem = [item for item in items if getAuctionByItemId(item.id, 'status') == 'open']
    if items:
        context = {'items': filteredItem}
        return render(req, 'auctions/index.html', context=context)
    error(req, message='Currently, no items are available for auction.')
    return render(req, 'auctions/index.html')
    


@login_required
def addItem(req):
    if req.method == 'GET':
        return render(req, 'auctions/addItem.html')
    
    return addNewItem(req)


@login_required
def bidItem(req, id):
    
    if req.method == 'GET':
      bids = None
      auction = getAuctionByItemId(id)
      try:
          bids = Bid.objects.filter(auctionid=auction.id)
      except:
          logging.error(f'Item does not exist')
      item = getRecordByPk(Item, id)
      context = {'item': item, 'bids':bids}
      return render(req, 'auctions/bidItem.html', context=context)

    return addNewBid(req, id)




def getBidClosingTime(req, id):
    
    handleAuctionClosure(id)

    if hasAuctionClosed(id):
        return HttpResponse('auction closed')
    
    resetTimeForItemNotBidded(id)

    bidTimeTupple = getBidTimeDiffInSecTupple(id)
    timeDiff = strftime('%M:%S', bidTimeTupple)
    return HttpResponse(timeDiff)
    


def getNotification(req):
    user = req.user.username
    if not user:
        logging.warning('User not logged in')
        return HttpResponse('')
    
    notificationType = req.GET.get('type')
    notificationType = notificationType.lower()

    if notificationType == 'count':
        notificationCount = getNotificationCount(user)
        return HttpResponse(notificationCount)
    
    notificationList = getNotificationList(user)
    return HttpResponse(notificationList)




def getWinner(req, id):
    if not hasAuctionClosed(id):
        return HttpResponse('')
    try:
        notification = Notification.objects.get(itemid=id)
    except:
        logging.error('getWinner: Error occured')
        return HttpResponse('')
    else:
        return HttpResponse(f'Winner: {notification.winner}')