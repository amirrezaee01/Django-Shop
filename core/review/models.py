from django.db import models
from shop.models import ProductModel
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Avg
# Create your models here.


class ReviewStatusType(models.IntegerChoices):
    pending = 1, "در انتظار تایید"
    accepted = 2, "تایید شده"
    rejected = 3, "رد شده"


class ReviewModel(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    product = models.ForeignKey('shop.ProductModel',on_delete=models.CASCADE)
    description = models.TextField()
    rate = models.IntegerField(default=5, validators=[
                               MinValueValidator(0), MaxValueValidator(5)])
    status = models.IntegerField(
        choices=ReviewStatusType.choices, default=ReviewStatusType.pending.value)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
    
    def __str__(self):
        return f"{self.user} - {self.product.id}"
    
    
    def get_status(self):
        return {
            "id":self.status,
            "title":ReviewStatusType(self.status).name,
            "label":ReviewStatusType(self.status).label,
        }
        
        
def update_product_rating(product_id):
    average = ReviewModel.objects.filter(
        product_id=product_id, status=ReviewStatusType.accepted.value
    ).aggregate(value=Avg("rate"))["value"]
    ProductModel.objects.filter(pk=product_id).update(avg=round(average, 1) if average is not None else 0)


@receiver(post_save, sender=ReviewModel)
def calculate_avg_review(sender, instance, **kwargs):
    update_product_rating(instance.product_id)


@receiver(post_delete, sender=ReviewModel)
def recalculate_rating_after_delete(sender, instance, **kwargs):
    update_product_rating(instance.product_id)
