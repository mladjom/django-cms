# Generated by Django 5.1.5 on 2025-01-30 07:56

import cms.models.featured_image
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Category Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
                ('meta_title', models.CharField(blank=True, max_length=200, verbose_name='Meta Title')),
                ('meta_description', models.TextField(blank=True, max_length=160, verbose_name='Meta Description')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='View Count')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='Title')),
                ('slug', models.SlugField(max_length=250, unique=True, verbose_name='Slug')),
                ('content', models.TextField(verbose_name='Content')),
                ('meta_title', models.CharField(blank=True, max_length=200, verbose_name='Meta Title')),
                ('meta_description', models.TextField(blank=True, max_length=160, verbose_name='Meta Description')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='View Count')),
                ('status', models.IntegerField(choices=[(0, 'Draft'), (1, 'Published')], default=0, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Tag Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
                ('meta_title', models.CharField(blank=True, max_length=200, verbose_name='Meta Title')),
                ('meta_description', models.TextField(blank=True, max_length=160, verbose_name='Meta Description')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='View Count')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('featured_image', models.ImageField(blank=True, null=True, upload_to=cms.models.featured_image.image_upload_path, verbose_name='Featured Image')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='Title')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
                ('content', models.TextField(verbose_name='Content')),
                ('excerpt', models.TextField(blank=True, verbose_name='Excerpt')),
                ('meta_title', models.CharField(blank=True, max_length=200, verbose_name='Meta Title')),
                ('meta_description', models.TextField(blank=True, max_length=160, verbose_name='Meta Description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('status', models.IntegerField(choices=[(0, 'Draft'), (1, 'Published')], default=0, verbose_name='Status')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Is Featured')),
                ('view_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='View Count')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='cms.category', verbose_name='Category')),
                ('tags', models.ManyToManyField(related_name='posts', to='cms.tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
    ]
