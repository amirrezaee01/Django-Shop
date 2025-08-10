from django.views.generic import View, TemplateView
from django.http import JsonResponse
from shop.models import ProductModel
from .cart import CartSession


class SessionAddProductView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get('product_id')
        success = False
        if product_id:
            success = cart.add_product(product_id)
        return JsonResponse({
            'cart': cart.get_cart_dict(),
            'total_quantity': cart.get_total_quantity(),
            'success': success,
        })


class SessionUpdateProductQuantityView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        success = False
        if product_id and quantity:
            success = cart.update_product_quantity(product_id, quantity)
        return JsonResponse({
            'cart': cart.get_cart_dict(),
            'total_quantity': cart.get_total_quantity(),
            'success': success,
        })


class SessionRemoveProductView(View):
    def post(self, request, *args, **kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get('product_id')
        success = False
        if product_id:
            success = cart.remove_product(product_id)
        return JsonResponse({
            'cart': cart.get_cart_dict(),
            'total_quantity': cart.get_total_quantity(),
            'success': success,
        })


class SessionCartSummaryView(TemplateView):
    template_name = 'cart/cart_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)
        context['cart_items'] = cart.get_cart_items()
        context['total_quantity'] = cart.get_total_quantity()
        context['total_payment_price'] = cart.get_total_payment_amount()
        return context
