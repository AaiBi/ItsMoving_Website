from django.db import models
from base_app.models import Mover


class Movers_Password_Recovery_Codes(models.Model):
    code = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    mover = models.ForeignKey(Mover, on_delete=models.CASCADE)

    def __str__(self):
        return self.code