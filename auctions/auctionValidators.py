from django.shortcuts import get_object_or_404
from .models import Auction
import logging
import re

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
      if int(auction.auction1) > int(userData.get('amount')):
        return self.errorMessages.append(f'Amount cannot be less than highest bidded price, {auction.auction1}')
    else:
      self.errorMessages.append(f'An error occured. Try again later.')