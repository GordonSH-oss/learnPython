from django.db import models
from django.conf import settings
from django.urls import reverse


class Topic(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    source_file = models.CharField(max_length=220)
    source_symbol = models.CharField(max_length=120, blank=True)
    summary = models.TextField()
    reading_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["reading_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("learning:topic-detail", kwargs={"slug": self.slug})

    @property
    def total_exercises(self):
        return self.exercises.count()

    @property
    def completed_exercises(self):
        return self.exercises.filter(status=Exercise.Status.DONE).count()

    @property
    def progress_percent(self):
        total = self.total_exercises
        if total == 0:
            return 0
        return round(self.completed_exercises / total * 100)

    def progress_percent_for(self, user):
        if not getattr(user, "is_authenticated", False):
            return 0
        total_steps = LessonStep.objects.filter(lesson__topic=self).count()
        total_tasks = ProjectTask.objects.filter(project__topic=self).count()
        total = total_steps + total_tasks
        if total == 0:
            return 0
        completed_steps = StepProgress.objects.filter(
            user=user,
            step__lesson__topic=self,
            completed=True,
        ).count()
        completed_tasks = ProjectTaskProgress.objects.filter(
            user=user,
            task__project__topic=self,
            completed=True,
        ).count()
        return round((completed_steps + completed_tasks) / total * 100)


class Lesson(models.Model):
    topic = models.ForeignKey(Topic, related_name="lessons", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=160)
    summary = models.TextField()
    explanation = models.TextField()
    source_file = models.CharField(max_length=220)
    source_symbol = models.CharField(max_length=120, blank=True)
    reading_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["topic__reading_order", "reading_order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["topic", "slug"],
                name="unique_lesson_slug_per_topic",
            )
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "learning:lesson-detail",
            kwargs={"topic_slug": self.topic.slug, "slug": self.slug},
        )

    def progress_percent_for(self, user):
        if not getattr(user, "is_authenticated", False):
            return 0
        total = self.steps.count()
        if total == 0:
            return 0
        completed = StepProgress.objects.filter(
            user=user,
            step__lesson=self,
            completed=True,
        ).count()
        return round(completed / total * 100)


class LessonStep(models.Model):
    lesson = models.ForeignKey(Lesson, related_name="steps", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=160)
    body = models.TextField()
    action = models.TextField()
    checkpoint = models.TextField()
    source_file = models.CharField(max_length=220)
    source_symbol = models.CharField(max_length=120, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["lesson__reading_order", "order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "slug"],
                name="unique_step_slug_per_lesson",
            )
        ]

    def __str__(self):
        return self.title


class Exercise(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    class Status(models.TextChoices):
        TODO = "todo", "Todo"
        DOING = "doing", "Doing"
        DONE = "done", "Done"

    topic = models.ForeignKey(Topic, related_name="exercises", on_delete=models.CASCADE)
    lesson_step = models.ForeignKey(
        LessonStep,
        related_name="exercises",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=160)
    prompt = models.TextField()
    source_hint = models.CharField(max_length=220, blank=True)
    difficulty = models.CharField(
        max_length=12,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.TODO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["topic__reading_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["topic", "slug"],
                name="unique_exercise_slug_per_topic",
            )
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "learning:exercise-detail",
            kwargs={"topic_slug": self.topic.slug, "slug": self.slug},
        )


class LearningLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="learning_logs",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    exercise = models.ForeignKey(
        Exercise,
        related_name="logs",
        on_delete=models.CASCADE,
    )
    note = models.TextField()
    minutes = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.exercise} - {self.minutes} min"


class ExerciseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(
        Exercise,
        related_name="user_progress",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=12,
        choices=Exercise.Status.choices,
        default=Exercise.Status.TODO,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "exercise"],
                name="unique_exercise_progress_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.exercise} - {self.status}"


class StepProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    step = models.ForeignKey(
        LessonStep,
        related_name="user_progress",
        on_delete=models.CASCADE,
    )
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "step"],
                name="unique_step_progress_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.step} - {self.completed}"


class MiniProject(models.Model):
    topic = models.ForeignKey(
        Topic,
        related_name="projects",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    summary = models.TextField()
    objective = models.TextField()
    source_file = models.CharField(max_length=220)
    source_symbol = models.CharField(max_length=120, blank=True)
    reading_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["reading_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("learning:project-detail", kwargs={"slug": self.slug})

    def progress_percent_for(self, user):
        if not getattr(user, "is_authenticated", False):
            return 0
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = ProjectTaskProgress.objects.filter(
            user=user,
            task__project=self,
            completed=True,
        ).count()
        return round(completed / total * 100)


class ProjectTask(models.Model):
    project = models.ForeignKey(
        MiniProject,
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=160)
    prompt = models.TextField()
    source_hint = models.CharField(max_length=220, blank=True)
    next_action = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["project__reading_order", "order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "slug"],
                name="unique_task_slug_per_project",
            )
        ]

    def __str__(self):
        return self.title


class ProjectTaskProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(
        ProjectTask,
        related_name="user_progress",
        on_delete=models.CASCADE,
    )
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "task"],
                name="unique_project_task_progress_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.task} - {self.completed}"
