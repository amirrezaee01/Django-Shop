from shop.models import ProductModel, ProductStatusType


class CartSession:
    total_payment_price = 0

    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault('cart', {
            'items': [],

        })

    def update_product_quantity(self, product_id, quantity):
        for item in self._cart['items']:
            if product_id == item['product_id']:
                item['quantity'] = int(quantity)
                break
        else:
            new_item = {
                'product_id': product_id,
                'quantity': int(quantity)
            }
            self._cart['items'].append(new_item)
        self.save()

    def remove_product(self, product_id):
        for item in self._cart['items']:
            if product_id == item['product_id']:
                self._cart['items'].remove(item)
                break
        self.save()

    def add_product(self, product_id):
        for item in self._cart['items']:
            if product_id == item['product_id']:
                item['quantity'] += 1
                break
        else:
            new_item = {
                'product_id': product_id,
                'quantity': 1
            }
            self._cart['items'].append(new_item)
        self.save()

    def clear(self):
        self._cart = self.session['cart'] = {
            'items': [],
        }
        self.save()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        cart_items = self._cart['items']
        self.total_payment_price = 0
        for item in cart_items:
            product_obj = ProductModel.objects.get(
                id=item['product_id'], status=ProductStatusType.publish.value)
            item['product_obj'] = product_obj
            total_price = int(item['quantity']) * product_obj.get_price()
            item['total_price'] = total_price
            self.total_payment_price += total_price
        return cart_items

    def get_total_payment_amount(self):
        return self.total_payment_price

    def get_total_quantity(self):
        total_quantity = 0
        for item in self._cart['items']:
            total_quantity += item['quantity']
        return total_quantity

    def __len__(self):
        return len(self._cart['items'])

    def save(self):
        self.session.modified = True
