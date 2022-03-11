from django.contrib import admin
from base_app.models import Quote_Request_Rejected, Review, Movers_Email
from user.models import Quote_Request_Payment, Payment

admin.site.register(Quote_Request_Rejected)
admin.site.register(Review)
admin.site.register(Movers_Email)
admin.site.register(Quote_Request_Payment)
admin.site.register(Payment)
