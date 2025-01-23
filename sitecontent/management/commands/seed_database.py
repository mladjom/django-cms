from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth.models import User
from sitecontent.models import Category, Tag, Post, Page
from faker import Faker

class Command(BaseCommand):
    help = 'Seeds the database with sample data.'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create sample categories
        categories = []
        for _ in range(5):
            category = Category.objects.create(
                name=fake.word(),
                slug=slugify(fake.word()),
                meta_title=fake.sentence(),
                meta_description=fake.sentence(),
            )
            categories.append(category)
            self.stdout.write(self.style.SUCCESS(f'Category "{category.name}" created.'))

        # Create sample tags
        tags = []
        for _ in range(10):
            tag = Tag.objects.create(
                name=fake.word(),
                slug=slugify(fake.word()),
                meta_title=fake.sentence(),
                meta_description=fake.sentence(),
            )
            tags.append(tag)
            self.stdout.write(self.style.SUCCESS(f'Tag "{tag.name}" created.'))

        # Create a sample user (author)
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
        )
        self.stdout.write(self.style.SUCCESS(f'User "{user.username}" created.'))

        # Create sample posts
        for _ in range(20):
            post = Post.objects.create(
                title=fake.sentence(),
                slug=slugify(fake.sentence()),
                content=fake.paragraph(),
                excerpt=fake.text(max_nb_chars=200),
                author=user,
                category=categories[fake.random_int(0, len(categories) - 1)],
                status=fake.random_element([0, 1]),
                is_featured=fake.boolean(),
                meta_title=fake.sentence(),
                meta_description=fake.sentence(),
            )
            post.tags.set(fake.random_elements(tags, length=fake.random_int(1, 5)))
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Post "{post.title}" created.'))

        # Create sample pages
        for _ in range(5):
            page = Page.objects.create(
                title=fake.sentence(),
                slug=slugify(fake.sentence()),
                content=fake.paragraph(),
                meta_title=fake.sentence(),
                meta_description=fake.sentence(),
            )
            self.stdout.write(self.style.SUCCESS(f'Page "{page.title}" created.'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
