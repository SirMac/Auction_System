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
  def __init__(self, req, aid):
    self.errorMessages = []
    self.bidData = req.POST
    self.amount = req.POST.get('amount')
    self.minimumbid = req.POST.get('minimumbid')
    self.highestBidAmt = req.POST.get('highestBidAmt')
    self.username = req.user.username
    self.validateNumberFields()
    self.validateMinimumBid()
    self.validateHighestBid(aid)
    self.validateParticipant(aid)
    self.validateAuctionStatus(aid)

  def toInt(self, str):
    try:
        num = int(str)
    except:
        return 0
    else:
        return num

  def validateNumberFields(self):
    numberFields = ['amount']
    for numberField in numberFields:
      if not self.bidData[numberField].isnumeric():
        logging.error(f'The field "{numberField}" must be numeic')
        return self.errorMessages.append(f'The field "{numberField}" must be numeic')

  def validateMinimumBid(self):
    if int(self.minimumbid) > int(self.amount):
      return self.errorMessages.append(f"Bid amount cannot be less than starting price, {self.minimumbid}")

  def validateHighestBid(self, aid):
    if self.toInt(self.highestBidAmt) > self.toInt(self.amount):
      return self.errorMessages.append(f'Bid amount cannot be less than the highest bid, {self.highestBidAmt}')
  
  def validateParticipant(self, aid):
    try:
      Participant.objects.get(auctionid=aid, username=self.username, status='active')
    except Exception as e:
      logging.error(f'validateParticipant: {e}')
      return self.errorMessages.append(f'Cannot bid. You are not a participant')

  def validateAuctionStatus(self, aid):
    try:
      Auction.objects.get(pk=aid, status='opened')
    except Exception as e:
      logging.error(f'validateAuctionStatus: {e}')
      return self.errorMessages.append(f'Cannot bid. Auction has closed')




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
