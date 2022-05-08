from django.contrib import admin
from base_app.models import Quote_Request_Rejected, Review, Movers_Email
from user.models import Payment, Payment_Notification

admin.site.register(Quote_Request_Rejected)
admin.site.register(Review)
admin.site.register(Movers_Email)
admin.site.register(Payment)
admin.site.register(Payment_Notification)
