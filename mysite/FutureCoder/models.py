from django.utils import timezone
from django.db import models
from PIL import Image
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.urls import reverse

class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = HTMLField(default="")
    video_url = models.URLField()
    presentation_id = models.CharField(max_length=255, default="")
    position = models.IntegerField()
    image = models.ImageField('Image', upload_to='courses/', null=True)

    class Meta:
        ordering = ['title']

    def display_lesson(self):
        return ', '.join(lesson.title for lesson in self.lesson.all()[:3])

    display_lesson.short_description = 'Lesson'

    def get_absolute_url(self):
        """Returns the url to access a particular lesson instance."""
        return reverse('course-detail', args=[str(self.pk)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.title} {self.description}'



class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    presentation_id = models.CharField(max_length=255, default="")
    position = models.IntegerField(default=5)
    title = models.CharField(max_length=255, default="")
    image = models.ImageField('Image', upload_to='courses/', null=True, default="")


    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title}"



class Profilis(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nuotrauka = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return f"{self.user} profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.nuotrauka.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.nuotrauka.path)


class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

class Progress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    completed_quizzes = models.ManyToManyField(Quiz, blank=True)

    LESSON_STATUS = (
        ('e', 'Editing'),
        ('s', 'Started'),
        ('f', 'Finished'),
    )
    status = models.CharField(
        max_length=1,
        choices=LESSON_STATUS,
        blank=True,
        default='e',
        help_text='Status',
    )


    class Meta:
        ordering = ['end_time']


    def __str__(self):
        return f'{self.lesson.title}'



# Create your models here.
