from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Patient
        exclude = ['id', 'created_by', 'patient_id', 'created_at', 'updated_at', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'allergies': forms.Textarea(attrs={'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 2}),
            'current_medications': forms.Textarea(attrs={'rows': 2}),
            'past_surgeries': forms.Textarea(attrs={'rows': 2}),
            'family_medical_history': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }