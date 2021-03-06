from django.contrib import admin
from base_app.models import Mover, Moving_Type1, Moving_Type2, Country, \
    Mover_Moving_Type2, Mover_Country, Quote_Request, Mover_Quote_Request, \
    Number_Mover_Quote_Request_PerDay, Number_Distribution_Quote_Request, Region, Mover_Region, \
    Customers_Notification_Email

admin.site.register(Moving_Type1)
admin.site.register(Moving_Type2)
admin.site.register(Mover)
admin.site.register(Mover_Moving_Type2)
admin.site.register(Country)
admin.site.register(Mover_Country)
admin.site.register(Quote_Request)
admin.site.register(Mover_Quote_Request)
admin.site.register(Number_Mover_Quote_Request_PerDay)
admin.site.register(Number_Distribution_Quote_Request)
admin.site.register(Region)
admin.site.register(Mover_Region)
admin.site.register(Customers_Notification_Email)
