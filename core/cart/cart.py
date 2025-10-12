from shop.models import ProductModel, ProductStatusType
from cart.models import *


class CartSession:
    def __init__(self, session):
        self.session = session
        self._cart = self.session.setdefault("cart", {"items": []})
        self.total_payment_price = 0  # instance variable, not class variable

    # -------------------------
    # ADD PRODUCT (incremental)
    # -------------------------
    def add_quantity(self, product_id, add_qty):
        """Incrementally add quantity to a cart item, respecting stock."""
        try:
            add_qty = int(add_qty)
        except (TypeError, ValueError):
            return False, {
                "code": "invalid_quantity",
                "message": "تعداد نامعتبر است.",
                "current_quantity": 0,
                "stock": 0,
            }
        if add_qty < 1:
            return False, {
                "code": "invalid_quantity",
                "message": "حداقل تعداد باید ۱ باشد.",
                "current_quantity": 0,
                "stock": 0,
            }

        product = ProductModel.objects.filter(
            id=product_id, status=ProductStatusType.publish.value
        ).first()
        if not product:
            return False, {
                "code": "not_found",
                "message": "محصول یافت نشد.",
                "current_quantity": 0,
                "stock": 0,
            }

        stock = int(product.stock)

        # find existing item
        item = next(
            (i for i in self._cart["items"] if i["product_id"] == product_id), None
        )
        current_qty = int(item["quantity"]) if item else 0

        # already at max
        if current_qty >= stock:
            return False, {
                "code": "at_max",
                "message": "شما قبلاً حداکثر موجودی این محصول را در سبد خرید دارید.",
                "current_quantity": current_qty,
                "stock": stock,
            }

        new_qty = current_qty + add_qty

        # would exceed stock
        if new_qty > stock:
            return False, {
                "code": "exceeds_stock",
                "message": f"امکان افزودن {add_qty} عدد وجود ندارد. فقط {stock - current_qty} عدد باقی مانده است.",
                "current_quantity": current_qty,
                "stock": stock,
            }

        # apply change
        if item:
            item["quantity"] = new_qty
        else:
            self._cart["items"].append({"product_id": product_id, "quantity": add_qty})
        self.save()

        return True, {
            "code": "added",
            "message": f"{add_qty} عدد به سبد خرید افزوده شد. مجموع این محصول: {new_qty}.",
            "current_quantity": new_qty,
            "stock": stock,
        }

    def add_product(self, product_id):
        """Shortcut for +1 (grid page use)."""
        success, info = self.add_quantity(product_id, 1)
        return success

    # -------------------------
    # UPDATE ABSOLUTE QUANTITY
    # -------------------------
    def update_product_quantity(self, product_id, quantity):
        """Set product quantity directly (used in cart summary)."""
        product = ProductModel.objects.filter(
            id=product_id, status=ProductStatusType.publish.value
        ).first()
        if not product:
            return False

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return False

        # Clamp quantity between 1 and stock
        quantity = max(1, min(quantity, product.stock))

        for item in self._cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                self.save()
                return True

        # If product not in cart, add it
        if quantity > 0:
            self._cart["items"].append({"product_id": product_id, "quantity": quantity})
            self.save()
            return True

        return False

    # -------------------------
    # REMOVE / CLEAR
    # -------------------------
    def remove_product(self, product_id):
        initial_len = len(self._cart["items"])
        self._cart["items"] = [
            item for item in self._cart["items"] if item["product_id"] != product_id
        ]
        if len(self._cart["items"]) != initial_len:
            self.save()
            return True
        return False

    def clear(self):
        self._cart = self.session["cart"] = {"items": []}
        self.save()

    # -------------------------
    # GETTERS
    # -------------------------
    def get_cart_dict(self):
        return self._cart

    def get_cart_items(self):
        self.total_payment_price = 0
        cart_items = []
        product_ids = [int(item["product_id"]) for item in self._cart["items"]]
        products = ProductModel.objects.filter(
            id__in=product_ids, status=ProductStatusType.publish.value
        )
        product_map = {product.id: product for product in products}

        for item in self._cart["items"]:
            product = product_map.get(int(item["product_id"]))
            if not product:
                continue  # skip missing/unpublished products

            quantity = item["quantity"]
            total_price = quantity * product.get_price()
            self.total_payment_price += total_price

            cart_items.append(
                {
                    "product_obj": product,
                    "product_id": product.id,
                    "quantity": quantity,
                    "total_price": total_price,
                }
            )

        return cart_items

    def get_total_payment_amount(self):
        return self.total_payment_price

    def get_total_quantity(self):
        return sum(item["quantity"] for item in self._cart["items"])

    def __len__(self):
        return len(self._cart["items"])

    def save(self):
        self.session.modified = True

    def sync_cart_items_from_db(self, user):

        cart, created = CartModel.objects.get_or_create(user=user)
        cart_items = CartItemModel.objects.filter(cart=cart)

        for cart_item in cart_items:
            for item in self._cart["items"]:
                if str(cart_item.product.id) == item["product_id"]:
                    cart_item.quantity = item["quantity"]
                    cart_item.save()
                    break
            else:
                new_item = {
                    "product_id": str(cart_item.product.id),
                    "quantity": cart_item.quantity,
                }
                self._cart["items"].append(new_item)
        self.merge_session_cart_in_db(user)
        self.save()

    def merge_session_cart_in_db(self, user):
        cart, created = CartModel.objects.get_or_create(user=user)

        for item in self._cart["items"]:
            product_obj = ProductModel.objects.get(
                id=item["product_id"], status=ProductStatusType.publish.value
            )

            cart_item, created = CartItemModel.objects.get_or_create(
                cart=cart, product=product_obj
            )
            cart_item.quantity = item["quantity"]
            cart_item.save()
        session_product_ids = [item["product_id"] for item in self._cart["items"]]
        CartItemModel.objects.filter(cart=cart).exclude(
            product__id__in=session_product_ids
        ).delete()
