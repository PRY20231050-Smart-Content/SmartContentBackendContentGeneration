# Generated by Django 4.1.7 on 2023-08-30 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_sp_get_posts_20232908_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='image_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]