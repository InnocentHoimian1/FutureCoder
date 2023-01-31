from django.contrib import admin
from .models import Lesson, Quiz, Profilis

class QuizInline(admin.TabularInline):
    model = Quiz
    readonly_fields = ('id',)
    can_delete = True
    extra = 0


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'position')
    inlines = [QuizInline]

class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'question', 'correct_option')


admin.site.register(Lesson, LessonAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Profilis)
# Register your models here.
