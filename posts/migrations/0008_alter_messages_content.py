# Generated by Django 4.1.7 on 2023-09-09 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_alter_messages_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='content',
            field=models.TextField(db_column='content CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci'),
        ),
    ]