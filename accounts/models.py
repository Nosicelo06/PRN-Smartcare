from django.contrib.auth.models import user
from django.db import models

# Create your models here.
class StaffProfile(models.Model):
    user = models.oneTooneField(User, on_delete=models.CASCADE)

    surname = models.Charfield(max_length=100)
    cell_number = models.Charfield(max_length=15)

    ROLE_CHOICES = [
        ("Admin", "Administrator"),
        ("Receptionist", "Receptionist"),
        ("Doctor", "Doctor"),
        ("Nurse", "Nurse"),
        ("Pharmacist","Phamacist"),
    ]
    role = models.Charfield(max_length=20, choices=ROLE_CHOICES)