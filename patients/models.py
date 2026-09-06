from django.db import models, transaction, IntegrityError
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import uuid


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'), ('UNK', 'Unknown'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'), ('married', 'Married'),
        ('divorced', 'Divorced'), ('widowed', 'Widowed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # PRN — the system-wide identifier used across ALL clinics
    prn = models.CharField(max_length=20, unique=True, editable=False, blank=True)

    # National ID is the real-world dedup key: prevents Clinic B from
    # accidentally creating a second file for someone already registered at Clinic A
    national_id = models.CharField(max_length=50, unique=True, help_text="National ID or passport number")

    # Which clinic + staff member originally opened this file (for audit only —
    # does NOT restrict which clinic can view/use the record)
    registered_at_clinic = models.ForeignKey('clinics.Clinic', on_delete=models.PROTECT, related_name='patients_registered')
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='patients_registered')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)

    # Contact
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    # Medical
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, default='UNK')
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    past_surgeries = models.TextField(blank=True)
    family_medical_history = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)  # soft-delete flag

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.prn})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def save(self, *args, **kwargs):
        if not self.prn:
            self._generate_prn()
        super().save(*args, **kwargs)

    def _generate_prn(self):
        """
        Generates a PRN like SC-2026-000482.
        Uses a locked query on the last PRN for the current year to get the
        next sequence number, retrying on rare race-condition collisions.
        """
        year = timezone.now().year
        prefix = f"SC-{year}-"
        max_attempts = 5

        for attempt in range(max_attempts):
            with transaction.atomic():
                last = (
                    Patient.objects.select_for_update()
                    .filter(prn__startswith=prefix)
                    .order_by('-prn')
                    .first()
                )
                if last:
                    last_seq = int(last.prn.split('-')[-1])
                else:
                    last_seq = 0
                next_seq = last_seq + 1
                candidate = f"{prefix}{next_seq:06d}"

                if not Patient.objects.filter(prn=candidate).exists():
                    self.prn = candidate
                    return
        raise IntegrityError("Could not generate a unique PRN after several attempts.")


class Visit(models.Model):
    """
    One row per clinic encounter. This is how the system 'remembers' a
    patient across Clinic A, B, C — same Patient, many Visits.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.PROTECT, related_name='visits')
    attended_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='visits_attended')

    visit_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.patient.full_name} @ {self.clinic.code} on {self.visit_date:%Y-%m-%d}"