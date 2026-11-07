# edubridge/forms.py

from django import forms

from edubridge.accounts.models import StudyMaterial

class SignupForm(forms.Form):
    role_choices = [
        ('student', 'Student'),
        ('alumni', 'Alumni'),
        ('teacher', 'Teacher'),
    ]
    role = forms.ChoiceField(choices=role_choices, required=True)
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    semester = forms.CharField(max_length=50, required=True)
    admission_number = forms.CharField(max_length=50, required=True)

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['subject', 'module', 'semester', 'description', 'file']

