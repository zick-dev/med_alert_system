from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import Profile, Appointment
from django.db.models import Count
from django.utils.html import format_html


class CustomAdminSite(admin.AdminSite):
    site_header = 'Medical Alert System Administration'
    site_title = 'Admin Dashboard'
    index_title = 'Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-dashboard/', self.admin_view(self.custom_dashboard), name="custom-dashboard")
        ]
        return custom_urls + urls

    def custom_dashboard(self, request):
        # Get data for charts
        patients_in = Profile.objects.filter(role='patient', approved=True).count()
        patients_out = Profile.objects.filter(role='patient', approved=False).count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        pending_appointments = Appointment.objects.filter(status='pending').count()

        context = {
            'patients_in': patients_in,
            'patients_out': patients_out,
            'completed_appointments': completed_appointments,
            'pending_appointments': pending_appointments,
        }
        return render(request, 'admin/index.html', context)

# Create an instance of CustomAdminSite
custom_admin_site = CustomAdminSite(name='custom_admin')
# Register your models with the custom admin site
@admin.register(Profile, site=custom_admin_site)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'approved')

@admin.register(Appointment, site=custom_admin_site)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'status')