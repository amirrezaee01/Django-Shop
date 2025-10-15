from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from shop.models import *
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin 
from django.db import models



class ReviewStatusType(models.IntegerChoices):
    pending = 1,"در انتظار تایید"
    accepted = 2,"تایید شده"
    rejected = 3,"رد شده"

class ReviewModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    product = models.ForeignKey("shop.ProductModel", on_delete=models.CASCADE)
    
    description = models.TextField()
    
    rate = models.IntegerField(default=5,validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    status = models.IntegerField(choices=ReviewStatusType.choices, default=ReviewStatusType.pending.value)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.title}"

@receiver(post_save, sender=ReviewModel)
def calculate_avg_review(sender, instance,created, **kwargs):
    pass
    
