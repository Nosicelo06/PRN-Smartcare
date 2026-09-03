from django.db import models
from django.conf import settings
from django.urls import reverse
import uuid


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('UNK', 'Unknown'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]

    # Ownership / record keeping
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients'
    )
    patient_id = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)

    # Contact info
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    # Medical info
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, default='UNK')
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    allergies = models.TextField(blank=True, help_text="Known allergies, comma-separated")
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    past_surgeries = models.TextField(blank=True)
    family_medical_history = models.TextField(blank=True)

    # Insurance / admin
    insurance_provider = models.CharField(max_length=150, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)  # soft-delete flag

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = f"PT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"

    def get_absolute_url(self):
        return reverse('patients:detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )