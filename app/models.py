from django.db import models
from uuid import uuid4

PAYMENT_STATUS_CHOICES=(
    ("pending","pending"),
    ("success","success"),
    ("failed","failed")
)

# Create your models here.
class Transaction(models.Model):
    trans_id=models.CharField(max_length=255,primary_key=True,default=uuid4)
    amount=models.FloatField()
    order_id=models.CharField(max_length=255,null=True,blank=True)
    payment_status=models.CharField(max_length=255,choices=PAYMENT_STATUS_CHOICES,default="pending")
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.trans_id)