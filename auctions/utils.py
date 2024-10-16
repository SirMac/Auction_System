from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from django.urls import reverse
from .auctionValidators import ValidateAuction, ValidateBid
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from time import strftime, gmtime
from datetime import datetime
from django.utils import timezone
from .models import Item, Bid, Auction, Notification
import logging


def addNewItem(req):
    name = req.POST.get('name')
    description = req.POST.get('description')
    categoryid = req.POST.get('categoryid')
    subcategoryid = req.POST.get('subcategoryid')
    minimumbid = req.POST.get('minimumbid')
    itemImage = req.FILES['image']
    
    validItem = ValidateAuction(req.POST)
    messages = validItem.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
            error(request=req, message=message)
        return redirect('auctions:addItem')

    fs = FileSystemStorage()
    itemName = fs.save(itemImage.name, itemImage)

    newItem = Item(
        name = name, 
        description = description, 
        categoryid = categoryid, 
        subcategoryid = subcategoryid, 
        minimumbid = minimumbid, 
        username = req.user.username,
        image = fs.url(itemName),
        status = 'opened'
    )
    newItem.save()
    success(request=req, message=f'Item "{name}" created successfully')
    addAuction(newItem.id)
    return redirect('auctions:index')



def addNewBid(req, id):
    amount = req.POST.get('amount')
    username = req.user.username
    auction = getAuctionByItemId(id)

    if not hasAuctionClosed(id):
        validBid = ValidateBid(req.POST)
        messages = validBid.errorMessages
        
        if messages:
            for message in messages:
                logging.error(message)
            return HttpResponse(message)

        newBid = Bid(
            auctionid = auction.id, 
            itemid = id, 
            username = username, 
            amount = amount
        )
        newBid.save()
        auction.auction1 = amount
        auction.save()
        logging.info(f'Bid for Item "{id}" with amount {amount} submitted for {username}')

    return HttpResponse('')



def addAuction(itemid):
    endate = getBidEndDateFromNow(timezone)
    newAuction = Auction(
        itemid = itemid, 
        endat = endate,
        status = 'opened'
    )
    newAuction.save()
    logging.info(f'Auction for Item "{itemid}" created successfully')





def toInt(str):
    try:
        num = int(str)
    except:
        return 0
    else:
        return num



def getAllRecords(model):
    try:
        record = model.objects.all()
    except (KeyError, model.DoesNotExist):
        return None
    else:
        return record



def getRecordByPk(model, id):
    try:
        record = model.objects.get(pk=id)
    except (KeyError, model.DoesNotExist):
        logging.error('getRecordByPk: model does not exist')
        return None
    else:
        return record



def getAuctionByItemId(id, field=''):
    try:
        auction = Auction.objects.get(itemid=id)
    except (KeyError, Auction.DoesNotExist):
        logging.error(f'Auction does not exist')
        return None
    else:
        if field:
            return getattr(auction, field)
        return auction



def getBidEndDateFromNow(timezone):
    maxMinutes = 5
    currentDate = timezone.now()
    endate = currentDate + timezone.timedelta(minutes=maxMinutes)
    return endate



def getHighestBid(auctionid):
    try:
        bid = Bid.objects.filter(auctionid=auctionid).order_by('-amount','createdat')
    except:
        return 0
    else:
        if len(bid) <= 0:
            return 0
        return bid[0]



def getBidTimeDiffInSecTupple(id):
    auction = ''
    try:
        auction = Auction.objects.get(itemid=id)
    except (KeyError, Auction.DoesNotExist):
        logging.error(f'Auction does not exist')
        return 0
    else:
        endAt = auction.endat
        currentTime = timezone.now()
        timeDiff = endAt - currentTime
        secondsTupple = gmtime(timeDiff.total_seconds())
        return secondsTupple




def hasBidTimeExpired(id):
    bidTimeTupple = getBidTimeDiffInSecTupple(id)
    if not bidTimeTupple:
        return True
    bidTimeSeconds = int(strftime('%M%S', bidTimeTupple))
    if bidTimeSeconds <= 0 or bidTimeSeconds > 500:
        return True
    return False



def hasItemBeenBidded(id):
    try:
        bids = Bid.objects.filter(itemid=id)
    except (KeyError, Bid.DoesNotExist):
        logging.error(f'Bid does not exist')
        return False
    else:
        if bids:
            return True
        return False
    

def hasAuctionClosed(itemid):
    item = getRecordByPk(Item, itemid)
    if item.status == 'closed':
        return True
    return False





def resetTimeForItemNotBidded(id):
    itemHasBids = hasItemBeenBidded(id)
    bidTimeExpired = hasBidTimeExpired(id)
    
    if bidTimeExpired and not itemHasBids:
        newEndDate = getBidEndDateFromNow(timezone)
        try:
            auction = Auction.objects.get(itemid=id)
        except:
            logging.error(f'resetTimeForItemNotBidded: Auction do not exit for item, {id}')
            return
        else:
            auction.endat = newEndDate
            auction.save()



def handleAuctionClosure(itemid):

    if hasAuctionClosed(itemid):
        return

    itemHasBids = hasItemBeenBidded(itemid)
    bidTimeExpired = hasBidTimeExpired(itemid)
    item = getRecordByPk(Item, itemid)
    auction = getAuctionByItemId(itemid)
    highestBid = getHighestBid(auction.id)
    
    if bidTimeExpired and itemHasBids and highestBid:
        newNotification = Notification(
            auctionid = auction.id,
            itemid = itemid,
            seller = item.username,
            winner = highestBid.username,
            bid = highestBid.amount,
            bidtime = highestBid.createdat
        )
        newNotification.save()

        auction.status = 'closed'
        item.status = 'closed'
        item.save()
        auction.save()




def getBidWinner(itemid):
    if not hasAuctionClosed(itemid):
        return None
    try:
        notification = Notification.objects.get(itemid=itemid)
    except KeyError as e:
        logging.error(f'getWinner: Error occured: {e}')
        return None
    else:
        return notification.winner




def getNotificationCount(user):
    try:
        sellerNotification = Notification.objects.filter(seller=user, status='pending')
        winnerNotification = Notification.objects.filter(winner=user, status='pending')
        notificationCount = len(sellerNotification) + len(winnerNotification)
    except:
        return ''
    else:
        return notificationCount
    



def getNotificationList(user):
    try:
        sellerNotification = Notification.objects.filter(seller=user)
        winnerNotification = Notification.objects.filter(winner=user)
    except:
        return ''
    else:
        setNotificationStatus(sellerNotification)
        setNotificationStatus(winnerNotification)
        notificationHtml = getNotificationHtml(
            sellerNotification, 
            {'title':'Seller Notification', 'type':'seller'}
        )
        notificationHtml += getNotificationHtml(
            winnerNotification, 
            {'title':'Winner Notification', 'type':'winner'}
        )
        if len(notificationHtml) == 0:
            return HttpResponse('Notification not found')
        return HttpResponse(notificationHtml)
    


def setNotificationStatus(notificationRecord):
    if not notificationRecord:
        return 
    for record in notificationRecord:
        record.status = 'viewed'
        record.save()




def getNotificationHtml(notificationList, options):
    title = options['title']
    type = options['type']
    if len(notificationList) == 0 or not title:
        return ''
    
    notificationHtml = f"<div class='notification-tbl-main'>"
    notificationHtml += "<table id='notification-table'>"
    notificationHtml += '<thead>'
    notificationHtml += '<tr>'
    notificationHtml += f'<th colspan=100>{title}</th>'
    notificationHtml += '</tr>'
    notificationHtml += '</thead>'
    notificationHtml += '<tbody>'
    for notification in notificationList:
        formatedDate = (notification.bidtime).strftime('%Y-%m-%d')
        item = getRecordByPk(Item, notification.itemid)
        if item:
            item = item.name
        else:
            item = '---'
        notificationHtml += "<tr class='notification-body-tr'>"
        if type == 'seller':
            notificationHtml += f"<td colspan=100>* <strong>{formatedDate}</strong>: Your item '{item}' on lot {notification.itemid} is won by <strong>{notification.winner}</strong>.</td>"
        else:
            notificationHtml += f"<td colspan=100>* <strong>{formatedDate}</strong>: You have won bid for item '{item}' on lot {notification.itemid}.</td>"
        notificationHtml += '</tr>'
    notificationHtml += '</tbody>'
    notificationHtml += '</table>'
    notificationHtml += '</div>'
    return notificationHtml


def getNotificationHtmlTbl(notificationList, title, type):

    if len(notificationList) == 0:
        return ''
    
    notificationHtml = f"<div class='notification-tbl-main'>"
    notificationHtml += f'<h3>{title}</h3>'
    notificationHtml += "<table id='notification-table'>"
    notificationHtml += '<thead>'
    notificationHtml += '<tr>'
    notificationHtml += '<th>Item Name</th>'
    if type == 'winner': 
        notificationHtml += '<th>Seller</th>'
    else: 
        notificationHtml += '<th>Winner</th>'
    notificationHtml += '<th>Bit Amount</th>'
    notificationHtml += '<th>Lot Number</th>'
    notificationHtml += '<th>Date</th>'
    notificationHtml += '</tr>'
    notificationHtml += '</thead>'
    notificationHtml += '<tbody>'
    for notification in notificationList:
        formatedDate = (notification.bidtime).strftime('%Y-%m-%d')
        item = getRecordByPk(Item, notification.itemid)
        if item:
            item = item.name
        else:
            item = '---'
        notificationHtml += '<tr>'
        notificationHtml += f'<td>{item}</td>'
        if type == 'winner':
            notificationHtml += f'<td>{notification.seller}</td>'
        else:
            notificationHtml += f'<td>{notification.winner}</td>'
        notificationHtml += f'<td>{notification.bid}</td>'
        notificationHtml += f'<td>{notification.itemid}</td>'
        notificationHtml += f'<td>{formatedDate}</td>'
        notificationHtml += '</tr>'
    notificationHtml += '</tbody>'
    notificationHtml += '</table>'
    notificationHtml += '</div>'
    return notificationHtml