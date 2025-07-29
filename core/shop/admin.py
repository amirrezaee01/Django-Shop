from django.contrib import admin
from .models import ProductModel, ProductCategoryModel, ProductImageModel
# Register your models here.

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'title', 'stock', 'status', 'created_date')

@admin.register(ProductCategoryModel)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_date')
    
@admin.register(ProductImageModel)
class ProductImageModelAdmin(admin.ModelAdmin):
    list_display = ('id','file', 'created_date')