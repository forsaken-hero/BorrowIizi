from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    #item_id = models.IntegerField()
    item_name = models.CharField()
    #item_avail = models.BooleanField()
    item_loaner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
