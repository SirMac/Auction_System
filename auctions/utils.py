from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from django.urls import reverse
from .auctionValidators import ValidateAuction
from .models import Item
import logging

def addNewAuction(req):
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


    validContact = ValidateAuction(req.POST)

    if validContact.checkDuplicate():
        message = f'Email ({email}) already exists'
        logging.warning(message)
        error(request=req, message=message)
        return redirect('contacts:createContact')

    
    messages = validContact.errorMessages
    
    if messages:
        for message in messages:
            logging.error(message)
            error(request=req, message=message)
        return redirect('contacts:createContact')


    contact = Item(
        firstName = firstName, 
        lastName = lastName, 
        company = company, 
        phone = phone, 
        email = email, 
        website = website, 
        unitNumber = unitNumber, 
        civicNumber = civicNumber, 
        street = street, 
        city = city, 
        province = province.upper(), 
        postalCode = postalCode.upper()
    )
    contact.save()
    success(request=req, message=f'Contact for "{firstName} {lastName}" created successfully')
    return redirect('contacts:index')





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

    validContact = ValidateAuction(req.POST)
    messages = validContact.errorMessages
    
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






def getAllAuctions():
    try:
        contacts = Item.objects.all()
    except (KeyError, Item.DoesNotExist):
        return None
    else:
        return contacts
            
