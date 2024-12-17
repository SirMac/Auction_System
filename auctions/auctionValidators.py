from .models import Auction, Participant
import logging



class ValidateAuctionBase:
  def __init__(self):
    self.errorMessages = []

  def validateEmptyFields(self, userData):
    for fieldName in userData:
      if len(userData[fieldName]) == 0:
        logging.error(f'The field "{fieldName}" cannot be empty')
        self.errorMessages.append(f'The field "{fieldName}" cannot be empty')

  def validateEditByOwner(self, req, id):
    auctionId = id
    currentUser = req.user.username
    try:
      auction = Auction.objects.get(pk=auctionId)
    except:
      message = f'Auction with id "{auctionId}" does not exist'
      logging.error(message)
    else:
      if auction.username != currentUser:
        message = f'Your are not authorized to perform this action'
        logging.error(message)
        return self.errorMessages.append(message)
      
  
  def validateTextFields(self, userData, textFields):
    for textField in textFields:
      if not userData[textField].replace(' ', '').isalpha():
        logging.error(f'The field "{textField}" must be letters only')
        self.errorMessages.append(f'The field "{textField}" must be letters only')


  def validateNumberFields(self, userData, numberFields):
    for numberField in numberFields:
      if not userData[numberField].isnumeric():
        logging.error(f'The field "{numberField}" must be numeic')
        self.errorMessages.append(f'The field "{numberField}" must be numeric')

  def validateParticipant(self, req, aid):
    username = req.user.username
    try:
      Participant.objects.get(auctionid=aid, username=username, status='active')
    except Exception as e:
      logging.error(f'validateParticipant: {e}')
      return self.errorMessages.append(f'Access denied. You are not a participant')

  def validateAuctionStatus(self, aid):
    try:
      Auction.objects.get(pk=aid, status='opened')
    except Exception as e:
      logging.error(f'validateAuctionStatus: {e}')
      return self.errorMessages.append(f'Access denied. Auction has closed')



class ValidateAddAuction(ValidateAuctionBase):
    
  def __init__(self, userData):
    super().__init__()
    self.validateEmptyFields(userData)
    # textFields = ['description']
    # self.validateTextFields(userData, textFields)
    numberFields = ['maxparticipant']
    self.validateNumberFields(userData, numberFields)


class ValidateEditAuction(ValidateAuctionBase):
  def __init__(self, req, auctionId):
    super().__init__()
    self.validateEmptyFields(req.POST)
    self.validateEditByOwner(req, auctionId)



class ValidateAddItem(ValidateAuctionBase):
    
  def __init__(self, req, auctionId):
    super().__init__()
    userData = req.POST
    self.validateEmptyFields(userData)
    # textFields = ['name']
    # self.validateTextFields(userData, textFields)
    numberFields = ['minimumbid']
    self.validateNumberFields(userData, numberFields)
    self.validateParticipant(req, auctionId)
    self.validateAuctionStatus(auctionId)



    
class ValidateBid(ValidateAuctionBase):
  def __init__(self, req, aid, highestBid):
    super().__init__()
    self.bidData = req.POST
    self.amount = req.POST.get('amount')
    self.minimumbid = req.POST.get('minimumbid')
    self.highestBidAmt = highestBid
    self.username = req.user.username
    numberFields = ['amount']
    self.validateNumberFields(req.POST, numberFields)
    self.validateMinimumBid()
    self.validateHighestBid(aid)
    self.validateParticipant(req, aid)
    self.validateAuctionStatus(aid)

  def toInt(self, str):
    try:
        num = int(str)
    except:
        return 0
    else:
        return num
  
  def validateMinimumBid(self):
    if int(self.minimumbid) > int(self.amount):
      return self.errorMessages.append(f"Bid amount cannot be less than starting price, {self.minimumbid}")

  def validateHighestBid(self, aid):
    if self.toInt(self.highestBidAmt) > self.toInt(self.amount):
      return self.errorMessages.append(f'Bid amount cannot be less than the highest bid, {self.highestBidAmt}')
  


class ValidateAddParticipant(ValidateAuctionBase):
  def __init__(self, req, id):
    super().__init__()
    userId = req.POST.get('username')
    self.validateDuplicateUsername(userId, id)
    self.validateNumberOfParticipants(id)
    self.validateEditByOwner(req, id)
    self.validateAuctionStatus(id)



  def validateDuplicateUsername(self, userId, id):
    try:
      participant = Participant.objects.get(auctionid=id, userid=userId, status='active')
    except:
      message = f'ValidateParticipant: Username with id "{userId}" does not exist'
      logging.error(message)
    else:
      if participant:
        message = f'Selected participant already added'
        logging.error(message)
        return self.errorMessages.append(message)

  def validateNumberOfParticipants(self, auctionid):
    try:
      auction = Auction.objects.get(pk=auctionid)
      participants = Participant.objects.filter(auctionid=auctionid, status='active')
    except:
      message = f'validateNumberOfParticipants: Participants for auction "{auctionid}" does not exist'
      logging.error(message)
    else:
      if not auction and len(participants) <= 0:
        return 
      
      if int(auction.maxparticipant) <= len(participants):
        message = f'Cannot add participants more than allowed'
        logging.error(message)
        return self.errorMessages.append(message)