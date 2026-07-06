from django.contrib import admin

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


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 0
    fields = ["title", "slug", "lesson_step", "difficulty", "status", "source_hint"]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ["title", "slug", "reading_order", "source_file", "source_symbol"]


class ProjectInline(admin.TabularInline):
    model = MiniProject
    extra = 0
    fields = ["title", "slug", "reading_order", "source_file", "source_symbol"]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "slug",
        "source_file",
        "reading_order",
        "progress_percent",
    ]
    list_editable = ["reading_order"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "source_file", "source_symbol"]
    inlines = [LessonInline, ProjectInline, ExerciseInline]


class LessonStepInline(admin.TabularInline):
    model = LessonStep
    extra = 0
    fields = ["title", "slug", "order", "source_file", "source_symbol"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "reading_order", "source_file"]
    list_filter = ["topic"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "summary", "explanation", "source_file"]
    inlines = [LessonStepInline]


@admin.register(LessonStep)
class LessonStepAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "order", "source_file"]
    list_filter = ["lesson__topic", "lesson"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "body", "action", "checkpoint", "source_file"]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "lesson_step", "difficulty", "status", "updated_at"]
    list_filter = ["topic", "difficulty", "status"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "prompt", "source_hint"]


@admin.register(LearningLog)
class LearningLogAdmin(admin.ModelAdmin):
    list_display = ["exercise", "user", "minutes", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["exercise__title", "note"]


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0
    fields = ["title", "slug", "order", "source_hint", "next_action"]


@admin.register(MiniProject)
class MiniProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "slug", "reading_order", "source_file"]
    list_filter = ["topic"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "summary", "objective", "source_file"]
    inlines = [ProjectTaskInline]


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "order", "source_hint"]
    list_filter = ["project"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "prompt", "source_hint", "next_action"]


@admin.register(StepProgress)
class StepProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "step", "completed", "updated_at"]
    list_filter = ["completed", "updated_at"]
    search_fields = ["user__username", "step__title"]


@admin.register(ExerciseProgress)
class ExerciseProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "exercise", "status", "updated_at"]
    list_filter = ["status", "updated_at"]
    search_fields = ["user__username", "exercise__title"]


@admin.register(ProjectTaskProgress)
class ProjectTaskProgressAdmin(admin.ModelAdmin):
    list_display = ["user", "task", "completed", "updated_at"]
    list_filter = ["completed", "updated_at"]
    search_fields = ["user__username", "task__title"]
