from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, success
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse
from time import strftime, gmtime
from .utils import addNewItem, doUpdateAuction, getAllRecords 
from .utils import addNewBid, getBidTimeDiffInSecTupple, resetTimeForItemNotBidded
from .models import Item, Bid, Auction
import logging



# @login_required
def index(req):
    # get only items whose auction is not closed
    items = getAllRecords(Item)
    if items:
        context = {'items': items}
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
        try:
            auction = Auction.objects.get(itemid=id)
            bids = Bid.objects.get(auctionid=auction.id)
        except:
            logging.error(f'Item does not exist')
        item = get_object_or_404(Item, pk=id)
        context = {'item': item, 'bids':bids}
        return render(req, 'auctions/bidItem.html', context=context)
    
    return addNewBid(req, id)



@login_required
def readContact(req):
    readAllContacts = req.GET.get('readall')

    if readAllContacts is None or readAllContacts.lower() == 'yes':
        contacts = getAllRecords(Item)
        if contacts is None:
            logging.error('No contact found.')
            error(req, message='No contact found.')
            return render(req, 'auctions/index.html')
        
        context = {'contacts': contacts}
        if len(contacts) == 0:
            logging.warning('No record found')
            error(req, message='No record found')
        return render(req, 'auctions/index.html', context=context)
            

    firstname = req.GET.get('firstname')
    lastname = req.GET.get('lastname')
    email = req.GET.get('email')


    if len(firstname)==0 and len(lastname)==0 and len(email)==0:
        logging.error('Provide at least one input')
        error(req, message='Provide at least one input')
        return redirect('contacts:index')
    
    
    contacts = Item.objects.filter(
        Q(firstName__iexact=firstname) |
        Q(lastName__iexact=lastname) |
        Q(email__iexact=email) 
    )
        
    if len(contacts) == 0:
        logging.warning('No record found')
        error(req, message='No record found')
        return render(req, 'auctions/index.html', context={'contacts':contacts})

    context = {'contacts': contacts}
    return render(req, 'auctions/index.html', context=context)
    
    
    

@login_required
def updateContact(req, id):
    if req.method == 'GET':
        if not req.session.get('urlref'):
            req.session['urlref'] = req.META.get('HTTP_REFERER')
        contact = get_object_or_404(Item, pk=id)
        context = {'contact': contact}
        return render(req, 'auctions/updateContact.html', context=context)

    return doUpdateAuction(req, id)    



@login_required
def deleteContact(req, id):
    try:
        contact = Item.objects.get(pk=id)
    except (KeyError, Item.DoesNotExist):
        logging.error(KeyError)
        error(req, message='Contact delete failed. Try again')
    else:
        success(req, message='Contact deleted successfully')
        contact.delete()
    return redirect(req.META.get('HTTP_REFERER'))



@login_required
def viewDetail(req, id):
    contact = get_object_or_404(Item, pk=id)
    context = {'contact': contact}
    return render(req, 'auctions/detail.html', context=context)




def getBidClosingTime(req, id):
    
    resetTimeForItemNotBidded(id)

    bidTimeTupple = getBidTimeDiffInSecTupple(id)
    timeDiff = strftime('%H:%M:%S', bidTimeTupple)
    return HttpResponse(timeDiff)
    

