from django.db import models

# Create your models here.
class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(db_collation='utf8mb4_unicode_ci')
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)  # Allow null and blank values
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    business_id = models.IntegerField()
    deleted_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.id} - {self.content}"


class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField()
    post = models.ForeignKey('Posts', on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    chosen = models.CharField(max_length=3, choices=CHOICES)
    selectable = models.CharField(max_length=3, choices=CHOICES)

    def __str__(self):
        return f"Message {self.id}"

from django.db import models

class PostDetail(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey('Posts', on_delete=models.CASCADE)
    post_ocassion = models.CharField(max_length=255)
    post_promo = models.CharField(max_length=255)
    post_objective = models.CharField(max_length=255)
    POST_LANGUAGE_CHOICES = [
        ('Spanish', 'Spanish'),
        ('English', 'English'),
    ]
    post_language = models.CharField(max_length=10, choices=POST_LANGUAGE_CHOICES)
    POST_USE_EMOJIS_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    post_use_emojis = models.CharField(max_length=3, choices=POST_USE_EMOJIS_CHOICES)
    post_keywords = models.JSONField()
    post_creativity = models.FloatField()
    POST_COPY_SIZE_CHOICES = [
        ('Short', 'Short'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    post_copy_size = models.CharField(max_length=10, choices=POST_COPY_SIZE_CHOICES)
    POST_INCLUDE_BUSINESS_INFO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    post_include_business_info = models.CharField(max_length=3, choices=POST_INCLUDE_BUSINESS_INFO_CHOICES)
    products_to_include = models.JSONField()
    products_to_include_names = models.JSONField()

    def __str__(self):
        return f"Post Detail {self.id}"
