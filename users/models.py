from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    approved = models.BooleanField(default=False)  # New field to track approval for doctors

    def __str__(self):
        return f'{self.user.username} Profile'

class TestResult(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=50)  # e.g., 'pending', 'completed'
    result_details = models.TextField(blank=True, null=True)  # Optional field for detailed results

    def __str__(self):
        return f"{self.test_name} - {self.patient.username} ({self.date})"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    patient = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'}, related_name='appointments_as_patient')  # Ensure patient is a Profile with role 'patient'
    doctor = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'}, related_name='appointments_as_doctor')  # Ensure doctor is a Profile with role 'doctor'
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(blank=True, null=True)  # Optional field for appointment reason
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # New status field for appointment

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.username} on {self.date} at {self.time}"
