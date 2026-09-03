from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Patient
from .forms import PatientForm

class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.created_by == self.request.user


class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 10

    def get_queryset(self):
        qs = Patient.objects.filter(created_by=self.request.user, is_active=True)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(patient_id__icontains=query) |
                Q(phone_number__icontains=query)
            )
        return qs


class PatientDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class PatientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'


class PatientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patients:list')

    def form_valid(self, form):
        # Soft delete instead of removing the row
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return redirect(self.success_url)