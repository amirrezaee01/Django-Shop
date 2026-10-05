from django.db import migrations, models


def remove_duplicate_wishlist_items(apps, schema_editor):
    Wishlist = apps.get_model("shop", "WishlistProductModel")
    db = schema_editor.connection.alias
    seen = set()
    duplicate_ids = []
    for item in Wishlist.objects.using(db).order_by("pk").iterator():
        key = (item.user_id, item.product_id)
        if key in seen:
            duplicate_ids.append(item.pk)
        else:
            seen.add(key)
    if duplicate_ids:
        Wishlist.objects.using(db).filter(pk__in=duplicate_ids).delete()


class Migration(migrations.Migration):
    dependencies = [("shop", "0007_alter_productimagemodel_options_and_more")]

    operations = [
        migrations.RunPython(remove_duplicate_wishlist_items, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="wishlistproductmodel",
            constraint=models.UniqueConstraint(fields=("user", "product"), name="unique_wishlist_product_per_user"),
        ),
    ]
