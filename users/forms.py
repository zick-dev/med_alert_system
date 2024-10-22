from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PatientRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(PatientRegisterForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['full_name']
        if commit:
            user.save()
            user.profile.role = 'patient'
            user.profile.save()
        return user
class DoctorRegisterForm(UserCreationForm):
    tag_number = forms.CharField(max_length=50, required=True, help_text='Enter your doctor tag number.')

    class Meta:
        model = User
        fields = ['username', 'email', 'tag_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super(DoctorRegisterForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['full_name']
        if commit:
            user.save()
            user.profile.role = 'doctor'
            user.profile.save()
        return user