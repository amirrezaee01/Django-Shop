from shop.models import ProductModel, ProductStatusType


class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault('cart', {'items': []})
        self.total_payment_price = 0  # instance variable, not class variable

    def add_product(self, product_id):
        # Check if product already in cart
        for item in self._cart['items']:
            if item['product_id'] == product_id:
                return False  # already added, do not increase quantity here

        # Get product and check stock
        product = ProductModel.objects.filter(
            id=product_id, status=ProductStatusType.publish.value).first()
        if not product or product.stock <= 0:
            return False  # product missing or no stock

        # Add product with quantity 1
        self._cart['items'].append({'product_id': product_id, 'quantity': 1})
        self.save()
        return True

    def update_product_quantity(self, product_id, quantity):
        product = ProductModel.objects.filter(
            id=product_id, status=ProductStatusType.publish.value).first()
        if not product:
            return False

        # Clamp quantity between 1 and stock
        quantity = max(1, min(int(quantity), product.stock))

        for item in self._cart['items']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                self.save()
                return True

        # If product not in cart, add it
        if quantity > 0:
            self._cart['items'].append(
                {'product_id': product_id, 'quantity': quantity})
            self.save()
            return True

        return False

    def remove_product(self, product_id):
        initial_len = len(self._cart['items'])
        self._cart['items'] = [item for item in self._cart['items']
                               if item['product_id'] != product_id]
        if len(self._cart['items']) != initial_len:
            self.save()
            return True
        return False

    def clear(self):
        self._cart = self.session['cart'] = {'items': []}
        self.save()

    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        self.total_payment_price = 0
        cart_items = []
        product_ids = [int(item['product_id']) for item in self._cart['items']]
        products = ProductModel.objects.filter(
            id__in=product_ids, status=ProductStatusType.publish.value)
        product_map = {product.id: product for product in products}

        for item in self._cart['items']:
            product = product_map.get(int(item['product_id']))
            if not product:
                continue  # skip missing/unpublished products

            quantity = item['quantity']
            total_price = quantity * product.get_price()
            self.total_payment_price += total_price

            cart_items.append({
                'product_obj': product,
                'product_id': product.id,
                'quantity': quantity,
                'total_price': total_price
            })

        return cart_items

    def get_total_payment_amount(self):
        return self.total_payment_price

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self._cart['items'])

    def __len__(self):
        return len(self._cart['items'])

    def save(self):
        self.session.modified = True
