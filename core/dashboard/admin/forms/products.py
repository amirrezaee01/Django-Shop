from django import forms
from shop.models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['category', 'title', 'slug', 'image', 'description',
                  'price', 'status', 'brief_description', 'stock', 'discount_percent']
