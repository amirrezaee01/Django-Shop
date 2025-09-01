from django.db import models
from django.utils.functional import cached_property


class ProductStatusType(models.IntegerChoices):
    publish = 1, ("نمایش")
    draft = 2, ("عدم نمایش")


class ProductCategoryModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ProductModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    category = models.ManyToManyField(ProductCategoryModel)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    image = models.ImageField(
        default='/default/product-image.png', upload_to="product/img/")
    description = models.TextField()
    brief_description = models.TextField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    price = models.DecimalField(default=0, max_digits=10, decimal_places=0)
    discount_percent = models.IntegerField(default=0)
    status = models.IntegerField(
        choices=ProductStatusType.choices, default=ProductStatusType.draft.value)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:

        ordering = ['-created_date']

    def __str__(self):
        return self.title

    def is_discounted(self):
        return self.discount_percent > 0

    def get_price(self):
        if self.is_discounted():
            discount = self.price * self.discount_percent / 100
            return round(self.price - discount)
        return round(self.price)

    def get_show_price(self):
        if self.is_discounted():
            return f"{self.get_price()} تومان <span class='text-muted text-decoration-line-through'>{self.price} تومان</span>"
        return f"{self.get_price()} تومان"

    def is_published(self):
        return self.status == ProductStatusType.publish.value


class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    file = models.ImageField(upload_to="product/extra-img/")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
