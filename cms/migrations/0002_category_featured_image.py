# Generated by Django 5.1.5 on 2025-01-30 08:44

import cms.models.featured_image
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to=cms.models.featured_image.image_upload_path, verbose_name='Featured Image'),
        ),
    ]
