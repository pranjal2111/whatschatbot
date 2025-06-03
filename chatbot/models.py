from django.db import models

# Create your models here.
class MessageLog(models.Model):
    sender = models.CharField(max_length=50)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender