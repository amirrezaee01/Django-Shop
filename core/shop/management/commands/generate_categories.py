from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
from shop.models import ProductCategoryModel

class Command(BaseCommand):
    help = 'Generate fake product categories (Persian only)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=10,
            help='Number of categories to create (default: 10)'
        )

    def handle(self, *args, **options):
        fake = Faker(locale='fa_IR')  # Persian locale

        created_count = 0
        total_to_create = options['count']

        self.stdout.write(f'در حال تولید {total_to_create} دسته‌بندی محصول...')

        while created_count < total_to_create:
            # Generate Persian title
            title = fake.unique.word()

            # Generate Persian slug with allow_unicode=True
            base_slug = slugify(title, allow_unicode=True)
            slug = base_slug

            # Ensure slug uniqueness
            suffix = 1
            while ProductCategoryModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1

            # Create the category
            ProductCategoryModel.objects.create(title=title, slug=slug)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'#{created_count}: {title} (slug: {slug})'))

        self.stdout.write(self.style.SUCCESS(f'با موفقیت {created_count} دسته‌بندی ساخته شد.'))
