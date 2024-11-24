from django.contrib import admin
from .models import Item, Auction, Notification, Category, SubCategory
from .models import Bid, Participant




class AuctionAdmin(admin.ModelAdmin):
    list_display = ["id", "description", "status", "maxparticipant", "createdat"]
    list_filter = ["id"]
    search_fields = ["id"]
admin.site.register(Auction, AuctionAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ["id", "auctionid", "name", "description", "createdat"]
    list_filter = ["auctionid"]
    search_fields = ["name"]
admin.site.register(Item, ItemAdmin)


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["id", "auctionid", "userid", "username", "status", "createdat"]
    list_filter = ["id"]
    search_fields = ["id"]
admin.site.register(Participant, ParticipantAdmin)


class BidAdmin(admin.ModelAdmin):
    list_display = ["id", "auctionid", "itemid", "username", "amount", "createdat"]
    list_filter = ["id"]
    search_fields = ["id"]
admin.site.register(Bid, BidAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "auctionid", "seller", "winner", "bid"]
    list_filter = ["auctionid"]
    search_fields = ["auctionid"]
admin.site.register(Notification, NotificationAdmin)



class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description", "createdat"]
    list_filter = ["name"]
    search_fields = ["name"]
admin.site.register(Category, CategoryAdmin)



class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "categoryid", "name", "description", "createdat"]
    list_filter = ["name"]
    search_fields = ["name"]
admin.site.register(SubCategory, SubCategoryAdmin)

