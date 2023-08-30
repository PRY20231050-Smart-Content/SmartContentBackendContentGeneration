from django.db import models

# Create your models here.
class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
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