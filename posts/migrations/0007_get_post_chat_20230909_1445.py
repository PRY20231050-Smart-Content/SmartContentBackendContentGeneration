# Generated by Django 4.1.7 on 2023-09-09 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_postdetail_products_to_include'),
    ]

    operations = [
        migrations.RunSQL("""
            DROP PROCEDURE IF EXISTS get_post_chat;

            CREATE PROCEDURE `get_post_chat`(p_post_id int)
            begin
                select pm.content, pm.chosen, pm.`role`, pm.created_at from posts_messages pm where pm.post_id = p_post_id;
            END
        """)]
