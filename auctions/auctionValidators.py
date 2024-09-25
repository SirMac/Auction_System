from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Item
import logging
import re

class ValidateAuction:
    
  def __init__(self, userData):
    self.errorMessages = []
    self.firstName = userData['firstname']
    self.lastName = userData['lastname']
    self.company = userData['company']
    self.phone = userData['phone']
    self.email = userData['email']
    self.website = userData['website']
    self.unitNumber = userData['unitNumber']
    self.civicNumber = userData['civicNumber']
    self.street = userData['street']
    self.city = userData['city']
    self.province = userData['province']
    self.postalCode = userData['postalCode']
    self.validateEmptyFields(userData)
    self.validateTextFields(userData)
    self.validateNumberFields(userData)
    self.validateEmail()
    self.validatePhoneNumber()
    self.validateWebsite()
    self.validateStreetCode()
    self.validateProvince()
    self.validatePostalCode()

      

  def checkDuplicate(self):
    try:
      Item.objects.get(email=self.email)
    except (KeyError, Item.DoesNotExist):
      return False
    else:
      return True
  

  def validateEmptyFields(self, userData):
    for fieldName in userData:
      if len(userData[fieldName]) == 0:
        logging.error(f'The field "{fieldName}" cannot be empty')
        self.errorMessages.append(f'The field "{fieldName}" cannot be empty')


  def validateTextFields(self, userData):
    textFields = ['firstname','lastname']
    for textField in textFields:
      if not userData[textField].isalpha():
        logging.error(f'The field "{textField}" must be letters only')
        self.errorMessages.append(f'The field "{textField}" must be letters only')


  def validateNumberFields(self, userData):
    numberFields = ['civicNumber', 'unitNumber']
    for numberField in numberFields:
      if not userData[numberField].isnumeric():
        logging.error(f'The field "{numberField}" must be numeic')
        self.errorMessages.append(f'The field "{numberField}" must be numeic')


  def validatePhoneNumber(self):
    message = "Phone number must be in the format: '+1 (111) 111-1111'"
    phoneRegex = r'^\+1\s\(\d{3}\)\s\d{3}-\d{4}$'
    matchedPhoneNumber = re.search(phoneRegex, self.phone)
    if matchedPhoneNumber == None:
      logging.error(message)
      self.errorMessages.append(message)


  def validateWebsite(self):
    message = "Website must be in the format: 'http(s)://x.x'"
    websiteRegex = r'^https?://\w+\.\w+$'
    matchedWebsite = re.search(websiteRegex, self.website)
    if matchedWebsite == None:
      logging.error(message)
      self.errorMessages.append(message)


  def validateEmail(self):
    message = 'Email address invalid'
    try:
      validate_email(self.email) 
    except ValidationError as e:
      logging.error(str(e))
      self.errorMessages.append(message) 

    
  def validateStreetCode(self):
    message = 'Street code must be alphanumeric only'
    streetCodeRegex = r'^[a-zA-Z0-9]+$'
    matchedStreetCode = re.search(streetCodeRegex, self.street)
    if matchedStreetCode == None:
      logging.error(message)
      self.errorMessages.append(message)  


  def validateProvince(self):
    message = 'Province must be two letters'
    provinceRegex = r'^[a-zA-Z]{2}$'
    matchedProvince = re.search(provinceRegex, self.province)
    if matchedProvince == None:
      logging.error(message)
      self.errorMessages.append(message)  
    

  def validatePostalCode(self):
    message = 'Postal code must be in the format 1A1 or A1A'
    postalCodePatterns = [r'^[a-zA-Z][0-9][a-zA-Z]$', r'^[0-9][a-zA-Z][0-9]$']
    wrongPatternCount = 0
    for pattern in postalCodePatterns:
      matchedPostalCode = re.search(pattern, self.postalCode)
      if matchedPostalCode == None:
        wrongPatternCount += 1
    if wrongPatternCount == len(postalCodePatterns):
      logging.error(message)
      self.errorMessages.append(message)
    