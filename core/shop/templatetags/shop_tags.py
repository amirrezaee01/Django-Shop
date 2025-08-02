from django import template
from shop.models import ProductStatusType, ProductModel

register = template.Library()

@register.inclusion_tag("includes/latest-products.html")
def show_latest_products():
    latest_products = ProductModel.objects.filter(
        status=ProductStatusType.publish.value).distinct().order_by("-created_date")[:8]
    return {"latest_products": latest_products}