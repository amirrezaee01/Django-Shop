import os
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from django.conf import settings

from faker import Faker

from shop.models import ProductModel, ProductCategoryModel, ProductStatusType
from accounts.models import User


class Command(BaseCommand):
    help = 'Generate fake Persian products with images, categories, and users.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='تعداد محصولات جعلی برای تولید')

    def handle(self, *args, **options):  # ✅ Correct level
        fake = Faker(locale='fa_IR')  # Persian content
        count = options['count']

        users = list(User.objects.all())
        categories = list(ProductCategoryModel.objects.all())
        image_folder = os.path.join(settings.BASE_DIR, 'shop', 'management', 'commands', 'images')
        image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not users:
            self.stdout.write(self.style.ERROR('No users found in the database.'))
            return
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found in the database.'))
            return
        if not image_files:
            self.stdout.write(self.style.ERROR(f'No image files found in: {image_folder}'))
            return

        created_count = 0

        for _ in range(count):
            title = fake.unique.sentence(nb_words=3).replace('.', '')
            base_slug = slugify(title, allow_unicode=True)
            slug = base_slug

            suffix = 1
            while ProductModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1

            product = ProductModel.objects.create(
                user=random.choice(users),
                title=title,
                slug=slug,
                description=fake.paragraph(nb_sentences=4),
                brief_description=fake.sentence(nb_words=10),
                stock=random.randint(1, 100),
                price=Decimal(random.randint(10000, 500000)),
                discount_percent=random.randint(0, 50),
                status=random.choice([
                    ProductStatusType.publish,
                    ProductStatusType.draft
                ])
            )

            selected_categories = random.sample(categories, k=random.randint(1, min(3, len(categories))))
            product.category.set(selected_categories)

            selected_image = random.choice(image_files)
            image_path = os.path.join(image_folder, selected_image)

            with open(image_path, 'rb') as img_file:
                product.image.save(f"{slug}.jpg", File(img_file), save=True)

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} fake products."))
