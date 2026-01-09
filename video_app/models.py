from django.db import models

class Video(models.Model):

    TYPE_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    original_file = models.FileField(upload_to="videos/originals/")
    thumbnail = models.ImageField(blank=True,null=True)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=15, choices=TYPE_CHOICES, default='pending')

    def __str__(self):
        return self.title
