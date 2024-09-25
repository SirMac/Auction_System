from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.messages import error, success
from django.db.models import Q
from .utils import addNewAuction, doUpdateAuction, getAllAuctions
from .models import Item
import logging



# @login_requireds
def index(req):
    return render(req, 'auctions/index.html')
    


@login_required
def createContact(req):
    if req.method == 'GET':
        return render(req, 'auctions/addContact.html')
    
    return addNewAuction(req)



@login_required
def readContact(req):
    readAllContacts = req.GET.get('readall')

    if readAllContacts is None or readAllContacts.lower() == 'yes':
        contacts = getAllAuctions()
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


