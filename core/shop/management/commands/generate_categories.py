from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
from shop.models import ProductCategoryModel

class Command(BaseCommand):
    help = 'Generate fake product categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=10,
            help='Number of categories to create (default: 10)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        created_count = 0
        total_to_create = options['count']

        self.stdout.write(f'Starting generation of {total_to_create} product categories...')

        while created_count < total_to_create:
            # Generate a fake title
            title = fake.unique.word().capitalize()
            base_slug = slugify(title)
            slug = base_slug

            # Ensure slug uniqueness in DB by appending suffix if needed
            suffix = 1
            while ProductCategoryModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1

            # Create the category
            ProductCategoryModel.objects.create(title=title, slug=slug)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created category #{created_count}: {title} (slug: {slug})'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} categories.'))
