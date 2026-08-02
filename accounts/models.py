from django.db import models

# Create your models here.

class Patient(models.Model):
    Id_number = models.CharField(max_length=13, unique=True)
    prn_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    surname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=15)
    Address = models.TextField()
    def _str_(self):
        return f"{self.first_name}{self.surname}".strip()

