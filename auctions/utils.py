from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages import error, success
from django.urls import reverse
from .auctionValidators import ValidateAuction, ValidateBid
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from time import strftime, gmtime, mktime
from django.utils import timezone
from .models import Item, Bid, Auction
import logging

def addNewItem(req):
    name = req.POST['name']
    description = req.POST['description']
    categoryid = req.POST['categoryid']
    subcategoryid = req.POST['subcategoryid']
    minimumbid = req.POST['minimumbid']
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
        status = 'posted'
    )
    newItem.save()
    success(request=req, message=f'Item "{name}" created successfully')
    addAuction(newItem.id)
    return redirect('auctions:index')



def getBidEndDateFromNow(timezone):
    maxMinutes = 5
    currentDate = timezone.now()
    endate = currentDate + timezone.timedelta(minutes=maxMinutes)
    return endate


def addAuction(itemid):
    endate = getBidEndDateFromNow(timezone)
    newAuction = Auction(
        itemid = itemid, 
        endat = endate,
        status = 'open'
    )
    newAuction.save()
    logging.info(f'Auction for Item "{itemid}" created successfully')




def doUpdateAuction(req, id):
    firstName = req.POST['firstname']
    lastName = req.POST['lastname']
    company = req.POST['company']
    phone = req.POST['phone']
    email = req.POST['email']
    website = req.POST['website']
    unitNumber = req.POST['unitNumber']
    civicNumber = req.POST['civicNumber']
    street = req.POST['street']
    city = req.POST['city']
    province = req.POST['province']
    postalCode = req.POST['postalCode']

    referer = req.session['urlref']

    validItem = ValidateAuction(req.POST)
    messages = validItem.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
            error(request=req, message=message)
        return redirect(reverse('contacts:updateContact', args=(id,)))


    try:
        contact = Item.objects.get(pk=id)
    except (KeyError, Item.DoesNotExist):
        logging.error(KeyError)
        error(req, message='Update failed. Try again.')
        return render(req, 'contacts/updateContact.html')
    else:
        contact.firstName = firstName
        contact.lastName = lastName
        contact.company = company
        contact.phone = phone
        contact.email = email
        contact.website = website
        contact.unitNumber = unitNumber
        contact.civicNumber = civicNumber
        contact.street = street
        contact.city = city
        contact.province = province.upper()
        contact.postalCode = postalCode.upper()
        contact.save()

    del req.session['urlref']
    success(req, message='Contact updated successfully')
    return redirect(referer)





def getAllRecords(model):
    try:
        rows = model.objects.all()
    except (KeyError, model.DoesNotExist):
        return None
    else:
        return rows



def getItemByPk(model, id):
    try:
        item = model.objects.get(pk=id)
    except (KeyError, model.DoesNotExist):
        return None
    else:
        return item
            


def addNewBid(req, id):
    amount = req.POST['amount']
    username = req.POST['username']
    
    validBid = ValidateBid(req.POST)
    messages = validBid.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
        return HttpResponse(message)

    auction = get_object_or_404(Auction, itemid=id)

    newBid = Bid(
        auctionid = auction.id, 
        itemid = id, 
        username = username, 
        amount = amount
    )
    newBid.save()
    auction.auction1 = amount
    auction.save()

    logging.info(f'Bid for Item "{id}" posted successfully')

    bids = get_object_or_404(Bid, auctionid=auction.id)
    if bids:
        bidList = "<ul>"
        for bid in bids:
           bidList += f'<li>Competing Bid: ${bid.amount}<li>'
        bidList += '<ul>'
    return HttpResponse(bidList)





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
        bids = Bid.objects.get(itemid=id)
    except (KeyError, Bid.DoesNotExist):
        logging.error(f'Bid does not exist')
        return False
    else:
        if bids:
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



def handleBidWinner(id):
    pass