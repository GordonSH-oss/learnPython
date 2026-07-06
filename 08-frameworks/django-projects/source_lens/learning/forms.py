from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Exercise, ExerciseProgress, LearningLog


class ExerciseStatusForm(forms.ModelForm):
    class Meta:
        model = ExerciseProgress
        fields = ["status"]


class LearningLogForm(forms.ModelForm):
    class Meta:
        model = LearningLog
        fields = ["note", "minutes"]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 4}),
            "minutes": forms.NumberInput(attrs={"min": 1}),
        }


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
