from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView

from .forms import ExerciseStatusForm, LearningLogForm, RegisterForm
from .models import (
    Exercise,
    ExerciseProgress,
    LearningLog,
    Lesson,
    LessonStep,
    MiniProject,
    ProjectTask,
    ProjectTaskProgress,
    StepProgress,
    Topic,
)


class SourceLensLoginView(LoginView):
    template_name = "registration/login.html"


def register(request):
    if request.user.is_authenticated:
        return redirect("learning:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "账号已创建，学习进度会从现在开始记录。")
        return redirect("learning:dashboard")
    return render(request, "registration/register.html", {"form": form})


def _topic_cards(topics, user):
    return [
        {
            "topic": topic,
            "progress": topic.progress_percent_for(user),
            "lesson_count": topic.lessons.count(),
            "project_count": topic.projects.count(),
        }
        for topic in topics
    ]


def _project_cards(projects, user):
    return [
        {
            "project": project,
            "progress": project.progress_percent_for(user),
            "task_count": project.tasks.count(),
        }
        for project in projects
    ]


def dashboard(request):
    topics = Topic.objects.prefetch_related("lessons__steps", "projects__tasks")
    projects = MiniProject.objects.select_related("topic").prefetch_related("tasks")
    total_steps = LessonStep.objects.count()
    completed_steps = (
        StepProgress.objects.filter(user=request.user, completed=True).count()
        if request.user.is_authenticated
        else 0
    )
    context = {
        "topic_cards": _topic_cards(topics, request.user),
        "project_cards": _project_cards(projects, request.user),
        "total_steps": total_steps,
        "done_steps": completed_steps,
        "request_snapshot": {
            "method": request.method,
            "path": request.path,
            "query_string": request.META.get("QUERY_STRING", ""),
            "middleware_seen": getattr(request, "source_lens_middleware_seen", False),
        },
    }
    return render(request, "learning/dashboard.html", context)


class TopicDetailView(DetailView):
    model = Topic
    template_name = "learning/topic_detail.html"
    context_object_name = "topic"

    def get_queryset(self):
        return Topic.objects.prefetch_related("lessons__steps", "projects__tasks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = self.object
        context["progress"] = topic.progress_percent_for(self.request.user)
        context["lesson_cards"] = [
            {
                "lesson": lesson,
                "progress": lesson.progress_percent_for(self.request.user),
                "step_count": lesson.steps.count(),
            }
            for lesson in topic.lessons.all()
        ]
        context["project_cards"] = _project_cards(topic.projects.all(), self.request.user)
        return context


def lesson_detail(request, topic_slug, slug):
    lesson = get_object_or_404(
        Lesson.objects.select_related("topic").prefetch_related(
            Prefetch(
                "steps",
                queryset=LessonStep.objects.prefetch_related("exercises"),
            )
        ),
        topic__slug=topic_slug,
        slug=slug,
    )
    completed_step_ids = set()
    exercise_progress = {}
    if request.user.is_authenticated:
        completed_step_ids = set(
            StepProgress.objects.filter(
                user=request.user,
                step__lesson=lesson,
                completed=True,
            ).values_list("step_id", flat=True)
        )
        exercise_progress = {
            progress.exercise_id: progress
            for progress in ExerciseProgress.objects.filter(
                user=request.user,
                exercise__lesson_step__lesson=lesson,
            )
        }
    for step in lesson.steps.all():
        for exercise in step.exercises.all():
            progress = exercise_progress.get(exercise.id)
            exercise.user_status = progress.status if progress else Exercise.Status.TODO

    return render(
        request,
        "learning/lesson_detail.html",
        {
            "lesson": lesson,
            "progress": lesson.progress_percent_for(request.user),
            "completed_step_ids": completed_step_ids,
            "exercise_progress": exercise_progress,
        },
    )


def exercise_detail(request, topic_slug, slug):
    exercise = get_object_or_404(
        Exercise.objects.select_related("topic", "lesson_step").prefetch_related("logs"),
        topic__slug=topic_slug,
        slug=slug,
    )
    progress = None
    if request.user.is_authenticated:
        progress, _ = ExerciseProgress.objects.get_or_create(
            user=request.user,
            exercise=exercise,
        )

    status_form = ExerciseStatusForm(instance=progress)
    log_form = LearningLogForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "请先登录，再记录练习进度。")
            return redirect(f"{reverse('learning:login')}?next={request.path}")
        action = request.POST.get("action")
        if action == "status":
            status_form = ExerciseStatusForm(request.POST, instance=progress)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, "练习状态已更新。")
                return redirect(exercise)
        elif action == "log":
            log_form = LearningLogForm(request.POST)
            if log_form.is_valid():
                log = log_form.save(commit=False)
                log.user = request.user
                log.exercise = exercise
                log.save()
                messages.success(request, "学习笔记已添加。")
                return redirect(exercise)
        else:
            messages.error(request, "未知表单动作。")

    if request.user.is_authenticated:
        logs = exercise.logs.filter(user=request.user).select_related("user")
    else:
        logs = exercise.logs.none()

    return render(
        request,
        "learning/exercise_detail.html",
        {
            "exercise": exercise,
            "progress": progress,
            "status_form": status_form,
            "log_form": log_form,
            "logs": logs,
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(
        MiniProject.objects.select_related("topic").prefetch_related("tasks"),
        slug=slug,
    )
    completed_task_ids = set()
    if request.user.is_authenticated:
        completed_task_ids = set(
            ProjectTaskProgress.objects.filter(
                user=request.user,
                task__project=project,
                completed=True,
            ).values_list("task_id", flat=True)
        )
    context = {
        "project": project,
        "progress": project.progress_percent_for(request.user),
        "completed_task_ids": completed_task_ids,
        "lab_payload": _lab_payload(project.slug, request),
    }
    return render(request, "learning/project_detail.html", context)


@login_required
def progress_dashboard(request):
    topics = Topic.objects.prefetch_related("lessons__steps", "projects__tasks")
    projects = MiniProject.objects.select_related("topic").prefetch_related("tasks")
    logs = LearningLog.objects.filter(user=request.user).select_related(
        "exercise",
        "exercise__topic",
    )[:10]
    return render(
        request,
        "learning/progress.html",
        {
            "topic_cards": _topic_cards(topics, request.user),
            "project_cards": _project_cards(projects, request.user),
            "logs": logs,
        },
    )


@login_required
@require_POST
def toggle_step(request, pk):
    step = get_object_or_404(LessonStep.objects.select_related("lesson", "lesson__topic"), pk=pk)
    progress, _ = StepProgress.objects.get_or_create(user=request.user, step=step)
    progress.completed = not progress.completed
    progress.save(update_fields=["completed", "updated_at"])
    return redirect(request.POST.get("next") or step.lesson.get_absolute_url())


@login_required
@require_POST
def set_exercise_progress(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    progress, _ = ExerciseProgress.objects.get_or_create(
        user=request.user,
        exercise=exercise,
    )
    form = ExerciseStatusForm(request.POST, instance=progress)
    if form.is_valid():
        form.save()
        messages.success(request, "练习状态已更新。")
    else:
        messages.error(request, "练习状态无效。")
    return redirect(request.POST.get("next") or exercise.get_absolute_url())


@login_required
@require_POST
def toggle_project_task(request, pk):
    task = get_object_or_404(ProjectTask.objects.select_related("project"), pk=pk)
    progress, _ = ProjectTaskProgress.objects.get_or_create(user=request.user, task=task)
    progress.completed = not progress.completed
    progress.save(update_fields=["completed", "updated_at"])
    return redirect(request.POST.get("next") or task.project.get_absolute_url())


def request_echo(request):
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() in {"accept", "host", "user-agent", "cookie"}
    }
    response = JsonResponse(
        {
            "method": request.method,
            "path": request.path,
            "full_path": request.get_full_path(),
            "query": {key: request.GET.getlist(key) for key in request.GET},
            "headers": headers,
            "cookies": request.COOKIES,
            "middleware_seen": getattr(request, "source_lens_middleware_seen", False),
        }
    )
    response.set_cookie("source_lens_seen", "1", samesite="Lax")
    return response


def _lab_payload(project_slug, request):
    if project_slug == "request-lab":
        return {
            "kind": "request",
            "method": request.method,
            "path": request.path,
            "query": {key: request.GET.getlist(key) for key in request.GET},
            "middleware_seen": getattr(request, "source_lens_middleware_seen", False),
        }
    if project_slug == "url-resolver-lab":
        return {
            "kind": "url",
            "dashboard": reverse("learning:dashboard"),
            "request_echo": reverse("learning:request-echo"),
            "sample_project": reverse(
                "learning:project-detail",
                kwargs={"slug": "url-resolver-lab"},
            ),
        }
    if project_slug == "orm-query-lab":
        qs = Exercise.objects.filter(topic__slug="orm-querysets")
        return {
            "kind": "orm",
            "exercise_count": qs.count(),
            "sql": str(qs.query),
        }
    return {"kind": "generic"}
