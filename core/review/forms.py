from django import forms
from .models import ReviewModel
from shop.models import *

class SubmitReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ['product','rate','description']

    def clean(self):
        cleaned_data = super().clean()
        prodcut = cleaned_data.get("product")
        
        try:
            ProductModel.objects.get(id=prodcut.id,status=ProductStatusType.publish.value)
            
        except ProductModel.DoesNotExist:
            raise forms.ValidationError("This product is not available")
        
        return cleaned_data 