from django.contrib import admin
from .models import Lesson, Quiz, Profilis, Progress, CourseEnrollment

class QuizInline(admin.TabularInline):
    model = Quiz
    readonly_fields = ('id',)
    can_delete = True
    extra = 0


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'position')
    inlines = [QuizInline]

class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'title')




admin.site.register(Lesson, LessonAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Profilis)
admin.site.register(Progress)
admin.site.register(CourseEnrollment)
# Register your models here.
