from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.forms import ValidationError
from django.utils.text import slugify
from django.urls import reverse
# In lms/models.py
from django.db import models
from django.core.exceptions import ValidationError


def course_slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.course_name)

class TrainerRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.status else 'Pending'}"

class CourseInfo(models.Model):
    COURSE_CATEGORIES = (
        ('development', 'Development'),
        ('business', 'Business'),
        ('finance', 'Finance & Accounting'),
        ('it', 'IT & Software'),
        ('marketing', 'Marketing'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.CharField(max_length=100, choices=COURSE_CATEGORIES, default='development')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.course_name
    
    def get_absolute_url(self):
        return reverse('lms:course_details', kwargs={'course_slug': self.slug})

class CourseDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_info = models.OneToOneField(CourseInfo, on_delete=models.CASCADE)
    course_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    course_desc = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Details for {self.course_info.course_name}"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseInfo, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')

    def clean(self):
        # Prevent staff users from enrolling
        if self.user.is_staff:
            raise ValidationError("Staff members cannot enroll as learners")
        
        # Prevent self-enrollment
        if self.user == self.course.user:
            raise ValidationError("Instructors cannot enroll in their own courses")

    def save(self, *args, **kwargs):
        self.full_clean()  # Runs validation before saving
        super().save(*args, **kwargs)
pre_save.connect(course_slug_generator, sender=CourseInfo)