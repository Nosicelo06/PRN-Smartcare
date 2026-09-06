from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Patient
        exclude = ['id', 'prn', 'registered_by', 'created_at', 'updated_at', 'is_active']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'allergies': forms.Textarea(attrs={'rows': 2}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 2}),
            'current_medications': forms.Textarea(attrs={'rows': 2}),
            'past_surgeries': forms.Textarea(attrs={'rows': 2}),
            'family_medical_history': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_national_id(self):
        national_id = self.cleaned_data['national_id']
        qs = Patient.objects.filter(national_id=national_id)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            existing = qs.first()
            raise forms.ValidationError(
                f"A patient with this National ID already exists (PRN: {existing.prn}). "
                f"Please search for their existing file instead of creating a new one."
            )
        return national_id