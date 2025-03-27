from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.urls import reverse

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

pre_save.connect(course_slug_generator, sender=CourseInfo)