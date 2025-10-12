from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
from shop.models import ProductCategoryModel


class Command(BaseCommand):
    help = "Generate fake Persian product categories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=10, help="Number of categories to create"
        )

    def handle(self, *args, **options):
        fake = Faker(locale="fa_IR")
        count = options["count"]
        created_count = 0

        for _ in range(count):
            title = fake.unique.word()
            base_slug = slugify(title, allow_unicode=True)
            slug = base_slug

            suffix = 1
            while ProductCategoryModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1

            ProductCategoryModel.objects.create(title=title, slug=slug)
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} categories.")
        )
