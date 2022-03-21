from django.db import models
from base_app.models import Mover, Mover_Quote_Request


class Movers_Password_Recovery_Codes(models.Model):
    code = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)

    def __str__(self):
        return self.code


class Payment(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=6.5)
    created = models.DateTimeField(auto_now_add=True)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=1.36)
