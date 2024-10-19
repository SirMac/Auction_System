from django.shortcuts import get_object_or_404
from .models import Auction
import logging

class ValidateAuction:
    
  def __init__(self, userData):
    self.errorMessages = []
    self.validateEmptyFields(userData)
    self.validateNumberFields(userData)
  

  def validateEmptyFields(self, userData):
    for fieldName in userData:
      if len(userData[fieldName]) == 0:
        logging.error(f'The field "{fieldName}" cannot be empty')
        self.errorMessages.append(f'The field "{fieldName}" cannot be empty')


  def validateTextFields(self, userData):
    textFields = ['name','description']
    for textField in textFields:
      if not userData[textField].isalpha():
        logging.error(f'The field "{textField}" must be letters only')
        self.errorMessages.append(f'The field "{textField}" must be letters only')


  def validateNumberFields(self, userData):
    numberFields = ['minimumbid']
    for numberField in numberFields:
      if not userData[numberField].isnumeric():
        logging.error(f'The field "{numberField}" must be numeic')
        self.errorMessages.append(f'The field "{numberField}" must be numeic')


    
class ValidateBid:
  def __init__(self, userData):
    self.errorMessages = []
    self.validateNumberFields(userData)
    self.validateMinimumBid(userData)
    self.validateHighestBid(userData)

  def toInt(self, str):
    try:
        num = int(str)
    except:
        return 0
    else:
        return num

  def validateNumberFields(self, userData):
    numberFields = ['amount']
    for numberField in numberFields:
      if not userData[numberField].isnumeric():
        logging.error(f'The field "{numberField}" must be numeic')
        return self.errorMessages.append(f'The field "{numberField}" must be numeic')

  def validateMinimumBid(self, userData):
    if int(userData['minimumbid']) > int(userData.get('amount')):
      return self.errorMessages.append(f'Amount cannot be less than starting price')

  def validateHighestBid(self, userData):
    id = userData.get('id')
    if id:
      auction = get_object_or_404(Auction, itemid=id)
      if self.toInt(auction.auction1) > self.toInt(userData.get('amount')):
        return self.errorMessages.append(f'Amount cannot be less than highest bidded price, {auction.auction1}')
    else:
      self.errorMessages.append(f'An error occured. Try again later.')