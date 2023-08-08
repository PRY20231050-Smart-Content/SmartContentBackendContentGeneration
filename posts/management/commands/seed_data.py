from django.core.management.base import BaseCommand
from faker import Faker
from posts.models import Posts
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed initial data into the Posts model'

    def handle(self, *args, **options):
        fake = Faker()

        for _ in range(10):  # You can adjust the number of posts to create
            content = fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
            image_url = fake.image_url()
            published_at = fake.date_time_this_year()
            status = random.choice(['draft', 'published'])
            business_id = fake.random_int(min=1, max=10)  # Adjust as needed

            Posts.objects.create(
                content=content,
                image_url=image_url,
                published_at=published_at,
                status=status,
                business_id=business_id,
            )

        self.stdout.write(self.style.SUCCESS('Data successfully seeded!'))
