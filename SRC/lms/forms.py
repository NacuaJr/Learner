from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CourseInfo, CourseDetails

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class TrainerRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class CourseInfoForm(forms.ModelForm):
    class Meta:
        model = CourseInfo
        fields = ['course_name', 'category']
        widgets = {
            'course_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class CourseDetailsForm(forms.ModelForm):
    class Meta:
        model = CourseDetails
        fields = ['course_image', 'course_desc']
        widgets = {
            'course_desc': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }