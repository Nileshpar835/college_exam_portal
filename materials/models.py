from django.db import models
from django.conf import settings

class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file_url = models.URLField(null=True, blank=True)
    external_link = models.URLField(null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
