from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .models import CourseEnrollment

from .forms import UserUpdateForm, ProfilisUpdateForm
from .models import Lesson, Quiz, Progress
from django.db.models import Q

class IndexView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num_lesson = Lesson.objects.count()
        num_quiz = Quiz.objects.count()
        num_visits = self.request.session.get('num_visits', 1)
        self.request.session['num_visits'] = num_visits + 1
        context.update({
            'num_lesson': num_lesson,
            'num_quiz': num_quiz,
            'num_visits': num_visits,
        })
        return context

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Lesson, pk=request.POST.get('course_id'))
        quiz = get_object_or_404(Quiz, pk=request.POST.get('quiz_id'))
        user = request.user
        now = timezone.now()

        # Check if user has already enrolled in the course
        if CourseEnrollment.objects.filter(user=user, course=course).exists():
            messages.error(request, "You have already enrolled in this course.")
            return redirect('index')

        # Check if user has already enrolled in the quiz
        if CourseEnrollment.objects.filter(user=user, quiz=quiz).exists():
            messages.error(request, "You have already enrolled in this quiz.")
            return redirect('index')

        # Create course enrollment
        CourseEnrollment.objects.create(user=user, course=course, quiz=quiz, date_enrolled=now)
        messages.success(request, "You have successfully enrolled in the course and quiz.")
        return redirect('index')



class LessonListView(generic.ListView):
    model = Lesson
    paginate_by = 2
    template_name = 'lesson_list.html'
    context_object_name = 'lessons'

class LessonDetailView(generic.DetailView):
    model = Lesson
    paginate_by = 2
    template_name = 'lesson_detail.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        course_enrollment = CourseEnrollment.objects.get(user=self.request.user, course=self.object)
        Progress.objects.create(user=self.request.user, course=self.object, percentage=100)
        course_enrollment.completed = True
        course_enrollment.save()
        messages.info(request, "Lesson Completed")
        return redirect("lesson_list")


class QuizListView(generic.ListView):
    model = Quiz
    template_name = 'quiz_list.html'
    context_object_name = 'quizzes'

class QuizDetailView(generic.DetailView):
    model = Quiz
    template_name = 'quiz_detail.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        course_enrollment = CourseEnrollment.objects.get(user=self.request.user, course=self.object.lesson)
        Progress.objects.create(user=self.request.user, course=self.object.lesson, percentage=100)
        course_enrollment.completed = True
        course_enrollment.save()
        messages.info(request, "Quiz Completed")
        return redirect("quiz_list")

def search(request):
    """
paprasta paieška. query ima informaciją iš paieškos laukelio,
search_results prafiltruoja pagal įvestą tekstą knygų pavadinimus ir aprašymus.
Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės didžiosios/mažosios.
"""
    query = request.GET.get("query")
    lessons = Lesson.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, "search.html", {"lessons": lessons, "query": query})

@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimam reikšmes iš registracijos formos laukų
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password"]
        password2 = request.POST["password2"]
        # ar sutampa įvesti passwordai
        if password1 == password2:
            # ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, f"User name {username} already exist!")
                return redirect("register")
            else:
                # ar nėra tokio pačio email
                if User.objects.filter(email=email).exists():
                    messages.error(request, f"Email {email} is already used by another user")
                    return redirect("register")
                else:
                    # taškas kai viskas tvarkoje, patikrinimai praeiti, kuriam naują userį
                    User.objects.create_user(username=username, email=email, password=password1)
                    messages.info(request, f"User {username} succesfully registered")
                    return redirect("login")
        else:
            messages.error(request, "Password does not match")
            return redirect("register")
    return render(request, "register.html")


@login_required
def profilis(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfilisUpdateForm(request.POST, request.FILES, instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.info(request, "Profile successfully updated")
            return redirect("profilis")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfilisUpdateForm(instance=request.user.profilis)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, "profile.html", context=context)
def enroll(request, course_id):
    course = get_object_or_404(Lesson, pk=course_id)
    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, "You are already enrolled in this course.")
        return redirect("lesson_list")
    else:
        CourseEnrollment.objects.create(user=request.user, course=course)
        messages.info(request, "You are now enrolled in this course.")
        return redirect("lesson_list")
class EnrolledCoursesListView(ListView):
    model = CourseEnrollment
    template_name = 'enrolled_courses.html'
    context_object_name = 'enrolled_courses'

    def get_queryset(self):
        return CourseEnrollment.objects.filter(user=self.request.user)

    def start_lesson(request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        progress, created = Progress.objects.get_or_create(user=request.user, lesson=lesson)
        if created:
            progress.start_time = timezone.now()
            progress.save()
        return render(request, 'lesson_detail.html', {'lesson': lesson})

    def complete_lesson(request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        progress, created = Progress.objects.get_or_create(user=request.user, lesson=lesson)
        progress.end_time = timezone.now()
        progress.save()
        return redirect('lessons')

def add_lesson(request):
    if request.method == 'POST':
        # Process form submission
        title = request.POST['title']
        description = request.POST['description']
        author = request.POST['author']
        image = request.FILES.get('image')

        lesson = Lesson.objects.create(
            title=title,
            description=description,
            author=author,
            image=image
        )
        return redirect('lesson_detail', lesson.id)
    else:
        # Render form template
        return render(request, 'add_lesson.html')

def course_progress(request):
    lessons = Lesson.objects.all()
    if not lessons:
        return render(request, 'user_progress.html', {'message': 'No lessons available'})
    progress = Progress.objects.filter(user=request.user)
    completed_lessons = [p.lesson for p in progress]
    quizzes = Quiz.objects.filter(lesson__in=completed_lessons)
    if not quizzes:
        return render(request, 'user_progress.html', {'message': 'No quizzes available'})
    completed_quizzes = [p.completed_quizzes.all() for p in progress]
    enrolled_courses = CourseEnrollment.objects.filter(user=request.user)
    completed_percentage = 0
    if lessons:
        completed_percentage = (len(completed_lessons) / len(lessons)) * 100
        completed_percentage = round(completed_percentage)

    return render(request, 'user_progress.html', {
        'lessons': lessons,
        'quizzes': quizzes,
        'completed_lessons': completed_lessons,
        'completed_quizzes': completed_quizzes,
        'completed_percentage': completed_percentage,
        'enrolled_courses': enrolled_courses
    })





# Create your views here.
