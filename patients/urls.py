from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.PatientListView.as_view(), name='list'),
    path('register/', views.PatientCreateView.as_view(), name='register_patient'),
    path('<uuid:pk>/', views.PatientDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.PatientUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.PatientDeleteView.as_view(), name='delete'),
]