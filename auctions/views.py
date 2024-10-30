from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.http import HttpResponse
from time import strftime
from .utils import addNewItem, getAllRecords, getAuctionByItemId, hasBiddingClosed
from .utils import addNewBid, getBidTimeDiffInSecTupple, resetTimeForItemNotBidded
from .utils import handleAuctionClosure, hasAuctionClosed, getNotificationCount
from .utils import getNotificationList, getRecordByPk, getBidWinner, addNewAuction
from .utils import addNewParticipant, participantStatus, doEditAuction
from .utils import doEditparticipant, auctionStatus
from .models import Auction, Item, Bid, Category, SubCategory, Participant
from django.contrib.auth.models import User
import logging



# @login_required
def index(req):
    editBtnLabel = {'editBtnLabel':'Edit'}
    context = {
        'pageOptions':{
            'page':'index', 
            'buttonLabel':'View', 
            'header':'Active Auctions',
            **editBtnLabel
        }
    }
    try:
        filteredAuction = Auction.objects.filter(status='opened')
    except:
        logging.error('Index: Auctions not found')
        return render(req, 'auctions/index.html', context=context)
    else:
        context['auctions'] = filteredAuction
        return render(req, 'auctions/index.html', context=context)
    

@login_required
def addAuction(req):
    if req.method == 'GET':
        return render(req, 'auctions/addAuction.html')
    
    return addNewAuction(req)


@login_required
def editAuction(req, id):

    if req.method == 'POST':
        return doEditAuction(req, id)

    auction = getRecordByPk(Auction, id)
    context = {'auction':auction, 'auctionStatus':auctionStatus}
    return render(req, 'auctions/editAuction.html', context=context)


@login_required
def auctionIndex(req, id):
    auction = getRecordByPk(Auction, id)
    context = {
        'auction':auction, 
        'pageOptions':{
            'page':'auctionIndex', 
            'viewBtnLabel':'Bid', 
            'header':'Items On Auction',
            'buttonLabel': 'Bid'
        }
    }
    try:
        filteredItems = Item.objects.filter(auctionid=id, status='opened')
    except:
        logging.error('Index: items not found')
        return render(req, 'auctions/auctionIndex.html', context=context)
    else:
        context['items'] = filteredItems
        return render(req, 'auctions/auctionIndex.html', context=context)
    


@login_required
def addParticipant(req, id):

    if req.method == 'POST':
        return addNewParticipant(req, id)

    auction = getRecordByPk(Auction, id)
    context = {'auction':auction, 'participantStatus':participantStatus}
    return render(req, 'auctions/addParticipant.html', context=context)
    


@login_required
def listParticipants(req, id):
    auction = getRecordByPk(Auction, id)
    auctionContext = {'auction': auction}
    try:
        participants = Participant.objects.filter(auctionid=id, status__in=participantStatus)
    except Exception as e:
        logging.error(f'listParticipants: {e}')
        return render(req, 'auctions/listParticipant.html', context=auctionContext)
    else:
        context = {'participants': participants, **auctionContext}
        return render(req, 'auctions/listParticipant.html', context=context)



@login_required
def editParticipant(req, aid, pid):
    participant = getRecordByPk(Participant, pid)
    auction = getRecordByPk(Auction, aid)

    if not auction or not participant:
        return index(req)

    if req.method == 'GET':
        context = {'auction': auction, 'participant':participant, 'participantStatus':participantStatus}
        return render(req, 'auctions/editParticipant.html', context=context)

    return doEditparticipant(req, aid, pid)



@login_required
def deleteParticipant(req, aid, pid):
    try:
        participant = Participant.objects.get(pk=pid)
    except:
        logging.error('doEditparticipant: Participant not found')
        return redirect('auctions:editParticipant', aid=aid ,pid=pid)
    else:
        participant.status = 'deleted'
        participant.save()
        return redirect('auctions:listParticipant', id=aid)



@login_required
def addItem(req, id):
    auction = getRecordByPk(Auction, id)
    if req.method == 'GET':
        return render(req, 'auctions/addItem.html', context={'auction':auction})
    
    return addNewItem(req, id)


@login_required
def bidItem(req, aid, itemid):
    if req.method == 'GET':
      page = req.GET.get('page')
      triggers = {'index':'every 1s', 'soldItems':'load'}

      try:
        trigger = triggers[page]
      except Exception as e:
        logging.error(e)
        trigger = 'every 1s'


      bids = None
      auction = getRecordByPk(Auction, aid) 

      try:
          bids = Bid.objects.filter(auctionid=auction.id)
      except:
          logging.error(f'Item does not exist')
          
      item = getRecordByPk(Item, itemid)

      context = {
          'auction': auction,
          'item': item, 
          'bids':bids, 
          'pageOptions':{'trigger':trigger}
        }
      
      return render(req, 'auctions/bidItem.html', context=context)

    return addNewBid(req, aid, itemid)




def getBidClosingTime(req, id):
    
    handleAuctionClosure(id)

    if hasBiddingClosed(id):
        return HttpResponse('Bidding closed')
    
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
            bidList += f"<li><span class='bid-date'>{bid.createdat.strftime('%Y-%m-%d %H:%M:%S')}</span> Competing bid ({bid.username}): <span class='bid-amount'>${bid.amount}</span><li>"
        bidList += '<ul>'
        winner = getBidWinner(id)
        if winner:
            bidList += f"<div id='bid-winner'>Winner: {winner}</div>"
        return HttpResponse(bidList)




def getSelectHtml(req):
    tableName = req.GET.get('target').lower()
    categoryId = req.GET.get('categoryid')
    modelOptions = {
        'category':{'model':Category, 'label':'name', 'filterKwargs':''}, 
        'subcategory':{'model':SubCategory, 'filterKwargs':{'categoryid':categoryId}, 'label':'name'}, 
        'user':{'model':User, 'filterKwargs':{'is_active':1}, 'label':'username'}
    } 
    select = "<option value=''>---</option>"

    if not tableName:
        logging.error('getSelectHtml: request query string empty')
        return HttpResponse(select)
    
    modelOption = modelOptions[tableName]

    if not modelOption:
        logging.error(f'getSelectHtml: modelOption not found for {tableName}')
        return HttpResponse(select)
    
    model = modelOption['model']

    if not model:
        logging.error(f'getSelectHtml: model not found for {tableName}')
        return HttpResponse(select)
    
    filterKwargs = modelOption['filterKwargs']

    if filterKwargs:
        records = model.objects.filter(**filterKwargs)
    else:
        records = getAllRecords(model)

    if not records:
        logging.error(f'getSelectHtml: record not found for {tableName}')
        return HttpResponse(select)
    
    label = modelOption['label']

    for record in records:
        select += f"<option value='{record.id}'>"
        select += getattr(record, label)
        select += '</option>'

    return HttpResponse(select)





def getSoldItems(req):
    context = {'pageOptions':{'page':'soldItems', 'buttonLabel':'View', 'header':'Sold Items'}}
    try:
        filteredItems = Item.objects.filter(status='closed')
    except:
        logging.error('getSoldItems: items not found')
        return render(req, 'auctions/index.html', context=context)
    else:
        context['items'] = filteredItems
        return render(req, 'auctions/index.html', context=context)