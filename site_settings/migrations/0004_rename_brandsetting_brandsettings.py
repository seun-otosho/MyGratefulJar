# Generated by Django 5.0.7 on 2024-07-13 03:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0003_brandsetting'),
        ('wagtailimages', '0026_delete_uploadedimage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BrandSetting',
            new_name='BrandSettings',
        ),
    ]
