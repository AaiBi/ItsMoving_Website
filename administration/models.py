from django.db import models
from base_app.models import Quote_Request, Mover


class Movers_Email_Admin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    quote_request = models.ForeignKey(Quote_Request, on_delete=models.CASCADE, default="")
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE, default="")
