from django.db import models

# Create your models here.
class Clinic(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, unique=True, help_text="Short code e.g. CLN-A")
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"