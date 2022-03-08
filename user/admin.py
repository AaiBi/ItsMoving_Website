from django.contrib import admin
from base_app.models import Quote_Request_Rejected, Review, Clients_Email, Movers_Email

admin.site.register(Quote_Request_Rejected)
admin.site.register(Review)
admin.site.register(Clients_Email)
admin.site.register(Movers_Email)