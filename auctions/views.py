from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.http import HttpResponse
from time import strftime
from .utils import addNewItem, getAllRecords, getAuctionByItemId
from .utils import addNewBid, getBidTimeDiffInSecTupple, resetTimeForItemNotBidded
from .utils import handleAuctionClosure, hasAuctionClosed, getNotificationCount
from .utils import getNotificationList, getRecordByPk, getBidWinner
from .models import Item, Bid, Category, SubCategory
import logging



# @login_required
def index(req):
    # items = getAllRecords(Item)
    # filteredItem = [item for item in items if getAuctionByItemId(item.id, 'status') == 'opened']
    try:
        filteredItems = Item.objects.filter(status='opened')
    except:
        logging.error('Index: items not found')
        return render(req, 'auctions/index.html')
    else:
        context = {'items': filteredItems}
        return render(req, 'auctions/index.html', context=context)
    


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




def getLiveBidDetail(req, id):
    try:
        auction = getAuctionByItemId(id)
        if not auction:
            return HttpResponse('')
        bids = Bid.objects.filter(auctionid=auction.id)
    except:
        return HttpResponse('')
    else:
        bidList = "<ul>"
        for bid in bids:
            bidList += f'<li>Competing Bid: ${bid.amount}<li>'
        bidList += '<ul>'
        winner = getBidWinner(id)
        if winner:
            bidList += f"<div id='bid-winner'>Winner: {winner}</div>"
        return HttpResponse(bidList)




def getSelectHtml(req):
    tableName = req.GET.get('target').lower()
    categoryId = req.GET.get('categoryid')
    models = {'category':Category, 'subcategory':SubCategory} 
    select = "<option value=''>---</option>"

    if not tableName:
        logging.error('getSelectHtml: request query string empty')
        return HttpResponse(select)
    
    model = models[tableName]

    if not model:
        logging.error(f'getSelectHtml: model not found for {tableName}')
        return HttpResponse(select)
    
    if categoryId:
        records = model.objects.filter(categoryid=categoryId)
    else:
        records = getAllRecords(model)

    if not records:
        logging.error(f'getSelectHtml: record not found for {tableName}')
        return HttpResponse(select)
    
    for record in records:
        select += f"<option value='{record.id}'>"
        select += record.name
        select += '</option>'

    return HttpResponse(select)





def getSoldItems(req):
    context = {'pageType':'soldItems'}
    try:
        filteredItems = Item.objects.filter(status='closed')
    except:
        logging.error('getSoldItems: items not found')
        return render(req, 'auctions/index.html', context=context)
    else:
        context['items'] = filteredItems
        return render(req, 'auctions/index.html', context=context)