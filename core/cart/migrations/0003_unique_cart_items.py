from django.db import migrations, models
from django.db.models import Count, Min, Sum


def merge_duplicate_cart_data(apps, schema_editor):
    Cart = apps.get_model("cart", "CartModel")
    CartItem = apps.get_model("cart", "CartItemModel")
    db = schema_editor.connection.alias

    # Collapse duplicate rows within every cart first. The old schema had no
    # uniqueness constraint, so get_or_create() could create duplicates during
    # concurrent requests.
    cart_ids = Cart.objects.using(db).order_by("pk").values_list("pk", flat=True)
    for cart_id in cart_ids.iterator(chunk_size=500):
        duplicate_products = list(
            CartItem.objects.using(db)
            .filter(cart_id=cart_id)
            .values("product_id")
            .annotate(total_quantity=Sum("quantity"), row_count=Count("pk"), keep_id=Min("pk"))
            .filter(row_count__gt=1)
        )
        for group in duplicate_products:
            CartItem.objects.using(db).filter(pk=group["keep_id"]).update(
                quantity=group["total_quantity"]
            )
            CartItem.objects.using(db).filter(
                cart_id=cart_id, product_id=group["product_id"]
            ).exclude(pk=group["keep_id"]).delete()

    # Retain the oldest cart for each user and move or add its items to it.
    # Materialize IDs before deletion so SQLite and PostgreSQL cursor iteration
    # are both safe while the same table is being modified.
    duplicate_user_ids = (
        Cart.objects.using(db)
        .order_by()
        .values("user_id")
        .annotate(cart_count=Count("pk"))
        .filter(cart_count__gt=1)
        .values_list("user_id", flat=True)
    )
    for user_id in list(duplicate_user_ids):
        carts = list(
            Cart.objects.using(db).filter(user_id=user_id).order_by("pk")
        )
        if len(carts) < 2:
            continue
        primary = carts[0]
        for duplicate in carts[1:]:
            items = list(CartItem.objects.using(db).filter(cart_id=duplicate.pk))
            for item in items:
                existing = CartItem.objects.using(db).filter(
                    cart_id=primary.pk, product_id=item.product_id
                ).first()
                if existing:
                    existing.quantity += item.quantity
                    existing.save(update_fields=["quantity"])
                    item.delete()
                else:
                    item.cart_id = primary.pk
                    item.save(update_fields=["cart"])
            duplicate.delete()


class Migration(migrations.Migration):
    dependencies = [("cart", "0002_alter_cartitemmodel_cart")]

    operations = [
        # Merging cart data cannot be exactly reversed: a combined quantity
        # does not retain which quantity came from each legacy row. Reversing
        # removes the constraints but intentionally leaves the consolidated data.
        migrations.RunPython(merge_duplicate_cart_data, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="cartmodel",
            constraint=models.UniqueConstraint(fields=("user",), name="unique_cart_per_user"),
        ),
        migrations.AddConstraint(
            model_name="cartitemmodel",
            constraint=models.UniqueConstraint(fields=("cart", "product"), name="unique_product_per_cart"),
        ),
    ]
