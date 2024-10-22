from django.urls import path
from . import views
from .views import patient_dashboard, book_appointment_view, approve_doctors_view, admin_dashboard
from django.contrib.auth import views as auth_views
from users.admin import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    # Login view for all roles (patients, doctors, and admin)
    path('', views.login_view, name='login'),
    path('patient-dashboard/', patient_dashboard, name='patient-dashboard'),
    # Registration view for patients
    path('register-patient/', views.register_patient_view, name='register-patient'),

    # Separate registration view for doctors
    path('register-doctor/', views.register_doctor_view, name='register-doctor'),

    # Dashboard views for different roles
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor-dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin-dashboard'),  # Ensure this line is present
    path('approve-doctors/', approve_doctors_view, name='approve-doctors'),  # Ensure this line is present
    path('book-appointment/', book_appointment_view, name='book-appointment'),  # Ensure this line is present

    # Optional logout view (Django’s built-in)
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]
