from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, TrainerRegisterForm, CourseInfoForm, CourseDetailsForm
from .models import CourseInfo, CourseDetails, TrainerRegistration

def home(request):
    return render(request, 'lms/home.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('lms:home')
    else:
        form = UserRegisterForm()
    return render(request, 'lms/auth/user_register.html', {'form': form})

def trainer_register(request):
    if request.method == 'POST':
        form = TrainerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            TrainerRegistration.objects.create(user=user)
            login(request, user)
            messages.info(request, 'Trainer account created! Waiting for admin approval.')
            return redirect('lms:home')
    else:
        form = TrainerRegisterForm()
    return render(request, 'lms/auth/trainer_register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {username}!')
            return redirect('lms:course_list')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'lms/auth/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('lms:home')

@login_required
def become_trainer(request):
    if request.method == 'POST':
        user = request.user
        user.is_staff = True
        user.save()
        TrainerRegistration.objects.create(user=user)
        messages.success(request, 'Trainer request submitted for approval!')
        return redirect('lms:home')
    return render(request, 'lms/auth/become_trainer.html')

# Course Views
@login_required
def course_list(request):
    courses = CourseInfo.objects.filter(user=request.user)
    return render(request, 'lms/courses/course_list.html', {'courses': courses})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseInfoForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            CourseDetails.objects.create(course_info=course, user=request.user)
            messages.success(request, 'Course created successfully!')
            return redirect('lms:course_details', course_slug=course.slug)
    else:
        form = CourseInfoForm()
    return render(request, 'lms/courses/course_form.html', {'form': form, 'title': 'Create Course'})

@login_required
def course_details(request, course_slug):
    course = get_object_or_404(CourseInfo, slug=course_slug, user=request.user)
    details = get_object_or_404(CourseDetails, course_info=course, user=request.user)
    
    if request.method == 'POST':
        form = CourseDetailsForm(request.POST, request.FILES, instance=details)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course details updated!')
            return redirect('lms:course_details', course_slug=course.slug)
    else:
        form = CourseDetailsForm(instance=details)
    
    return render(request, 'lms/courses/course_details.html', {
        'course': course,
        'form': form,
        'details': details
    })

@login_required
def course_update(request, course_slug):
    course = get_object_or_404(CourseInfo, slug=course_slug, user=request.user)
    
    if request.method == 'POST':
        form = CourseInfoForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('lms:course_details', course_slug=course.slug)
    else:
        form = CourseInfoForm(instance=course)
    
    return render(request, 'lms/courses/course_form.html', {
        'form': form,
        'title': 'Update Course',
        'course': course
    })

@login_required
def course_delete(request, course_slug):
    course = get_object_or_404(CourseInfo, slug=course_slug, user=request.user)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('lms:course_list')
    
    return render(request, 'lms/courses/course_confirm_delete.html', {'course': course})