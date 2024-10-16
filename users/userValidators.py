from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from auctions.models import Item, Auction
from auctions.utils import getHighestBid
import logging
# from django.contrib.auth.models import User


class ValidateUser:

    def __init__(self, userData):
        self.errorMessages = []
        self.username = userData['username']
        self.email = userData['email']
        self.password1 = userData['password1']
        self.password2 = userData['password2']
        self.confirmPassword()
        self.validateEmail()

    def confirmPassword(self):
        if self.password1 != self.password2:
            self.errorMessages.append('Passwords do not match')

    def validateEmail(self):
        try:
            validate_email(self.email)
        except ValidationError as e:
            print(str(e))
            self.errorMessages.append('Email address invalid')

    # def checkDuplicate(self):
    #     try:
    #         User.objects.get(email=self.email)
    #     except (KeyError, User.DoesNotExist):
    #         return False
    #     else:
    #         return True


class ValidateUserDeregistration:

    def __init__(self, username):
        self.errorMessages = []
        self.username = username
        self.validateActiveItemOnAuction()
        self.validateActiveBid()
        self.validateAdminUser()



    def validateAdminUser(self):
        if self.username.lower() == 'admin':
            message = 'Cannot deregister admin account'
            logging.error(message)
            self.errorMessages.append(message)


    def validateActiveItemOnAuction(self):
        try:
            item = Item.objects.filter(username=self.username, status='opened')
        except KeyError as e:
            logging.error(str(e))
        else:
            if len(item) <= 0:
                return
            item = item[0]
            if item.status == 'close':
                return
            message = f"Deregistration failed. You have an active item, '{item.name}' on auction"
            logging.error(message)
            self.errorMessages.append(message)



    def validateActiveBid(self):
        auction = []
        try:
            item = Item.objects.filter(username=self.username, status='opened')
            if len(item) > 0:
                item = item[0]
                auction = Auction.objects.filter(itemid=item.id)
        except KeyError as e:
            logging.error(str(e))
        else:
            if len(auction) <= 0:
                return
            auction = auction[0]
            highestBid = getHighestBid(auction.id)
            if highestBid and highestBid.username == self.username:
                message = f"Deregistration failed. You are the highest bidder for the item, '{item.name}' on auction"
                logging.error(message)
                self.errorMessages.append(message)
