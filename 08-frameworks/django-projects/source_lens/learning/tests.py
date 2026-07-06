from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

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


class CurriculumSeedTests(TestCase):
    def test_seed_lessons_is_idempotent(self):
        call_command("seed_lessons", verbosity=0)
        first_counts = {
            "topics": Topic.objects.count(),
            "lessons": Lesson.objects.count(),
            "steps": LessonStep.objects.count(),
            "exercises": Exercise.objects.count(),
            "projects": MiniProject.objects.count(),
            "tasks": ProjectTask.objects.count(),
        }

        call_command("seed_lessons", verbosity=0)

        self.assertEqual(
            first_counts,
            {
                "topics": Topic.objects.count(),
                "lessons": Lesson.objects.count(),
                "steps": LessonStep.objects.count(),
                "exercises": Exercise.objects.count(),
                "projects": MiniProject.objects.count(),
                "tasks": ProjectTask.objects.count(),
            },
        )
        self.assertEqual(first_counts["projects"], 3)


class ProgressModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.topic = Topic.objects.create(
            slug="request-response",
            title="请求与响应链路",
            source_file="django/http/request.py",
            source_symbol="HttpRequest",
            summary="Connect request data to response output.",
            reading_order=1,
        )
        self.lesson = Lesson.objects.create(
            topic=self.topic,
            slug="request-object",
            title="HttpRequest 从哪里来",
            summary="Read request objects.",
            explanation="Request objects are created by handlers.",
            source_file="django/http/request.py",
            source_symbol="HttpRequest",
            reading_order=1,
        )
        self.step = LessonStep.objects.create(
            lesson=self.lesson,
            slug="inspect-request",
            title="Inspect request",
            body="Read request data.",
            action="Open request echo.",
            checkpoint="Explain QueryDict.",
            source_file="django/http/request.py",
            source_symbol="QueryDict",
            order=1,
        )
        self.project = MiniProject.objects.create(
            topic=self.topic,
            slug="request-lab",
            title="Request Lab",
            summary="Observe requests.",
            objective="Understand request data.",
            source_file="learning/views.py",
            source_symbol="request_echo",
            reading_order=1,
        )
        self.task = ProjectTask.objects.create(
            project=self.project,
            slug="querydict-observation",
            title="Observe QueryDict",
            prompt="Use duplicate query params.",
            source_hint="django/http/request.py:QueryDict",
            next_action="Open Request Echo.",
            order=1,
        )

    def test_step_progress_is_unique_per_user_and_step(self):
        StepProgress.objects.create(user=self.user, step=self.step, completed=True)

        with self.assertRaises(IntegrityError), transaction.atomic():
            StepProgress.objects.create(user=self.user, step=self.step, completed=False)

    def test_different_users_have_independent_progress(self):
        StepProgress.objects.create(user=self.user, step=self.step, completed=True)

        self.assertEqual(self.lesson.progress_percent_for(self.user), 100)
        self.assertEqual(self.lesson.progress_percent_for(self.other_user), 0)

    def test_topic_and_project_progress_for_user(self):
        StepProgress.objects.create(user=self.user, step=self.step, completed=True)
        ProjectTaskProgress.objects.create(
            user=self.user,
            task=self.task,
            completed=True,
        )

        self.assertEqual(self.topic.progress_percent_for(self.user), 100)
        self.assertEqual(self.project.progress_percent_for(self.user), 100)


class SourceLensViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_lessons", verbosity=0)
        cls.user = User.objects.create_user(username="learner", password="pass")

    def test_dashboard_topic_lesson_and_project_are_public(self):
        response = self.client.get(reverse("learning:dashboard"), {"chapter": "http"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "课程首页")
        self.assertEqual(response.headers["X-Source-Lens"], "middleware-ran")

        topic = Topic.objects.get(slug="request-response")
        response = self.client.get(topic.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "请求与响应链路")

        lesson = Lesson.objects.get(slug="request-object")
        response = self.client.get(lesson.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HttpRequest 从哪里来")

        project = MiniProject.objects.get(slug="request-lab")
        response = self.client.get(project.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Request Lab")

    def test_anonymous_user_cannot_submit_progress(self):
        step = LessonStep.objects.first()

        response = self.client.post(reverse("learning:toggle-step", args=[step.id]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("learning:login"), response["Location"])
        self.assertFalse(StepProgress.objects.exists())

    def test_logged_in_user_can_complete_step_and_project_task(self):
        self.client.force_login(self.user)
        step = LessonStep.objects.first()
        task = ProjectTask.objects.first()

        self.client.post(reverse("learning:toggle-step", args=[step.id]))
        self.client.post(reverse("learning:toggle-project-task", args=[task.id]))

        self.assertTrue(
            StepProgress.objects.get(user=self.user, step=step).completed
        )
        self.assertTrue(
            ProjectTaskProgress.objects.get(user=self.user, task=task).completed
        )

    def test_logged_in_user_can_update_exercise_and_add_log(self):
        self.client.force_login(self.user)
        exercise = Exercise.objects.get(slug="inspect-request-echo")

        response = self.client.post(
            reverse("learning:set-exercise-progress", args=[exercise.id]),
            {"status": Exercise.Status.DONE},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            ExerciseProgress.objects.get(user=self.user, exercise=exercise).status,
            Exercise.Status.DONE,
        )

        response = self.client.post(
            exercise.get_absolute_url(),
            {"action": "log", "note": "读了 QueryDict.getlist。", "minutes": 20},
        )
        self.assertRedirects(response, exercise.get_absolute_url())
        log = LearningLog.objects.get(user=self.user, exercise=exercise)
        self.assertEqual(log.minutes, 20)

    def test_labs_return_expected_payloads(self):
        request_echo = self.client.get(
            reverse("learning:request-echo"),
            {"chapter": ["http", "orm"]},
        )
        self.assertEqual(request_echo.status_code, 200)
        self.assertEqual(request_echo.json()["query"]["chapter"], ["http", "orm"])
        self.assertIn("source_lens_seen", request_echo.cookies)

        url_lab = self.client.get(
            reverse("learning:project-detail", kwargs={"slug": "url-resolver-lab"})
        )
        self.assertContains(url_lab, "sample_project")

        orm_lab = self.client.get(
            reverse("learning:project-detail", kwargs={"slug": "orm-query-lab"})
        )
        self.assertContains(orm_lab, "SELECT")
