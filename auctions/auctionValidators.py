from django.shortcuts import get_object_or_404
from .models import Auction, Participant
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
  def __init__(self, userData, aid):
    self.errorMessages = []
    self.validateNumberFields(userData)
    self.validateMinimumBid(userData)
    self.validateHighestBid(userData, aid)

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
    if int(userData.get('minimumbid')) > int(userData.get('amount')):
      return self.errorMessages.append(f"Bid amount cannot be less than starting price, {userData.get('minimumbid')}")

  def validateHighestBid(self, userData, aid):
    try:
      auction = Auction.objects.get(pk=aid)
    except Exception as e:
      logging.error(f'ValidateHighestBid: {e}')
    else:
      if self.toInt(auction.auction1) > self.toInt(userData.get('amount')):
        return self.errorMessages.append(f'Bid amount cannot be less than the highest bid, {auction.auction1}')
  




class ValidateParticipant:
  def __init__(self, username):
    self.errorMessages = []
    self.validateDuplicateUsername(username)


  def validateDuplicateUsername(self, username):
    try:
      participant = Participant.objects.get(username=username)
    except:
      message = f'Username "{username}" does not exist'
      logging.error(message)
    else:
      if participant:
        message = f'<div class="error">Participant with username "{username}" already added</div>'
        logging.error(message)
        return self.errorMessages.append(message)
