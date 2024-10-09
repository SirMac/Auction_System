from django.contrib import admin
from .models import Item, Auction, Notification, Category, SubCategory



class ItemAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description", "createdat"]
    list_filter = ["createdat"]
    search_fields = ["name"]
admin.site.register(Item, ItemAdmin)


class AuctionAdmin(admin.ModelAdmin):
    list_display = ["id", "itemid", "status", "startat", "endat"]
    list_filter = ["itemid"]
    search_fields = ["itemid"]
admin.site.register(Auction, AuctionAdmin)



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

