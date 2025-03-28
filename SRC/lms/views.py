from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, TrainerRegisterForm, CourseInfoForm, CourseDetailsForm
from .models import CourseInfo, CourseDetails, TrainerRegistration, Enrollment

def home(request):
    # Show all approved courses (filter out drafts if needed)
    courses = CourseInfo.objects.all()  # Or add filters like .filter(is_published=True)
    return render(request, 'lms/home.html', {'courses': courses})

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
            # Redirect to appropriate page based on user type
            if user.is_staff:
                return redirect('lms:course_list')
            return redirect('lms:home')
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
    if request.user.is_staff:
        courses = CourseInfo.objects.filter(user=request.user)
        return render(request, 'lms/courses/course_list.html', {'courses': courses})
    return redirect('lms:home')

@login_required
def course_create(request):
    if not request.user.is_staff:
        return redirect('lms:home')
        
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
    course = get_object_or_404(CourseInfo, slug=course_slug)
    details = get_object_or_404(CourseDetails, course_info=course)
    
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, 
            course=course
        ).exists()

    context = {
        'course': course,
        'details': details,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'lms/courses/course_details.html', context)

@login_required
def enroll_course(request, course_slug):
    course = get_object_or_404(CourseInfo, slug=course_slug)
    
    # Prevent instructors from enrolling in their own courses
    if request.user == course.user:
        messages.error(request, "You cannot enroll in your own course!")
        return redirect('lms:course_details', course_slug=course.slug)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course!')
    else:
        Enrollment.objects.create(user=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.course_name}!')
    
    return redirect('lms:course_details', course_slug=course.slug)


@login_required
def my_enrollments(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'lms/enrollments/my_enrollments.html', {'enrollments': enrollments})

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