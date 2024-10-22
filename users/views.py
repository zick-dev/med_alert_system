from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Profile  # Import Profile from models.py
from .forms import PatientRegisterForm, DoctorRegisterForm
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import datetime
from django.contrib.auth.views import LoginView
from .models import TestResult, Appointment
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def approve_doctors_view(request):
    unapproved_doctors = Profile.objects.filter(role='doctor', approved=False)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.profile.approved = True
        user.is_active = True
        user.save()

        messages.success(request, f'Doctor {user.username} has been approved.')

    return render(request, 'admin/approve_doctors.html', {'unapproved_doctors': unapproved_doctors})


# Login View for All Users (Patients, Doctors, Admin)

def login_view(request):
    if request.method == 'POST':
        email_or_username = request.POST['username']
        password = request.POST['password']

        # Try authenticating with email and password for non-admin users
        try:
            # If user is admin (logging in with username)
            user = authenticate(request, username=email_or_username, password=password)

            # If not admin, check if it's a doctor or patient (logging in with email)
            if user is None:
                user = authenticate(request, username=Profile.objects.get(user__email=email_or_username).user.username,
                                    password=password)

            # If user authenticated
            if user is not None:
                login(request, user)

                # Redirect based on role
                if user.profile.role == 'admin':
                    return redirect('admin_dashboard')
                elif user.profile.role == 'doctor':
                    return redirect('doctor_dashboard')
                else:
                    return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('login')

        except Profile.DoesNotExist:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'users/login.html')  # Replace with your actual login template


# Replace with your actual login template
# Register View for Patients
def register_patient_view(request):
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')

            # Check if a user with the same email already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return redirect('register-patient')

            try:
                # Save the form (create user)
                user = form.save()

                # Create the Profile instance and link it to the user
                Profile.objects.create(user=user, role='patient')

                # Log the user in after registration
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=email, password=raw_password)
                if user:
                    login(request, user)
                    messages.success(request, 'Your account has been created! You are now logged in.')
                    return redirect('patient-dashboard')
                else:
                    messages.error(request, 'Authentication failed.')
                    return redirect('login')

            except IntegrityError:
                messages.error(request, 'There was an issue creating your account. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = PatientRegisterForm()

    return render(request, 'users/register_patient.html', {'form': form})
# Register View for Doctors
def register_doctor_view(request):
    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')

            # Check if a user with the same email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return redirect('register-doctor')

            try:
                # Create the user with email as username, inactive until approved by admin
                user = User.objects.create_user(username=email, email=email, password=raw_password)
                user.is_active = False  # Doctor is inactive until admin approval
                user.save()

                # Create a corresponding profile for the doctor with approved=False
                Profile.objects.create(user=user, role='doctor', approved=False)

                # Notify the admin about the new doctor registration
                send_mail(
                    'New Doctor Registration',
                    'A new doctor has registered and requires approval.',
                    'noreply@medalertsystem.com',
                    ['ijay.globals@gmail.com'],  # Replace with the admin's email
                    fail_silently=False,
                )

                messages.success(request, 'Your account has been created and is awaiting admin approval.')
                return redirect('login')
            except IntegrityError:
                messages.error(request, 'There was an issue creating your account. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorRegisterForm()

    return render(request, 'users/register_doctor.html', {'form': form})



@login_required
def patient_dashboard(request):
    # Get the profile associated with the current user
    try:
        profile = Profile.objects.get(user=request.user)  # Ensure Profile model is linked to User
    except Profile.DoesNotExist:
        # Handle case where the profile doesn't exist, e.g., show an error message or redirect
        return redirect('some_error_page')  # Replace with an actual error page if needed

    # Check if the logged-in user is a patient
    if profile.role != 'patient':
        return redirect('some_error_page')  # Restrict access for non-patients

    # Get the patient's test results and upcoming appointments
    today = datetime.now().date()  # Get today's date
    test_results = TestResult.objects.filter(patient=profile)  # Use Profile (not request.user)
    upcoming_appointments = Appointment.objects.filter(patient=profile, date__gte=today).order_by('date')

    return render(request, 'users/patient_dashboard.html', {
        'test_results': test_results,
        'upcoming_appointments': upcoming_appointments,
    })



def book_appointment_view(request):
    # Logic for booking an appointment goes here
    return render(request, 'users/book_appointment.html')


@login_required
def doctor_dashboard(request):
    return render(request, 'users/doctor_dashboard.html')


# Ensure only admins can access this view
@login_required
@staff_member_required
def admin_dashboard(request):
    # Count patients and doctors for chart data
    total_patients = Profile.objects.filter(role='patient').count()
    total_doctors = Profile.objects.filter(role='doctor', approved=True).count()

    # For pie and bar charts, count patients in/out by status
    patients_in = Profile.objects.filter(role='patient', approved=True).count()
    patients_out = Profile.objects.filter(role='patient', approved=False).count()

    return render(request, 'admin/admin_dashboard.html', {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'patients_in': patients_in,
        'patients_out': patients_out,
    })
