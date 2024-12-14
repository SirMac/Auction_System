from django.shortcuts import redirect
from django.contrib.messages import error, success
from .auctionValidators import ValidateAddAuction, ValidateBid, ValidateAddParticipant
from .auctionValidators import ValidateEditAuction, ValidateAddItem
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from time import strftime, gmtime
from django.utils import timezone
from .models import Item, Bid, Auction, Notification, Participant
from django.contrib.auth.models import User
import logging




def addNewAuction(req):
    name = req.POST.get('name')
    description = req.POST.get('description')
    maxparticipant = req.POST.get('maxparticipant')

    validAuction = ValidateAddAuction(req.POST)
    messages = validAuction.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
        error(request=req, message=message)
        return redirect('auctions:addAuction')


    newAuction = Auction(
        name = name,
        description = description, 
        maxparticipant = maxparticipant,
        username = req.user.username,
        status = 'opened'
    )
    newAuction.save()
    logging.info(f'Auction "{newAuction.id}" created successfully')
    success(request=req, message=f'New auction created successfully')
    return redirect('auctions:index')



def doEditAuction(req, id):
    name = req.POST.get('name')
    description = req.POST.get('description')
    maxparticipant = req.POST.get('maxparticipant')
    status = req.POST.get('status')

    auctionValidation = ValidateEditAuction(req, id)
    messages = auctionValidation.errorMessages
    if messages:
        for message in messages:
            logging.error(message)
        error(request=req, message=message)
        return redirect('auctions:editAuction', id=id)

    try:
        auction = Auction.objects.get(pk=id)
    except:
        logging.error('doEditAuction: auction not found')
        return redirect('auctions:editAuction', id=id)
    else:
        auction.name = name
        auction.description = description
        auction.maxparticipant = maxparticipant
        auction.status = status
        auction.save()

        success(request=req, message='Auction updated successfully')
        return redirect('auctions:auctionIndex', id=id)




def addNewParticipant(req, id):
    userid = req.POST.get('username')
    status = req.POST.get('status')
    username = getRecordByPk(User, userid)

    if not username:
        logging.error('addNewParticipant: Username not found')
        return HttpResponse('Username not found')
    
    validParticipant = ValidateAddParticipant(req, id)
    messages = validParticipant.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
        return HttpResponse(f'<div class="error">{message}</div>')

    newParticipant = Participant(
        auctionid = id,
        userid = userid,
        username = username,
        status = status
    )
    newParticipant.save()
    logging.info(f'Participant "{newParticipant.id}" created successfully')
    return HttpResponse(f"New participant '{username}' added successfully")


def doEditparticipant(req, aid, pid):
    status = req.POST.get('status')
    try:
        participant = Participant.objects.get(pk=pid)
    except:
        logging.error('doEditparticipant: Participant not found')
        error(request=req, message='An error occured. Try again.')
        return redirect('auctions:editParticipant', aid=aid ,pid=pid)
    else:
        participant.status = status
        participant.save()
        success(request=req, message=f'Participant, {participant.username} updated successfully.')
        return redirect('auctions:listParticipant', id=aid)




def addNewItem(req, id):
    name = req.POST.get('name')
    description = req.POST.get('description')
    categoryid = req.POST.get('categoryid')
    subcategoryid = req.POST.get('subcategoryid')
    minimumbid = req.POST.get('minimumbid')
    itemImage = req.FILES['image']
    
    validItem = ValidateAddItem(req, id)
    messages = validItem.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
        error(request=req, message=message)
        return redirect('auctions:addItem', id=id)

    endate = getBidEndDateFromNow(timezone)

    fs = FileSystemStorage()
    itemName = fs.save(itemImage.name, itemImage)

    newItem = Item(
        auctionid = id,
        name = name, 
        description = description, 
        categoryid = categoryid, 
        subcategoryid = subcategoryid, 
        minimumbid = minimumbid, 
        username = req.user.username,
        image = fs.url(itemName),
        status = 'opened',
        endat = endate
    )
    newItem.save()
    success(request=req, message=f'Item "{name}" successfully added to auction "{id}"')
    return redirect('auctions:auctionIndex', id=id)




def doEditItem(req, aid, itemid):
    name = req.POST.get('name')
    description = req.POST.get('description')
    minimumbid = req.POST.get('minimumbid')
    try:
        item = Item.objects.get(pk=itemid)
    except:
        logging.error('doEditItem: Item not found')
        error(request=req, message='Item not found.')
        return redirect('auctions:auctionIndex', id=aid)
    else:
        if item.status.lower() == 'closed':
            error(request=req, message=f'Bidding on Item "{item.name}" on Lot "{item.id}" closed.')
            return redirect('auctions:auctionIndex', id=aid)    
        
        item.name = name
        item.description = description
        item.minimumbid = minimumbid
        item.save()
        success(request=req, message=f'Item, {item.name} updated successfully.')
        return redirect('auctions:auctionIndex', id=aid)





def addNewBid(req, aid, itemid):
    amount = req.POST.get('amount')
    username = req.user.username
    auction = getRecordByPk(Auction, aid)

    if hasAuctionClosed(aid):
        return HttpResponse('Auction has closed')
    
    if hasBiddingClosed(itemid):
        return HttpResponse(f'Bidding for Item on Lot {itemid} has closed')

    highestBidAmt = getHighestBidAmt(itemid)
    validBid = ValidateBid(req, aid, highestBidAmt)
    messages = validBid.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
        return HttpResponse(message)

    newBid = Bid(
        auctionid = auction.id, 
        itemid = itemid, 
        username = username, 
        amount = amount
    )
    newBid.save()
    logging.info(f'Bid for Item "{itemid}" with amount {amount} submitted for {username}')

    return HttpResponse('')




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
    item = getRecordByPk(Item, id)

    if not item:
        return None
    
    auction = getRecordByPk(Auction, item.auctionid)

    if not auction:
        return None
    
    if field:
        return getattr(auction, field)
    
    return auction



def getBidEndDateFromNow(timezone):
    maxMinutes = 5
    currentDate = timezone.now()
    endate = currentDate + timezone.timedelta(minutes=maxMinutes)
    return endate



def getHighestBid(itemid):
    try:
        bid = Bid.objects.filter(itemid=itemid).order_by('-amount','createdat')
    except:
        return None
    else:
        if len(bid) <= 0:
            return None
        return bid[0]


def getHighestBidAmt(itemid):
    highestBid = getHighestBid(itemid)
    highestBidAmt = 0
    if highestBid:
        highestBidAmt = highestBid.amount
    return highestBidAmt


def getBidTimeDiffInSecTupple(id):
    item = getRecordByPk(Item, id)
    
    if not item:
        logging.error(f'Item does not exist')
        return 0
    
    endAt = item.endat
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
    

def hasAuctionClosed(auctionid):
    auction = getRecordByPk(Auction, auctionid)
    if auction and auction.status == 'closed':
        return True
    return False



def hasBiddingClosed(itemid):
    item = getRecordByPk(Item, itemid)
    if item and item.status == 'closed':
        return True
    return False





def resetTimeForItemNotBidded(id):
    itemHasBids = hasItemBeenBidded(id)
    bidTimeExpired = hasBidTimeExpired(id)
    
    if bidTimeExpired and not itemHasBids:
        newEndDate = getBidEndDateFromNow(timezone)
        item = getRecordByPk(Item, id)
        if not item:
            logging.error(f'resetTimeForItemNotBidded: Item do not exit for, {id}')
            return
        
        item.endat = newEndDate
        item.save()



def handleBiddingClosure(itemid):

    if hasBiddingClosed(itemid):
        return

    itemHasBids = hasItemBeenBidded(itemid)
    bidTimeExpired = hasBidTimeExpired(itemid)
    item = getRecordByPk(Item, itemid)
    auction = getAuctionByItemId(itemid)
    highestBid = getHighestBid(itemid)
    
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

        item.status = 'closed'
        item.save()




def getBidWinner(itemid):
    if not hasBiddingClosed(itemid):
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






participantStatus = [
    'active',
    'observer'
]


auctionStatus = [
    'opened',
    'closed'
]