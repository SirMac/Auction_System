from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from django.urls import reverse
from .auctionValidators import ValidateAuction
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import Item
import logging

def addNewItem(req):
    name = req.POST['name']
    description = req.POST['description']
    categoryid = req.POST['categoryid']
    subcategoryid = req.POST['subcategoryid']
    minimumbid = req.POST['minimumbid']
    itemImage = req.FILES['image']
    
    print('image:', itemImage.name, settings.MEDIA_URL)
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
    return redirect('auctions:index')





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






def getAllItems():
    try:
        contacts = Item.objects.all()
    except (KeyError, Item.DoesNotExist):
        return None
    else:
        return contacts
            
