from django.core.management.base import BaseCommand

from learning.curriculum import CURRICULUM, MINI_PROJECTS
from learning.models import Exercise, Lesson, LessonStep, MiniProject, ProjectTask, Topic


class Command(BaseCommand):
    help = "Seed Django source-learning topics and exercises."

    def handle(self, *args, **options):
        topic_count = 0
        lesson_count = 0
        step_count = 0
        exercise_count = 0
        project_count = 0
        task_count = 0

        for topic_data in CURRICULUM:
            lessons = topic_data["lessons"]
            topic_defaults = {
                key: value for key, value in topic_data.items() if key != "lessons"
            }
            topic, _ = Topic.objects.update_or_create(
                slug=topic_data["slug"],
                defaults=topic_defaults,
            )
            topic_count += 1

            for lesson_data in lessons:
                steps = lesson_data["steps"]
                lesson_defaults = {
                    key: value for key, value in lesson_data.items() if key != "steps"
                }
                lesson, _ = Lesson.objects.update_or_create(
                    topic=topic,
                    slug=lesson_data["slug"],
                    defaults=lesson_defaults,
                )
                lesson_count += 1

                for step_data in steps:
                    exercises = step_data["exercises"]
                    step_defaults = {
                        key: value
                        for key, value in step_data.items()
                        if key != "exercises"
                    }
                    step, _ = LessonStep.objects.update_or_create(
                        lesson=lesson,
                        slug=step_data["slug"],
                        defaults=step_defaults,
                    )
                    step_count += 1

                    for exercise_data in exercises:
                        Exercise.objects.update_or_create(
                            topic=topic,
                            slug=exercise_data["slug"],
                            defaults={**exercise_data, "lesson_step": step},
                        )
                        exercise_count += 1

        for project_data in MINI_PROJECTS:
            tasks = project_data["tasks"]
            topic = Topic.objects.get(slug=project_data["topic_slug"])
            project_defaults = {
                key: value
                for key, value in project_data.items()
                if key not in {"tasks", "topic_slug"}
            }
            project, _ = MiniProject.objects.update_or_create(
                slug=project_data["slug"],
                defaults={**project_defaults, "topic": topic},
            )
            project_count += 1

            for task_data in tasks:
                ProjectTask.objects.update_or_create(
                    project=project,
                    slug=task_data["slug"],
                    defaults=task_data,
                )
                task_count += 1

        if options.get("verbosity", 1) > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Seeded "
                    f"{topic_count} topics, {lesson_count} lessons, "
                    f"{step_count} steps, {exercise_count} exercises, "
                    f"{project_count} projects, and {task_count} tasks."
                )
            )
