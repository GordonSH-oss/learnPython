from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = "learning"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("accounts/login/", views.SourceLensLoginView.as_view(), name="login"),
    path(
        "accounts/logout/",
        LogoutView.as_view(next_page="learning:dashboard"),
        name="logout",
    ),
    path("accounts/register/", views.register, name="register"),
    path("progress/", views.progress_dashboard, name="progress"),
    path("request-echo/", views.request_echo, name="request-echo"),
    path("topics/<slug:slug>/", views.TopicDetailView.as_view(), name="topic-detail"),
    path(
        "topics/<slug:topic_slug>/lessons/<slug:slug>/",
        views.lesson_detail,
        name="lesson-detail",
    ),
    path(
        "topics/<slug:topic_slug>/exercises/<slug:slug>/",
        views.exercise_detail,
        name="exercise-detail",
    ),
    path("projects/<slug:slug>/", views.project_detail, name="project-detail"),
    path("steps/<int:pk>/toggle/", views.toggle_step, name="toggle-step"),
    path(
        "exercises/<int:pk>/progress/",
        views.set_exercise_progress,
        name="set-exercise-progress",
    ),
    path(
        "project-tasks/<int:pk>/toggle/",
        views.toggle_project_task,
        name="toggle-project-task",
    ),
]
