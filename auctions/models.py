from django.db import models
from django.utils import timezone



class Auction(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default='opened')
    auction1 = models.CharField(max_length=200, default='0')
    maxparticipant = models.CharField(max_length=200, default='0')
    createdat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.description


class Item(models.Model):
    auctionid = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    categoryid = models.CharField(max_length=200)
    subcategoryid = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    minimumbid = models.IntegerField()
    username = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    createdat = models.DateTimeField(default=timezone.now)
    startat = models.DateTimeField(default=timezone.now)
    endat = models.DateTimeField()

    def __str__(self):
        return self.name
       

class Participant(models.Model):
    auctionid = models.CharField(max_length=200)
    userid = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    createdat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.auctionid



class Bid(models.Model):
    auctionid = models.CharField(max_length=200)
    itemid = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    amount = models.IntegerField()
    createdat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.auctionid


class Notification(models.Model):
    auctionid = models.CharField(max_length=200)
    itemid = models.CharField(max_length=200)
    seller = models.CharField(max_length=200)
    winner = models.CharField(max_length=200)
    bid = models.CharField(max_length=200)
    status = models.CharField(max_length=100, default='pending')
    bidtime = models.DateTimeField(default=timezone.now)
    createdat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.auctionid
 


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    createdat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    

class SubCategory(models.Model):
    categoryid = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    createdat = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name