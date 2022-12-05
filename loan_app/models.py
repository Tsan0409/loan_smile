from django.db import models

# Create your models here.


# サンプル
class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
