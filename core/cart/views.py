from django.shortcuts import get_object_or_404
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from shop.models import ProductModel
from .cart import CartSession


class SessionAddProductView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get('product_id')
        if product_id:
            cart.add_product(product_id)
        return JsonResponse({
            'cart': cart.get_cart_dict(),
            'total_quantity': cart.__len__(),
        })


class SessionCartSummaryView(TemplateView):
    template_name = 'cart/cart_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)
        cart_items = cart.get_cart_dict().get('items', [])

        for item in cart_items:
            item['product_obj'] = get_object_or_404(
                ProductModel, id=item['product_id']
            )

        context['cart_items'] = cart_items
        context['total_quantity'] = cart.get_total_quantity()
        return context
