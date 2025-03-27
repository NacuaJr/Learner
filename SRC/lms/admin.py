from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import TrainerRegistration, CourseInfo, CourseDetails

# Add this inline class definition
class TrainerRegistrationInline(admin.StackedInline):
    model = TrainerRegistration
    can_delete = False
    verbose_name_plural = 'Trainer Registration'
    fk_name = 'user'
    extra = 0  # No extra blank forms

@admin.register(TrainerRegistration)
class TrainerRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')

class CustomUserAdmin(UserAdmin):
    inlines = (TrainerRegistrationInline,)  # Now properly defined
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_trainer', 'is_approved_trainer')
    list_select_related = ('trainerregistration',)
    
    def is_trainer(self, instance):
        return instance.is_staff
    is_trainer.boolean = True
    
    def is_approved_trainer(self, instance):
        if hasattr(instance, 'trainerregistration'):
            return instance.trainerregistration.status
        return False
    is_approved_trainer.boolean = True

class CourseDetailsInline(admin.StackedInline):
    model = CourseDetails
    extra = 1

class CourseInfoAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'user', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('course_name', 'user__username')
    inlines = [CourseDetailsInline]

# Unregister the default User admin and register our custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(CourseInfo, CourseInfoAdmin)